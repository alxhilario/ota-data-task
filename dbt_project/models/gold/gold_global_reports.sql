{{ config(schema='gold') }}

with 
gr_combined_key_and_report_date AS (
	select
		concat_ws(', ', admin2, province_state, country_region) as combined_key,
		last_update::date as report_date,
		last_update,
		confirmed,
		deaths,
		recovered,
		active,
		process_date
	from {{ ref('silver_global_reports') }}
),
global_report_deduped as (
	select distinct on (combined_key, report_date)
		combined_key,
		report_date,
		confirmed,
		deaths,
		recovered,
		active,
		process_date
	from gr_combined_key_and_report_date
	order by combined_key, report_date, last_update desc
)
select
	--a.combined_key,
	a.report_date,
	b.id as location_id,
	a.confirmed,
	a.deaths,
	a.recovered,
	a.active,
	a.process_date
from global_report_deduped a
left join {{ ref('gold_locations') }} b
on a.combined_key = b.combined_key
where b.id is not null
order by report_date, location_id