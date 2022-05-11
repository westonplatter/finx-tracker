/**

quick and dirty pnl calc for an ES options strat

**/


with x_times as (
	select count(*), order_time
	from trades_trade as t
	where order_time is not null
		and t.underlying_symbol = 'ESM2'
	group by order_time
	having count(*) >= 4
	order by order_time desc
)

select
	t.date_time,
	t.order_time,
	sum(abs(quantity))/count(*) as combo_quantity,
	count(*) as row_count,
	sum(t.fifo_pnl_realized)/(sum(abs(quantity))/count(*)) as pnl_per_combo,
	sum(t.fifo_pnl_realized)

from trades_trade t
join x_times gst on t.order_time = gst.order_time
where t.open_close_indicator = 'C'
group by t.date_time, t.order_time
;

select * from trades_trade where order_time = '2022-04-11 20:47:39-04:00'
