from calendar import weekday
from tokenize import group
import pandas as pd
from sqlalchemy import create_engine
from x_import import parse_date_series, parse_datetime_series


def fetch_dates_sql():
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

def is_gs_a(grouped_df):
    strikes_unique = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call calendar at same strike
    # Front = Friday
    # Back = Monday
    return (
        strikes_unique == 1 and
        dte_diff == -3 and
        front_date.weekday() == 4 and
        back_date.weekday() == 0
    )


def is_gs_b(grouped_df):
    strikes_unique = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call diagonal with 2 strike diff
    # Front = Friday
    # Back = Monday
    return (
        strikes_unique == 3 and
        dte_diff == -3 and
        front_date.weekday() == 4 and
        back_date.weekday() == 0
    )


def classify_strategy(grouped_df):
    if is_gs_a(grouped_df):
        return "gs_a"
    if is_gs_b(grouped_df):
        return "gs_b"
    return "not automatically tagged"

def classify_vintage(grouped_df):
    exps = grouped_df.expiry.values


def main():
    engine = create_engine("postgresql://debug:debug@127.0.0.1:5432/finx_tracker")
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
    df = df.query("open_close_indicator == 'C'").copy()
    df["strategy_set"] = 0
    df["strategy"] = None

    for k, grouped in df.groupby([df.date_time]):
        strategy_key = classify_strategy(grouped)
        df.loc[grouped.index, "strategy"] = strategy_key
        df.loc[grouped.index, "front"] = grouped.expiry.min()

        # strategy_set_max = df[df["strategy"] == strategy_key]["strategy_set"].max()
        # df.loc[grouped.index, "strategy_set"] = strategy_set_max+1

        # print(k, strategy_key, strategy_set_max)

    df.sort_values(["date_time"], ascending=True)
    df.to_csv("gs_trades.csv")



if __name__ == "__main__":
    main()

