import glob
import os
from typing import List

from finx_reports_ib.config_helpers import get_ib_json
from finx_reports_ib.download_trades import fetch_report
from finx_reports_ib.adapters import ReportOutputAdapterPandas
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


def fetch_dfs_from_ibkr_flex_report() -> List[pd.DataFrame]:
    report_name = "annual"

    # configs = get_config(file_name)
    configs = os.environ
    data = get_ib_json(configs)

    if "accounts" not in data:
        return None

    open_position_dfs = []
    for account in data["accounts"]:
        # get query_id and flex_token from env var json
        query_id = int(account[report_name.lower()])
        if query_id <= 0:
            print(f"{account['name']} does not have a {report_name} query_id")
            continue
        flex_token = account["flex_token"]

        # fetch report from IBKR's FlexQuery API
        report = fetch_report(flex_token, query_id, cache_report_on_disk=False)
        output_adapter = ReportOutputAdapterPandas(report=report)
        account_ids = report.account_ids()

        # parsed each account's open positions into a df
        for aid in account_ids:
            open_position_dfs.append(output_adapter.put_open_positions(aid=aid))

    return open_position_dfs


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
    """
    Transform df to a format that can be persisted to the database.

    Args:
        df (pd.DataFrame): raw df

    Returns:
        pd.DataFrame: df
    """
    df = transform_snake_case_names(df)
    df = transform_datetime_columns(df)
    df = transform_drop_columns(df)
    df = transform_cast_types(df)
    return df


def append_to_table(engine, df, table_name):
    df.to_sql(table_name, con=engine, if_exists="append", index=False)


def truncate_table(engine, account_id: str):
    print(f"Truncating table for account_id: {account_id}")
    query = sa.text("DELETE FROM portfolios_position WHERE account_id = :account_id ;")
    stmt = query.bindparams(account_id=account_id)
    engine.execute(stmt)


def persist_portfolios_to_db(df):
    account_ids = df["account_id"].unique()
    for aid in account_ids:
        print(f"Persisting positions for account_id: {aid}")
        port = Portfolio.objects.filter(account_id=aid).first()
        if port is None:
            port = Portfolio(account_id=aid)
            port.save()


def run():
    db_url = gen_db_url()
    engine = create_engine(db_url)

    for open_positions_df in fetch_dfs_from_ibkr_flex_report():
        try:
            df = open_positions_df.copy()
            df = transform_df(df)

            for account_id, gdf in df.groupby("account_id"):
                truncate_table(engine, account_id=account_id)
                persist_portfolios_to_db(gdf)

                # replace empty strings with None
                gdf = gdf.replace('', None)

                append_to_table(engine, gdf, POSITIONS_TABLE_NAME)
        except Exception:  # trunk-ignore(pylint/W0718)
            print(f"Error persisting positions for account_id: {account_id}")
            import pdb; pdb.set_trace()
