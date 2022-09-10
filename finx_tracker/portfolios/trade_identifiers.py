from typing import List, Set

STATIC_PUT_CALL_SET = set(["P", "C"])
STATIC_CALL_SET = set(["C"])
STATIC_PUT_SET = set(["P"])


def is_gs_a(grouped_df):
    strikes_unique = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call calendar at same strike
    # Front = Friday
    # Back = Monday
    return strikes_unique == 1 and dte_diff == -3 and front_date.weekday() == 4 and back_date.weekday() == 0


def is_gs_b(grouped_df):
    strikes_unique = len(grouped_df.strike.unique())

    front_date = grouped_df.expiry.min()
    back_date = grouped_df.expiry.max()
    dte_diff = (front_date - back_date).days

    # short put/call diagonal with 2 strike diff
    # Front = Friday
    # Back = Monday
    return strikes_unique == 3 and dte_diff == -3 and front_date.weekday() == 4 and back_date.weekday() == 0


def classify_strategy(grouped_df):
    if is_gs_a(grouped_df):
        return "gs_a"
    if is_gs_b(grouped_df):
        return "gs_b"
    return "not automatically tagged"


def is_straddle(put_call_set: Set, strikes: List = [], expiries: List = []):
    return len(strikes) == 1 and len(expiries) == 1 and put_call_set == STATIC_PUT_CALL_SET


def is_strangle(put_call_set: Set, strikes: List = [], expiries: List = []):
    raise NotImplementedError
    return len(strikes) == 2 and len(expiries) == 1 and (put_call_set == STATIC_CALL_SET or STATIC_PUT_SET)


def is_diagonal(strikes: List = [], expiries: List = []):
    raise NotImplementedError


class OptionStrategyIdentifier(object):
    @classmethod
    def classify_df(cls, df):
        pass
