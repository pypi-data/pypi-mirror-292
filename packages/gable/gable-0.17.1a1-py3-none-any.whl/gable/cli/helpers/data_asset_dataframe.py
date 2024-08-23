import pandas as pd
from gable.cli.helpers.data_asset_s3 import NativeS3Converter
from gable.openapi import ResolvedDataAsset, SourceType, StructuredDataAssetResourceName


def convert_dataframe_to_recap(path: str, dataframe: pd.DataFrame) -> dict:
    return NativeS3Converter().to_recap(dataframe, has_schema=False, event_name=path)


def resolve_dataframe_data_asset(
    data_source: str,
    path: str,
    dataframe: pd.DataFrame,
) -> ResolvedDataAsset:
    """
    Register a pandas DataFrame as a data asset
    """
    # Convert the DataFrame to a Recap StructType
    recap_schema = convert_dataframe_to_recap(path, dataframe)

    return ResolvedDataAsset(
        source_type=SourceType.dataframe,
        data_asset_resource_name=StructuredDataAssetResourceName(
            source_type=SourceType.dataframe, data_source=data_source, path=path
        ),
        schema=recap_schema,
    )
