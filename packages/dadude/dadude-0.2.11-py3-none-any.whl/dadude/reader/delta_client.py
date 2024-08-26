from loguru import logger
import pandas as pd
from deltalake import DeltaTable
# from deltalake.data_catalog import DataCatalog

from ..config import default_storage_config, DeltaStorageTier


logger = logger.bind(name=__name__)


class DeltaClientError(Exception):
    """Base class for exceptions in this module."""

    pass


def read_delta_table(
    bucket: str,
    tier: str,
    table: str,
    version: int | None = None,
    preview: bool = False,
    local_cache_dir: str | None = None,
) -> pd.DataFrame:
    tier_path = DeltaStorageTier(tier).value
    table_path = f"s3a://{bucket}/{tier_path}/{table}"
    if version:
        logger.info(f"Reading {table} version {version}")
    else:
        logger.info(f"Reading latest version of {table}")
    try:
        dt = DeltaTable(
            table_path, version=version, storage_options=default_storage_config
        )
    except Exception as e:
        logger.error(f"Error reading DeltaTable: {e}")
        raise DeltaClientError(f"Error reading DeltaTable: {e}")
    df_pdf = dt.to_pandas()
    if preview:
        logger.info(f"Previewing first 5 rows of {table_path}")
        print(df_pdf.head())
    if local_cache_dir:
        logger.info(f"Saving DeltaTable to {local_cache_dir}")
        df_pdf.to_json(
            f"{local_cache_dir}/{table}.json", orient="records", lines=True, index=False
        )
    return df_pdf


def read_delta_table_from_catalog():
    raise NotImplementedError
    # return DeltaTable.from_data_catalog(
    #     data_catalog=DataCatalog.UNITY,
    #     database_name="materials",
    #     table_name="property_entity",
    # )


# TODO: add reading from local cache
