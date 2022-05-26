from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine

from .common import gen_db_url
from .import_trades import parse_date_series, parse_datetime_series
from finx_tracker.portfolios.models import StrategyTrade

CLOSE_OUT_COLUMN = "co_trade_id"
CLOSE_OUT_COLUMN_VALUE = "trade_id"


def fetch_gs_dates_sql():
    sql = """
    with x_times as (
        select
            count(*),
            date_time
        from trades_trade as t
        where date_time is not null
            and t.underlying_symbol = 'ESM2'
        group by date_time
            having count(*) >= 4
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
    strikes_count = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call calendar at same strike
    # Front = Friday
    # Back = Monday
    return (
        strikes_count == 1
        and dte_diff == -3
        and front_date.weekday() == 4
        and back_date.weekday() == 0
    )


def is_gs_b(grouped_df):
    strikes_count = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    print(strikes_count, dte_diff, front_date.weekday(), back_date.weekday())

    # short put/call diagonal with 2 strike diff
    # Front = Friday
    # Back = Monday
    return (
        strikes_count == 3
        and dte_diff == -3
        and front_date.weekday() == 4
        and back_date.weekday() == 0
    )


def classify_strategy(grouped_df):
    if is_gs_a(grouped_df):
        return "gs_a"
    if is_gs_b(grouped_df):
        return "gs_b"
    return "not automatically tagged"


def find_roll_id_for_conids_and_dt(xdf, conids, dt) -> pd.DataFrame:
    qdf = (
        xdf.query("conid.isin(@conids)")
        .query("date_time < @dt")
        .query(f"{CLOSE_OUT_COLUMN} == 0")
    )
    return qdf.head(1)


def run():
    engine = create_engine(gen_db_url())
    sql = fetch_gs_dates_sql()

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
    df["strategy"] = None
    df.sort_values(["date_time"], ascending=True)

    for k, grouped in df.groupby([df.date_time]):
        strategy_key = classify_strategy(grouped)
        df.loc[grouped.index, "strategy"] = strategy_key
        df.loc[grouped.index, "front"] = grouped.expiry.min()

    for idx, row in df.iterrows():
        trade_id = row.trade_id
        st = StrategyTrade.objects.filter(ext_trade_id=trade_id).first()

        if st is None:
            st = StrategyTrade(ext_trade_id=row.trade_id, group_name=row.front)
            if row.strategy == "gs_a":
                st.strategy_id = 1
            if row.strategy == "gs_b":
                st.strategy_id = 2
            st.save()

    # select t.trade_id, st.id
    # from trades_trade as t
    # left outer join portfolios_strategy_trade as st on st.ext_trade_id = t.trade_id

    tdf = df.pivot_table(
        values=["fifo_pnl_realized"],
        index=["front"],
        columns=["strategy"],
        aggfunc=["count", "sum"])

    print(tdf)

    tdf.to_csv("gs.csv")
