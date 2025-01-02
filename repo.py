import datetime
import io
import zipfile
from pathlib import Path
from typing import Any, Generator, Iterable, Mapping, Optional

import requests
from dagster import (
    AssetExecutionContext,
    AssetKey,
    Definitions,
    MaterializeResult,
    asset,
    define_asset_job,
    get_dagster_logger,
)
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, DbtProject, dbt_assets
from dagster_embedded_elt.dlt import (
    DagsterDltResource,
    DagsterDltTranslator,
    dlt_assets,
)
from dagster_embedded_elt.dlt.dlt_event_iterator import DltEventType
from dlt.extract.resource import DltResource

from dlt_pipeline.jhu_csse_covid_19_pipeline import get_pipeline, get_source


logger = get_dagster_logger()

SCRATCH_DIR = "/tmp"
DATASET_URL = "https://github.com/CSSEGISandData/COVID-19/archive/refs/heads/master.zip"
DATASET_BASE_LOCATION = f"{SCRATCH_DIR}/COVID-19-master"
GROUP_NAME = "jhu_csse_covid_19"
RELATIVE_PATH_TO_MY_DBT_PROJECT = "./dbt_project"

dbt_project = DbtProject(
    project_dir=Path(__file__)
    .joinpath("..", RELATIVE_PATH_TO_MY_DBT_PROJECT)
    .resolve(),
)
dbt_project.prepare_if_dev()
dbt = DbtCliResource(
    project_dir=dbt_project,
)


class DDltTranslator(DagsterDltTranslator):
    def get_asset_key(self, resource: DltResource) -> AssetKey:
        """Overrides asset key to be the dlt resource name."""
        return AssetKey(f"{resource.name}")

    def get_deps_asset_keys(self, resource: DltResource) -> Iterable[AssetKey]:
        """Overrides dependency to be a single source asset."""
        return [AssetKey("jhu_csse_covid_19_data_repo")]


class DDbtTranslator(DagsterDbtTranslator):
    def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> Optional[str]:
        return GROUP_NAME


@asset(group_name=GROUP_NAME, kinds={"file"})
def jhu_csse_covid_19_data_repo() -> MaterializeResult:
    """Downloads the JHU CCSE Covid 19 Github repo and extracts the content to temp dir."""
    r = requests.get(DATASET_URL, allow_redirects=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(SCRATCH_DIR)
    return MaterializeResult(
        metadata={"url": DATASET_URL, "dataset_location": DATASET_BASE_LOCATION}
    )


@dlt_assets(
    dlt_source=get_source(DATASET_BASE_LOCATION, datetime.datetime.now()),
    dlt_pipeline=get_pipeline(),
    group_name=GROUP_NAME,
    dagster_dlt_translator=DDltTranslator(),
)
def jhu_csse_covid_19_dlt_pipeline(
    context: AssetExecutionContext, dlt: DagsterDltResource
) -> Generator[DltEventType, Any, None]:
    """Runs the DLT pipeline."""
    yield from dlt.run(
        context=context, write_disposition="replace", loader_file_format="csv"
    )


@dbt_assets(manifest=dbt_project.manifest_path) #, dagster_dbt_translator=DDbtTranslator())
def dbt_models(context: AssetExecutionContext, dbt: DbtCliResource):
    """Creates assets for dbt models"""
    yield from dbt.cli(["build"], context=context).stream()


all_assets_job = define_asset_job(name="jhu_csse_covid_19_data_ingestion")

defs = Definitions(
    assets=[
        jhu_csse_covid_19_data_repo,
        jhu_csse_covid_19_dlt_pipeline,
        dbt_models,
    ],
    resources={
        "dlt": DagsterDltResource(),
        "dbt": dbt,
    },
    jobs=[all_assets_job],
)
