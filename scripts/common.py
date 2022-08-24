import re

import environ
import pandas as pd


def gen_db_url():
    env = environ.Env()
    connection_dict = env.db("DATABASE_URL")
    db_url = (
        "postgresql://"
        + connection_dict["USER"]
        + ":"
        + connection_dict["PASSWORD"]
        + "@"
        + connection_dict["HOST"]
        + ":"
        + str(connection_dict["PORT"])
        + "/"
        + connection_dict["NAME"]
    )
    return db_url


def parse_datetime_series(raw_series: pd.Series) -> pd.Series:
    raw_series = raw_series.replace(r"", pd.NaT)

    try:
        FORMAT = "%Y-%m-%d;%H%M%S"
        series = pd.to_datetime(raw_series, errors="raise", format=FORMAT)
        series = series.dt.tz_localize(tz="US/Eastern")
        return series
    except ValueError:
        FORMAT = "%Y-%m-%d %H:%M:%S%z"
        series = pd.to_datetime(raw_series, errors="raise", format=FORMAT, utc=True)
        series = series.dt.tz_convert(tz="US/Eastern")
        return series


def parse_date_series(raw_series: pd.Series) -> pd.Series:
    FORMAT = "%Y-%m-%d"
    raw_series = raw_series.replace(r"", pd.NaT)
    series = pd.to_datetime(raw_series, errors="raise", format=FORMAT).dt.date
    return series


def transform_snake_case_names(df):
    def camel_to_snake(name):
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    snake_case_cols = {}
    for col in df.columns:
        snake_case_cols[col] = camel_to_snake(col)
    df.rename(columns=snake_case_cols, inplace=True)

    return df
