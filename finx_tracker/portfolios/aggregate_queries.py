from collections import namedtuple
from typing import List

import sqlalchemy as sa
from django.db import connection


def namedtuple_fetchall(cursor, tuple_name: str):
    "Return all rows from a cursor as a namedtuple"
    nt_result = namedtuple(tuple_name, [col[0] for col in cursor.description])
    return [nt_result(*row) for row in cursor.fetchall()]


def agg_query_strategy_pnl():
    """Return strategy aggregate PnL"""

    query = """
        select
            t.account_id AS account_id
            , ps.key AS strategy_key
            , ps.description AS strategy_description
            , pg.id AS grouping_id
            , pg.name AS grouping_name
            , pg.status AS grouping_status
            , sum(t.fifo_pnl_realized) AS realized_pnl
            , sum(pp.fifo_pnl_unrealized) AS unrealized_pnl
            , sum(pp.position_value) AS position_value
            , sum(t.fifo_pnl_realized) + sum(pp.fifo_pnl_unrealized) AS total_pnl
            -- TODO calc percent of unrealized vs realized vs cost basis (helpful for rolling option positions)

        from trades_trade as t
        left outer join portfolios_grouping_trade as pgt on t.trade_id = pgt.trade_id
        left outer join portfolios_grouping as pg on pgt.group_id = pg.id
        left outer join portfolios_strategy as ps on pg.strategy_id = ps.id
        left outer join portfolios_portfolio as p on p.id = ps.portfolio_id
        left outer join portfolios_position as pp on pp.originating_transaction_id = t.transaction_id

        group by
            t.account_id
            , pg.id
            , ps.key
            , ps.description

        order by
            t.account_id
            , ps.key
            , pg.id
        ;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        return namedtuple_fetchall(cursor=cursor, tuple_name="AggQueryStrategyPnl")
