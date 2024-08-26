# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=logging-fstring-interpolation
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught
from typing import List
import requests
from ipulse_shared_base_ftredge import AttributeType



def source_market_single_symbol_bulk_from_api( api_token, symbol_at_data_provider, from_date, records_origin_short_ref):

    """
    THIS FUNCTION SHALL RETURN A LIST OF DICTS, WHERE EACH DICT REPRESENTS A RECORD.
    EODHD already send the data in this format.
    """

    if records_origin_short_ref=="eodhd__eod":

        if from_date:
            api_url_without_token = (
                f"https://eodhd.com/api/eod/{symbol_at_data_provider}?from={from_date}&order=d&fmt=json&api_token="
            )
        else:
            api_url_without_token = (
                f"https://eodhd.com/api/eod/{symbol_at_data_provider}?order=d&fmt=json&api_token="
            )

        api_url_with_token = api_url_without_token + api_token
        response = requests.get(url=api_url_with_token, timeout=30)
        response.raise_for_status()
        sourced_data=response.json()
    else:
        raise ValueError(f"Data Origin {records_origin_short_ref} not supported.")

    return sourced_data, api_url_without_token



def get_attribute_of_market_records_single_symbol(records_formatting_provider_short_ref:str, attribute_type:AttributeType, records: List[dict]):


    if records_formatting_provider_short_ref=="eodhd__eod":
        date_col_name = "date"
        if attribute_type==AttributeType.OLDEST_DATE:
            records.sort(key=lambda x: x[date_col_name])
            return records[0][date_col_name]
        if attribute_type==AttributeType.RECENT_DATE:
            records.sort(key=lambda x: x[date_col_name])
            return records[-1][date_col_name]
        else:
            raise ValueError(f"Attribute Type {attribute_type} not supported for records_origin_short_ref {records_formatting_provider_short_ref}.")

    elif records_formatting_provider_short_ref=="sourcing_schema_checked":
        date_col_name = "date_id"
        if attribute_type==AttributeType.OLDEST_DATE:
            records.sort(key=lambda x: x[date_col_name])
            return records[0][date_col_name]
        if attribute_type==AttributeType.RECENT_DATE:
            records.sort(key=lambda x: x[date_col_name])
            return records[-1][date_col_name]
        else:
            raise ValueError(f"Attribute Type {attribute_type} not supported for records_origin_short_ref {records_formatting_provider_short_ref}.")
    else:
        raise ValueError(f"Data Origin Reference {records_formatting_provider_short_ref} not supported.")
