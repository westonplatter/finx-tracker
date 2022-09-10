from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine

from .common import gen_db_url
from .import_trades import parse_date_series, parse_datetime_series

CLOSE_OUT_COLUMN = "co_trade_id"
CLOSE_OUT_COLUMN_VALUE = "trade_id"


def fetch_dates_sql():
    sql = """
    with x_times as (
        select
            count(*),
            date_time
        from trades_trade as t
        where date_time is not null
            -- and t.underlying_symbol = 'ESM2'
        group by date_time
        -- having count(*) >= 4
        order by date_time desc
    )

    select date_time
    from x_times
    order by date_time
    ;
    """
    return sql


def transform_set_strike(df):
    xdf = df[df.asset_category.isin(["OPT", "FOP"])]
    df.loc[xdf.index, "strike"] = xdf["description"].str.split(" ", expand=True)[2]
    return None


def _count_descriptions(descriptions: pd.Series):
    return descriptions.count()


def is_gs_a(grouped_df):
    descriptions_unique = _count_descriptions(grouped_df.description)

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call calendar at same strike
    # Front = Friday
    # Back = Monday
    return (
        descriptions_unique == 1 and dte_diff == -3 and front_date.weekday() == 4 and back_date.weekday() == 0
    )


def is_gs_b(grouped_df):
    descriptions_unique = _count_descriptions(grouped_df.description)

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call diagonal with 2 strike diff
    # Front = Friday
    # Back = Monday
    return (
        descriptions_unique == 3 and dte_diff == -3 and front_date.weekday() == 4 and back_date.weekday() == 0
    )


def is_roll(grouped_df):
    descriptions_unique = _count_descriptions(grouped_df.description)

    options_count = len(grouped_df)

    return descriptions_unique in [1, 2] and options_count == 2


def classify_strategy(grouped_df):
    if is_gs_a(grouped_df):
        return "gs_a"
    if is_gs_b(grouped_df):
        return "gs_b"
    if is_roll(grouped_df):
        return "roll"
    return "not automatically tagged"


def find_roll_id_for_conids_and_dt(xdf, conids, dt) -> pd.DataFrame:
    qdf = xdf.query("conid.isin(@conids)").query("date_time < @dt").query(f"{CLOSE_OUT_COLUMN} == 0")
    return qdf.head(1)


def run():
    engine = create_engine(gen_db_url())
    sql = fetch_dates_sql()

    with engine.connect() as con:
        dates_df = pd.read_sql_query(sql, con=con).reset_index()

        sql = """
            select * from trades_trade
        """
        trades_df = pd.read_sql_query(sql, con=con)

        df = pd.merge(trades_df, dates_df, on="date_time")
        df.drop(columns=["index"], inplace=True)

        df.date_time = pd.to_datetime(df.date_time)
        df.expiry = pd.to_datetime(df.expiry)

    transform_set_strike(df)

    import pytz

    x = datetime(2022, 1, 1, tzinfo=pytz.utc)
    df = df.query("@x <= date_time")

    df["strategy"] = None
    df.sort_values(["date_time"], ascending=True)

    for k, grouped in df.groupby([df.date_time]):
        strategy_key = classify_strategy(grouped)
        df.loc[grouped.index, "strategy"] = strategy_key
        df.loc[grouped.index, "front"] = grouped.expiry.min()

    rolls_df = (df.query("strategy == 'roll'")).copy()

    rolls_df["roll_id"] = 0
    rolls_df[CLOSE_OUT_COLUMN] = 0

    def gen_msg(xdf, cols):
        msg = []
        for _, row in xdf.iterrows():
            values = [f"{row[col]}" for col in cols]
            msg.append(" ".join(values))
        return ", ".join(msg)

    # for k, g in rolls_df.groupby(["date_time"]):
    #     if len(g.description.unique()) == 1:
    #         continue

    #     opened = g.query("open_close_indicator == 'O'")
    #     closed = g.query("open_close_indicator == 'C'")

    #     columns = ["quantity", "description"]
    #     m1 = "O = " + gen_msg(opened, columns)
    #     m2 = "C = " + gen_msg(closed, columns)
    #     msg = [m1, m2]

    #     open_close_set = set(g.open_close_indicator.unique())

    #     if set(["O"]) == open_close_set:
    #         roll_id = rolls_df["roll_id"].max() + 1
    #         rolls_df.loc[g.index, "roll_id"] = roll_id
    #         print("Open   ", msg, roll_id)

    #     if set(["C", "O"]) == open_close_set:
    #         conids, dt = closed.conid.values, g.date_time.values[0]
    #         parent_df = find_roll_id_for_conids_and_dt(rolls_df, conids, dt)
    #         rolls_df.loc[parent_df.index, CLOSE_OUT_COLUMN] = closed[
    #             CLOSE_OUT_COLUMN_VALUE
    #         ].values[0]
    #         roll_ids = parent_df["roll_id"].values
    #         if len(roll_ids) == 0:
    #             roll_id = rolls_df["roll_id"].max() + 1
    #         else:
    #             roll_ids[0]

    #         rolls_df.loc[g.index, "roll_id"] = roll_id
    #         print("Roll   ", msg, " ", roll_id)

    #     if set(["C"]) == open_close_set:
    #         conids, dt = closed.conid.values, g.date_time.values[0]
    #         parent_df = find_roll_id_for_conids_and_dt(rolls_df, conids, dt)
    #         try:
    #             parent_conid = parent_df.conid.values[0]
    #             roll_id = parent_df["roll_id"].values[0]
    #             closed_closing_order_id = closed.query("conid == @parent_conid")[
    #                 CLOSE_OUT_COLUMN_VALUE
    #             ].values[0]
    #             rolls_df.loc[parent_df.index, CLOSE_OUT_COLUMN] = closed_closing_order_id
    #             rolls_df.loc[g.index, "roll_id"] = roll_id
    #             print("Close  ", msg, roll_id)
    #         except:
    #             print('Help on row', g)

    for k, grouped in df.groupby([df.date_time]):
        strategy_key = classify_strategy(grouped)
        df.loc[grouped.index, "strategy"] = strategy_key
        df.loc[grouped.index, "front"] = grouped.expiry.min()

        print("-------------------")
        print(grouped.description)
        cat = grouped.asset_category.unique()
        print(strategy_key)

        underlying = list(set([x.split(" ")[0] for x in grouped.description.values]))

        if cat == ["FOP"] and underlying == "CL":
            suggestion = "roll_cl"
        else:
            suggestion = "None"

        print(suggestion)

        # val = input("Enter your value: ")
        # print(val)

        # import pdb; pdb.set_trace()
