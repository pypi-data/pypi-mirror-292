# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long
# pylint: disable=unused-variable
# pylint: disable=broad-exception-caught
from ipulse_shared_base_ftredge import CloudProvider, DataSourceType, DuplicationHandling, MatchConditionType
from ipulse_shared_data_eng_ftredge import Pipelinemon
from .cloud_gcp import (write_json_to_gcs_extended,
                        read_json_from_gcs,
                        read_json_from_gcs_extended)

#######################################################################################################################
#######################################################################################################################
#################################################     cloud IO functions      ########################################

# Define the central function that routes to the relevant cloud-specific function
def write_json_to_cloud_storage_extended(cloud_storage:CloudProvider | DataSourceType, storage_client, data:dict | list | str, bucket_name: str, file_name: str,
                      duplication_handling:DuplicationHandling,  duplication_match_condition_type: MatchConditionType, duplication_match_condition: str = "",
                       max_retries:int=2, max_matched_deletable_files:int=1,
                      pipelinemon: Pipelinemon = None, logger=None, print_out=False, raise_e=False):

    """
    This function writes data to a cloud storage location, based on the cloud storage provider and data source type.
    Pipelinemon if provided, will be used to log the operation. Systems impacted and Write operation status will be logged.
    """

    supported_cloud_storage_values = [CloudProvider.GCP, DataSourceType.GCS]

    if cloud_storage in [CloudProvider.GCP, DataSourceType.GCS]:
        return write_json_to_gcs_extended(
            pipelinemon=pipelinemon,
            storage_client=storage_client,
            data=data,
            bucket_name=bucket_name,
            file_name=file_name,
            duplication_handling_enum=duplication_handling,
            duplication_match_condition_type_enum=duplication_match_condition_type,
            duplication_match_condition=duplication_match_condition,
            max_retries=max_retries,
            max_deletable_files=max_matched_deletable_files,
            logger=logger,
            print_out=print_out,
            raise_e=raise_e
        )

    raise ValueError(f"Unsupported cloud storage : {cloud_storage}. Supported cloud storage values: {supported_cloud_storage_values}")


def read_json_from_cloud_storage(cloud_storage:CloudProvider | DataSourceType , storage_client, bucket_name:str, file_name:str, logger=None, print_out:bool=False):

    supported_cloud_storage_values = [CloudProvider.GCP, DataSourceType.GCS]

    if cloud_storage in [CloudProvider.GCP, DataSourceType.GCS]:
        return read_json_from_gcs(storage_client=storage_client, bucket_name=bucket_name, file_name=file_name, logger=logger, print_out=print_out)

    raise ValueError(f"Unsupported cloud storage: {cloud_storage}. Supported cloud storage values: {supported_cloud_storage_values}")


def read_json_from_cloud_storage_extended(cloud_storage:CloudProvider | DataSourceType, storage_client, bucket_name:str, file_name:str, pipelinemon:Pipelinemon=None,logger=None, print_out:bool=False):

    supported_cloud_storage_values = [CloudProvider.GCP, DataSourceType.GCS]

    if cloud_storage in [CloudProvider.GCP, DataSourceType.GCS]:
        return read_json_from_gcs_extended(pipelinemon=pipelinemon, storage_client=storage_client, bucket_name=bucket_name, file_name=file_name, logger=logger, print_out=print_out)

    raise ValueError(f"Unsupported cloud storage: {cloud_storage}. Supported cloud storage values: {supported_cloud_storage_values}")