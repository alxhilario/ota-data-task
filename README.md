# OTA Data Task

This project is designed to ingest, process, and analyze COVID-19 data from the JHU CSSE repository using a combination of Dagster, dlt, and dbt.

## Running the Project

To run the project, follow these steps:

1. **Create a .env file containing the database credentials**:
   ```sh
	# required env variables
	DAGSTER_POSTGRES_PASSWORD=<ADD YOUR PASSWORD HERE>
	JHU_CSSE_COVID_19__DESTINATION__POSTGRES__CREDENTIALS__PASSWORD=<ADD YOUR PASSWORD HERE>

	# optional env variables
	# JHU_CSSE_COVID_19__DESTINATION__POSTGRES__CREDENTIALS__DATABASE=postgres
	# JHU_CSSE_COVID_19__DESTINATION__POSTGRES__CREDENTIALS__USERNAME=admin
	# DAGSTER_POSTGRES_DB=postgres
	# DAGSTER_POSTGRES_USER=dagster_admin
   ```

1. **Build and Start Docker Containers**:
   ```sh
   docker-compose up --build
   ```

2. **Access Dagster Webserver**:
   Open your browser and navigate to `http://localhost:3000` to access the Dagster webserver.

3. **Run the Data Ingestion Job**:
   Trigger the [jhu_csse_covid_19_data_ingestion job](http://localhost:3000/locations/jhu_csse_covid_19/jobs/jhu_csse_covid_19_data_ingestion) from the Dagster webserver to start the data ingestion and transformation process.


## Tech Stack and Key Components

### 1. Dagster

Dagster is used as the orchestrator for the data pipeline. It manages the execution of various tasks, including data extraction, transformation, and loading. Some of reasons why Dagster is chosen as the orchestrator:

* Type-safe pipelines: Dagster enforces type checks on inputs and outputs, making the pipelines more robust and easier to debug.
* Python-first: It is Python-based, making it familiar for data engineers.
* Graph-based execution: Dagster uses Directed Acyclic Graphs (DAGs) to represent dependencies, making workflows transparent and easy to understand.
* Integration with modern tools: Dagster integrates seamlessly with tools commonly used in data workflows like dbt and dlt.

### 2. dlt

dlt (data load tool) is used for extracting data from the JHU CSSE repository and loading it into the data storage. It's chosen for this project because of the following reasons:

* Purpose-built for ELT workflows: dlt is specifically designed for ELT workflows, making it ideal for the first step of extracting data from various sources and loading it into a destination. It handles the complexity of data extraction while allowing flexibility for downstream transformations.
* Python-first: It is Python-based, making it familiar for data engineers.

### 3. dbt

dbt (data build tool) is used for transforming the data in the data storage. It allows for modular SQL-based transformations and ensures data quality through testing. It's well-suited for transforming data because of the following reasons:

* SQL-first: dbt allows users to write transformations directly in SQL, making it intuitive for data analysts and engineers familiar with SQL.
* Works within the ELT paradigm: It focuses entirely on transforming raw data into clean, analytics-ready datasets, following the modern ELT paradigm.
* Declarative and configurable: Transformations are written as SQL models, and dependencies between them are defined declaratively
* Open-Source with strong community support: dbt is open-source and backed by an active community that contributes plugins, adapters, and support.


## Data Analysis

### 1. What are the top 5 most common values in a particular column, and what is their frequency?

``` SQL
-- for this question, I'm getting the common values in the country_region column

select 
	gl.country_region, count(1) as c
from gold.gold_global_reports ggr
left join gold.gold_locations gl 
	on ggr.location_id = gl.id
group by gl.country_region 
order by c desc limit 5
```

### 2. How does a particular metric change over time within the dataset?

``` SQL
-- the daily growth of confirmed cases
select
	report_date,
	sum(confirmed) as total_confirmed,
	(sum(confirmed) - lag(SUM(confirmed)) over (order by report_date)) as daily_change
from gold.gold_global_reports
group by report_date
order by report_date asc
```

### 3. Is there a correlation between two specific columns? Explain your findings.

``` SQL
-- correlation between confirmed cases and deaths
with stats as (
	select
		avg(confirmed) as avg_confirmed,
		avg(deaths) as avg_deaths,
		stddev(confirmed) as std_confirmed,
		stddev(deaths) as std_deaths
	from
		gold.gold_global_reports
),
covariance as (
	select
		SUM((confirmed - avg_confirmed) * (deaths - avg_deaths)) / (count(*) - 1) as cov_confirmed_deaths
	from
		gold.gold_global_reports, stats
)
-- this returns a value of 0.73224999
select cov_confirmed_deaths / (std_confirmed * std_deaths) as correlation
from covariance, stats
```

Finding:
* The value of `0.73224999` represents the Pearson correlation coefficient, in this case, indicates a strong positive correlation.
* The closer the value is to 1, the stronger the positive linear relationship between the two variables.
* Since the value is positive, it means that as one variable increases (i.e., confirmed cases), the other variable (e.g., deaths) tends to also increase.
