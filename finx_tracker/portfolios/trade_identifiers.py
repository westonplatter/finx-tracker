import pandas as pd


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
