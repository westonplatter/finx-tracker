#
# end goal: import trades from finx-ib-report csv files for strategy
# categorization and booking.
#
# Success is simple code that does few things well.
#
import glob
import os
import re
from typing import List

import pandas as pd
from sqlalchemy import create_engine

from finx_tracker.portfolios.models import Portfolio
from finx_tracker.trades.models import Trade

from .common import gen_db_url

TRADES_TABLE_NAME = Trade._meta.db_table


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


def fetch_files_from_disk() -> List:
    path = os.getcwd()
    csv_files = glob.glob(os.path.join(path, "data", "*.csv"))
    csv_files = [x for x in csv_files if ("close" not in x and "trades" in x)]
    return csv_files


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


def remove_existing_trades(engine, df) -> pd.DataFrame:
    query = f"select trade_id from {TRADES_TABLE_NAME}"
    with engine.connect() as con:
        existing_df = pd.read_sql(query, con=con)
        existing_trade_ids = existing_df.trade_id.unique()
    new_df = df[~df.trade_id.isin(existing_trade_ids)].copy()
    return new_df


def append_to_table(engine, df, table_name):
    with engine.connect() as con:
        df.to_sql(table_name, con=con, if_exists="append", index=False)


def persist_portfolios_to_db(df):
    account_ids = df["account_id"].unique()
    for aid in account_ids:
        port = Portfolio.objects.filter(account_id=aid).first()
        if port is None:
            port = Portfolio(account_id=aid)
            port.save()


def run():
    db_url = gen_db_url()
    engine = create_engine(db_url)
    for file in fetch_files_from_disk():
        df = pd.read_csv(file)
        df = transform_df(df)
        persist_portfolios_to_db(df)
        new_df = remove_existing_trades(engine, df)
        append_to_table(engine, new_df, TRADES_TABLE_NAME)
