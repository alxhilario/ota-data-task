with cleaned_data as (
	select 
		fips::integer,
		admin2,
		case 
			when TRIM(province_state) = TRIM(country_region) then null
			when province_state = 'Taiwan' then null
			when province_state = 'Fench Guiana' then 'French Guiana'
			when province_state = 'Falkland Islands (Islas Malvinas)' then 'Falkland Islands (Malvinas)'
			when province_state = 'St Martin' then 'Saint Martin'
			when province_state is null and country_region = 'North Ireland' then 'Northern Ireland'
            when province_state is null and country_region in ('St. Martin', 'St Martin') then 'Saint Martin'
			when province_state is null and country_region in (
                'Faroe Islands', 'Jersey', 'Gibraltar', 'Cayman Islands', 'Reunion', 'Martinique', 'Guernsey', 
                'Curacao', 'Guadeloupe', 'Puerto Rico', 'Saint Barthelemy', 'Channel Islands', 'Guam', 'Aruba', 'Greenland',
                'French Guiana', 'Mayotte'
            ) then country_region
			else TRIM(province_state) 
		end province_state,
		case
			when province_state is null and country_region in ('Guam', 'Puerto Rico') then 'US'
			when country_region in ('Taipei and environs', 'Taiwan*') then 'Taiwan'
			when country_region in ('Mainland China', 'Hong Kong', 'Macau', 'Hong Kong SAR', 'Macao SAR') then 'China'
			when country_region = 'Korea, North' then 'North Korea'
			when country_region in ('Republic of Korea', 'Korea, South') then 'South Korea'
			when country_region = 'Republic of Ireland' then 'Ireland'
			when country_region = 'Czech Republic' then 'Czechia'
			when country_region = 'Viet Nam' then 'Vietnam'
			when country_region like 'Iran%' then 'Iran'
			when country_region = 'East Timor' then 'Timor-Leste'
			when province_state is null and country_region in ('Aruba', 'Curacao') then 'Netherlands'
			when country_region in ('The Bahamas', 'Bahamas, The') then 'Bahamas'
			when country_region in ('The Gambia', 'Gambia, The') then 'Gambia'
			when country_region = 'Republic of Moldova' then 'Moldova'
			when province_state is null and country_region in ('Greenland', 'Faroe Islands') then 'Denmark'
			when province_state is null and country_region in ('Mayotte', 'French Guiana', 'Reunion', 'Martinique', 'St. Martin', 'Saint Martin', 'Guadeloupe', 'Saint Barthelemy')  then 'France'
			when province_state is null and country_region in ('Jersey', 'Gibraltar', 'Cayman Islands', 'North Ireland', 'Guernsey', 'Channel Islands') then 'United Kingdom'
			else TRIM(country_region)
		end country_region,
		last_update::timestamp as last_update,
		coalesce(lat, latitude) as latitude,
		coalesce(longx, longitude) as longtitude,
		confirmed::integer,
		deaths::integer,
		recovered::integer,
		active::integer,
		coalesce(incident_rate, incidence_rate) as incident_rate,
		case_fatality_ratio,
        process_date
	from {{ source('bronze_jhu_csse_repo', 'csse_covid_19_daily_reports_global') }}
)
SELECT * FROM cleaned_data