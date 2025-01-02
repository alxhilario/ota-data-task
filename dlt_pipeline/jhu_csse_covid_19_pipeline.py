import glob
import logging
from datetime import datetime
from typing import Any, Generator

import dlt
import pandas as pd
from dlt.extract.resource import DltResource

DAILY_REPORTS_GLOBAL_DIR = "/csse_covid_19_data/csse_covid_19_daily_reports/"
UID_ISO_FIPS_LOOKUP_FILE = "/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv"

# explicitly define the data types to resolve any discrepancies
# when pandas tries to infer the schema of the csv files
DTYPES = {
    "FIPS": pd.Int64Dtype(),
    "Confirmed": pd.Int64Dtype(),
    "Deaths": pd.Int64Dtype(),
    "Recovered": pd.Int64Dtype(),
    "Active": pd.Int64Dtype(),
}

logger = logging.getLogger(__name__)


def list_csv_files(dir) -> list[str]:
    return glob.glob(f"{dir}/*.csv")


@dlt.resource(parallelized=True, table_name="csse_covid_19_daily_reports_global")
def daily_reports_global(
    file_paths: list[str], process_date: datetime
) -> Generator[pd.DataFrame, Any, None]:
    for file in file_paths:
        df = pd.read_csv(file, dtype=DTYPES)
        df["process_date"] = process_date
        yield df


@dlt.resource(table_name="uid_iso_fips_lookup")
def uid_iso_fips_lookup(
    file_path: str, process_date: datetime
) -> Generator[pd.DataFrame, Any, None]:
    df = pd.read_csv(file_path, dtype=DTYPES)
    df["process_date"] = process_date
    yield df


@dlt.source
def get_source(source_path: str, process_date: datetime) -> list[DltResource]:
    global_report_urls = list_csv_files(f"{source_path}/{DAILY_REPORTS_GLOBAL_DIR}")
    logger.info(f"Global report file count={len(global_report_urls)}")
    return [
        daily_reports_global(global_report_urls, process_date),
        uid_iso_fips_lookup(f"{source_path}/{UID_ISO_FIPS_LOOKUP_FILE}", process_date),
    ]


def get_pipeline(
    pipeline: str = "jhu_csse_covid_19", destination: str = "postgres", dataset="bronze"
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name=pipeline, destination=destination, dataset_name=dataset
    )
