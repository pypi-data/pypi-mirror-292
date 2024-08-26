from loguru import logger
import pandas as pd
from deltalake import DeltaTable
# from deltalake.data_catalog import DataCatalog

from ..config import default_storage_config, DeltaStorageTier, DEFAULT_BUCKET


logger = logger.bind(name=__name__)


class DeltaClientError(Exception):
    """Base class for exceptions in this module."""

    pass


def read_delta_table(
    tier: str, table: str, version: int | None = None, preview: bool = False, save_dir: str | None = None
) -> pd.DataFrame | None:
    tier_path = DeltaStorageTier(tier).value
    table_path = f"s3a://{DEFAULT_BUCKET}/{tier_path}/{table}"
    if version:
        logger.info(f"Reading {table} version {version}")
    else:
        logger.info(f"Reading latest version of {table}")
    try:
        dt = DeltaTable(table_path, version=version, storage_options=default_storage_config)
    except Exception as e:
        logger.error(f"Error reading DeltaTable: {e}")
        raise DeltaClientError(f"Error reading DeltaTable: {e}")
    df_pdf = dt.to_pandas()
    if preview:
        logger.info(f"Previewing first 5 rows of {table_path}")
        print(df_pdf.head())
    if save_dir:
        logger.info(f"Saving DeltaTable to {save_dir}")
        df_pdf.to_json(
            f"{save_dir}/{table}.json", orient="records", lines=True, index=False
        )
    else:
        return df_pdf


def read_delta_table_from_catalog():
    raise NotImplementedError
    # return DeltaTable.from_data_catalog(
    #     data_catalog=DataCatalog.UNITY,
    #     database_name="materials",
    #     table_name="property_entity",
    # )


# TODO: add reading from local cache
