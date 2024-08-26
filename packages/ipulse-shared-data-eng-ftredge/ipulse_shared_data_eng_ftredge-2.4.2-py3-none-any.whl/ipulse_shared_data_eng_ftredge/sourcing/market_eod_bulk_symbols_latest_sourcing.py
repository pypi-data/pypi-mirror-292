# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long


from typing import Optional
import requests

def source_latest_eod_ohlcva_for_symbols(exchange, symbols, records_origin_short_ref, api_token,date:Optional[str]=None):
    """
    THIS FUNCTION SHALL RETURN A LIST OF DICTS, WHERE EACH DICT REPRESENTS A RECORD.
    EODHD already send the data in this format.
    """

    if records_origin_short_ref=="eodhd__eod_bulk_last_day":
        if date:
            # check if from_date is in the format YYYY-MM-DD
            if len(date) != 10:
                raise ValueError("The date should be in the format YYYY-MM-DD")
            api_url_without_token = (
                f"https://eodhd.com/api/eod-bulk-last-day/{exchange}?symbols={','.join(symbols)}&fmt=json&date={date}&api_token="
            )
        else:

            api_url_without_token = (
                    f"https://eodhd.com/api/eod-bulk-last-day/{exchange}?symbols={','.join(symbols)}&fmt=json&api_token="
                )
        api_url_with_token = api_url_without_token + api_token

        response = requests.get(url=api_url_with_token, timeout=30)
        response.raise_for_status()
        sourced_data=response.json()

    else:
        raise ValueError(f"Data Origin {records_origin_short_ref} not supported.")

    return sourced_data, api_url_without_token



def source_market_single_symbol_bulk_from_api( api_token, symbol_at_data_provider,records_origin_short_ref, from_date:Optional[str]=None ):

    """
    THIS FUNCTION SHALL RETURN A LIST OF DICTS, WHERE EACH DICT REPRESENTS A RECORD.
    EODHD already send the data in this format.
    """

  

    if records_origin_short_ref=="eodhd__eod":

        if from_date:
            # check if from_date is in the format YYYY-MM-DD
            if len(from_date) != 10:
                raise ValueError("The from_date should be in the format YYYY-MM-DD")

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
