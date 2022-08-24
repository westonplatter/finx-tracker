from collections import namedtuple
from django.db import connection


def namedtuplefetchall(cursor, tuple_name: str):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple(tuple_name, [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def agg_query_strategy_pnl():
    """Return strategy aggregate PnL"""

    query = """
        select
            ps.name AS strategy_name
            , ps.description AS strategy_description
            , pg.id AS portfolio_group_id
            , pg.name AS grouping_name
            , pg.status AS grouping_status
            , sum(t.fifo_pnl_realized) AS realized_pnl
            , sum(pp.fifo_pnl_unrealized) AS unrealized_pnl
            , sum(pp.position_value) AS position_value
            -- TODO(weston) calc how drastic the Syn Straggle - Rolling / Gamma Hedged gap is

        from portfolios_grouping_trade as pgt
        join trades_trade as t on t.trade_id = pgt.ext_trade_id
        join portfolios_grouping as pg on pgt.group_id = pg.id
        join portfolios_strategy as ps on pg.strategy_id = ps.id
        left outer join portfolios_position as pp on pp.originating_transaction_id = t.transaction_id
        group by
            pg.id
            , ps.name
            , ps.description
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        return namedtuplefetchall(cursor=cursor, tuple_name='AggQueryStrategyPnl')
