{{ config(schema='gold') }}

select * from {{ref('silver_locations')}}