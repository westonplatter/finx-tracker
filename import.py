#
# end goal: import trades from finx-ib-report csv files for strategy
# categorization and booking. Success is simple code that does few
# things well.
#
import re

import pandas as pd
from sqlalchemy import create_engine


def parse_datetime_series(raw_series: pd.Series) -> pd.Series:
    FORMAT = "%Y-%m-%d;%H%M%S"
    raw_series = raw_series.replace(r"", pd.NaT)
    series = pd.to_datetime(raw_series, errors="raise", format=FORMAT)
    series = series.dt.tz_localize(tz="US/Eastern")
    return series


def parse_date_series(raw_series: pd.Series) -> pd.Series:
    FORMAT = "%Y-%m-%d"
    raw_series = raw_series.replace(r"", pd.NaT)
    series = pd.to_datetime(raw_series, errors="raise", format=FORMAT).dt.date
    return series


def fetch_from_disk():
    fn = "./data/my_trades.csv"
    df = pd.read_csv(fn)
    return df


def transform_snake_case_names(df):
    def camel_to_snake(name):
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    snake_case_cols = {}
    for col in df.columns:
        snake_case_cols[col] = camel_to_snake(col)
    df.rename(columns=snake_case_cols, inplace=True)

    return df


def transform_datetime_columns(df):
    df["open_date_time"] = parse_datetime_series(df["open_date_time"])
    df["holding_period_date_time"] = parse_datetime_series(
        df["holding_period_date_time"]
    )
    df["report_date"] = parse_date_series(df["report_date"])
    return df


def transform_drop_columns(df):
    df.drop(columns=["unnamed: 0"], inplace=True)
    return df


def transform_df(df):
    df = transform_snake_case_names(df)
    df = transform_datetime_columns(df)
    df = transform_drop_columns(df)
    return df


def persist_to_db(engine, df):
    with engine.connect() as con:
        df.to_sql("trades", con=con, if_exists="replace", index=False)


def main():
    df = fetch_from_disk()
    df = transform_df(df)
    engine = create_engine("postgresql://debug:debug@127.0.0.1:65432/finx_tracker")
    persist_to_db(engine, df)


if __name__ == "__main__":
    main()
