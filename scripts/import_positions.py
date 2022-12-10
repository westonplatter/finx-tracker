import glob
import os
from typing import List

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine

from finx_tracker.portfolios.models import Portfolio, Position

from .common import (
    gen_db_url,
    parse_date_series,
    parse_datetime_series,
    transform_snake_case_names,
)

POSITIONS_TABLE_NAME = Position._meta.db_table


def fetch_files_from_disk() -> List:
    path = os.getcwd()
    csv_files = glob.glob(os.path.join(path, "data", "*_open_positions.csv"))
    return csv_files


def transform_datetime_columns(df):
    df["open_date_time"] = parse_datetime_series(df["open_date_time"])
    df["holding_period_date_time"] = parse_datetime_series(df["holding_period_date_time"])
    df["report_date"] = parse_date_series(df["report_date"])
    return df


def transform_drop_columns(df):
    cols = [
        "unnamed: 0",
        "serial_number",
        "delivery_type",
        "commodity_type",
        "fineness",
        "weight",
    ]
    for col in cols:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
    return df


def transform_cast_types(df):
    df = df.astype({"code": str})
    return df


def transform_df(df):
    df = transform_snake_case_names(df)
    df = transform_datetime_columns(df)
    df = transform_drop_columns(df)
    df = transform_cast_types(df)
    return df


def append_to_table(engine, df, table_name):
    df.to_sql(table_name, con=engine, if_exists="append", index=False)


def truncate_table(engine, account_id: str):
    query = sa.text("DELETE FROM portfolios_position WHERE account_id = :account_id ;")
    stmt = query.bindparams(account_id=account_id)
    engine.execute(stmt)


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
        file_df = pd.read_csv(file)
        transform_df(file_df)
        for account_id, df in file_df.groupby("account_id"):
            truncate_table(engine, account_id=account_id)
            persist_portfolios_to_db(df)
            append_to_table(engine, df, POSITIONS_TABLE_NAME)
