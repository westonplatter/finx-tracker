from os import environ
from typing import List, Optional

import pandas as pd
from sqlalchemy import create_engine

from .common import gen_db_url

CLOSE_OUT_COLUMN = "co_trade_id"
CLOSE_OUT_COLUMN_VALUE = "trade_id"


def gen_sql_combo_trade_datetimes(account_ids: Optional[List[str]]):
    account_ids_sql = ""

    if account_ids is not None and len(account_ids) > 1:
        if len(account_ids) > 2:
            account_ids_sql = f" AND account_id IN ({tuple(account_ids)})"
        else:
            account_ids_sql = f" AND account_id = '{account_ids[0]}'"

    sql = f"""
    with x_times as (
        select
            count(*),
            date_time
        from trades_trade as t
        where
            date_time is not null
            {account_ids_sql}
        group by date_time
        having count(*) > 1
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


def is_gs_a(grouped_df):
    options_count = len(grouped_df.description.unique())
    strikes_count = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call calendar at same strike
    # Front = Friday
    # Back = Monday
    return (
        options_count == 4
        and strikes_count == 1
        and dte_diff == -3
        and front_date.weekday() == 4
        and back_date.weekday() == 0
    )


def is_gs_b(grouped_df):
    options_count = len(grouped_df.description.unique())
    strikes_count = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call diagonal with 2 strike diff
    # Front = Friday
    # Back = Monday
    return (
        options_count == 4
        and strikes_count == 3
        and dte_diff == -3
        and front_date.weekday() == 4
        and back_date.weekday() == 0
    )


def is_gs_v2(grouped_df):
    options_count = len(grouped_df.description.unique())
    strikes_count = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call calendar at same strike
    # Front = Friday
    # Back = Monday
    return (
        options_count == 2
        and strikes_count == 1
        and dte_diff == -3
        and front_date.weekday() == 4
        and back_date.weekday() == 0
    )


def is_gs_v3(grouped_df):
    options_count = len(grouped_df.description.unique())
    strikes_count = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call calendar at same strike
    # Front = Friday
    # Back = Monday
    return (
        options_count == 2
        and strikes_count == 1
        and dte_diff == -4
        and front_date.weekday() == 0
        and back_date.weekday() == 4
    )


def classify_strategy(grouped_df):
    if is_gs_a(grouped_df):
        return "gs_a"
    if is_gs_b(grouped_df):
        return "gs_b"
    if is_gs_v2(grouped_df):
        return "gs_v2"
    if is_gs_v3(grouped_df):
        return "gs_v3"
    return "not automatically tagged"


def is_rolling_trade(df: pd.DataFrame) -> bool:
    return ("O" in df["open_close_indicator"].values) and ("C" in df["open_close_indicator"].values)


def find_roll_id_for_conids_and_dt(df: pd.DataFrame, conids: List, dt: pd.Timestamp) -> pd.DataFrame:
    df = (
        df.query("conid.isin(@conids)")
        .query("date_time < @dt")
        .query("open_close_indicator == ")
        .query(f"{CLOSE_OUT_COLUMN} == 0")
    )
    return df.head(1)


def find_opening_trade_fifo(opening_trades, conid, dt) -> pd.DataFrame:
    return opening_trades[
        (opening_trades["conid"] == conid)
        & (opening_trades.date_time < dt)
        & (opening_trades[CLOSE_OUT_COLUMN] == 0)
    ].head(1)


def get_strategy_id_for_strategy(engine, strategy_key: str, account_id: str) -> int:
    query = f"""
        select ps.id
        from portfolios_strategy as ps
        join portfolios_portfolio as pp on pp.id = ps.portfolio_id
        where
            ps.name = '{strategy_key}'
            and pp.account_id = '{account_id}'
    """
    return pd.read_sql(query, engine).id.iloc[0]


def run():
    engine = create_engine(gen_db_url())

    # hack to get account ids without exposing in code
    account_ids = environ.get("ACCOUNT_IDS", None)
    if account_ids is not None:
        account_ids = [x for x in account_ids.split(",")]

    with engine.connect() as con:
        # get dates
        query = gen_sql_combo_trade_datetimes(account_ids=account_ids)
        datetimes_df = pd.read_sql_query(query, con=con).reset_index()

        # get trades
        if len(account_ids) > 0:
            account_ids_predicate = (
                f"account_id IN {tuple(account_ids)}"
                if len(account_ids) > 1
                else f"account_id = '{account_ids[0]}'"
            )
            query = f"select * from trades_trade where {account_ids_predicate}"
        else:
            query = "select * from trades_trade"

        trades_df = pd.read_sql_query(query, con=con)

        df = pd.merge(trades_df, datetimes_df, on="date_time", how="inner")
        df.drop(columns=["index"], inplace=True)

        df.date_time = pd.to_datetime(df.date_time)
        df.expiry = pd.to_datetime(df.expiry)

    # transforms
    transform_set_strike(df)
    df["strategy"] = None
    df.sort_values(["date_time"], ascending=True)
    df[CLOSE_OUT_COLUMN] = 0

    opening_trades = df.query('open_close_indicator == "O"')

    for ix, row in df.iterrows():
        # only closing trades
        if row.open_close_indicator == "O":
            continue
        single_opening_trade = find_opening_trade_fifo(opening_trades, row.conid, row.date_time)
        if len(single_opening_trade.index) >= 1:
            if len(single_opening_trade.index) > 1:
                import pdb

                pdb.set_trace()
            else:
                co_trade_id = single_opening_trade["trade_id"].values[0]
                df.loc[ix, CLOSE_OUT_COLUMN] = co_trade_id

        # strategy_key = classify_strategy(grouped)
        # df.loc[grouped.index, "strategy"] = strategy_key
        # df.loc[grouped.index, "front"] = grouped.expiry.min()

    import pdb

    pdb.set_trace()

    # for _, row in df.iterrows():
    #     trade_id = row.trade_id
    #     st = StrategyTrade.objects.filter(ext_trade_id=trade_id).first()

    #     if st is None:
    #         st = StrategyTrade(ext_trade_id=row.trade_id, group_name=row.front)
    #         try:
    #             st.strategy_id = get_strategy_id_for_strategy(engine, row.strategy, row.account_id)
    #             st.save()
    #         except Exception as e:
    #             print(f"for {row.account_id}, cannot find strategy id for {row.strategy}")
    #             print(e)

    # select t.trade_id, st.id
    # from trades_trade as t
    # left outer join portfolios_strategy_trade as st on st.ext_trade_id = t.trade_id

    # tdf = df.pivot_table(
    #     values=["fifo_pnl_realized"],
    #     index=["front", "account_id"],
    #     columns=["strategy"],
    #     aggfunc=["count", "sum"],
    # )

    # print(tdf)
    # print(tdf.sum())
    # print(f"Total = {tdf.sum().sum():0.2f}")
