#
# end goal: import trades from finx-ib-report csv files for strategy
# categorization and booking.
#
# Success is simple code that does few things well.
#
import glob
import os
from typing import List

from finx_reports_ib.config_helpers import get_ib_json
from finx_reports_ib.download_trades import fetch_report
from finx_reports_ib.adapters import ReportOutputAdapterPandas
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


from finx_tracker.portfolios.models import Portfolio
from finx_tracker.trades.models import Trade


from .common import (
    gen_db_url,
    parse_date_series,
    parse_datetime_series,
    transform_snake_case_names,
)

TRADES_TABLE_NAME = Trade._meta.db_table


def fetch_dfs_from_ibkr_flex_report() -> List[pd.DataFrame]:
    """
    Fetches trades from IBKR's FlexQuery API

    Returns:
        List[pd.DataFrame]: df with trades segmented by account_id
    """
    report_name = "weekly"

    # configs = get_config(file_name)
    configs = os.environ
    data = get_ib_json(configs)

    if "accounts" not in data:
        return None

    trade_dfs = []
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
            trade_dfs.append(output_adapter.put_trades(aid=aid))

    return trade_dfs


def fetch_files_from_disk() -> List:
    path = os.getcwd()
    csv_files = glob.glob(os.path.join(path, "data", "*.csv"))
    csv_files = [x for x in csv_files if ("close" not in x and "trades" in x)]
    return csv_files


def transform_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["open_date_time"] = parse_datetime_series(df["open_date_time"])
    df["holding_period_date_time"] = parse_datetime_series(df["holding_period_date_time"])
    df["report_date"] = parse_date_series(df["report_date"])
    return df


def transform_drop_columns(df: pd.DataFrame) -> pd.DataFrame:
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


def transform_cast_types(df: pd.DataFrame) -> pd.DataFrame:
    # placeholder
    return df


def transform_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply transforms to df
    """
    df = transform_snake_case_names(df)
    df = transform_datetime_columns(df)
    df = transform_drop_columns(df)
    df = transform_cast_types(df)
    return df


def remove_existing_trades(engine: Engine, df: pd.DataFrame) -> pd.DataFrame:
    query = f"select trade_id from {TRADES_TABLE_NAME}"
    with engine.connect() as con:
        existing_df = pd.read_sql(query, con=con)
        existing_trade_ids = existing_df.trade_id.unique()
    new_df = df[~df.trade_id.isin(existing_trade_ids)].copy()
    return new_df


def append_to_table(engine: Engine, df: pd.DataFrame, table_name: str) -> None:
    df.to_sql(table_name, con=engine, if_exists="append", index=False)


def persist_portfolios_to_db(df: pd.DataFrame) -> None:
    account_ids = df["account_id"].unique()
    for aid in account_ids:
        port = Portfolio.objects.filter(account_id=aid).first()
        if port is None:
            port = Portfolio(account_id=aid)
            port.save()


def run():
    """
    Run is the expected django scripts entry point
    """
    db_url = gen_db_url()
    engine = create_engine(db_url)

    for df in fetch_dfs_from_ibkr_flex_report():
        df = transform_df(df)
        persist_portfolios_to_db(df)
        new_df = remove_existing_trades(engine, df)
        append_to_table(engine, new_df, TRADES_TABLE_NAME)
