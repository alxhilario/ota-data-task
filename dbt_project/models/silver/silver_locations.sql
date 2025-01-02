with cleaned_data as (
    select 
		uid as id,
		iso2,
		iso3,
		code3,
		fips,
		admin2,
		case
			when province_state = 'St Martin' then 'Saint Martin'
			else province_state 
		end province_state,
		case
			when country_region = 'Korea, South' then 'South Korea'
			when country_region = 'Korea, North' then 'North Korea'
			when country_region = 'Taiwan*' then 'Taiwan'
			else country_region
		end country_region,
		lat as latitude,
		longx as longtitude,
		population,
		process_date
	from {{ source('bronze_jhu_csse_repo', 'uid_iso_fips_lookup') }}
)
select 
	id::integer,
	iso2,
	iso3,
	code3::integer,
	fips::integer,
	admin2,
    province_state,
    country_region,
    concat_ws(', ', admin2, province_state, country_region) as combined_key,
	latitude,
	longtitude,
	population,
	process_date
from cleaned_data