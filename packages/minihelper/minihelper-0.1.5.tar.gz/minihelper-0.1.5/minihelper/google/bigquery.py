from loguru import logger
import google.auth
from google.cloud import bigquery
import pandas as pd


SCOPES = [
    "https://www.googleapis.com/auth/bigquery"
]


def _client() -> bigquery.Client:
    """Returns bigquery client with default credentials

    Returns:
        bigquery.Client: a bigquery client with default credentials having access to scopes
    """

    creds, proj = google.auth.default(scopes = SCOPES)
    return bigquery.Client(project=proj, credentials=creds)


def query_to_df(query:str) ->pd.DataFrame:
    """Runs a query on bigquery and output a pandas dataframe

    Args:
        query (str): query to be run

    Returns:
        pd.DataFrame: pandas dataframe resulted from the query
    """

    logger.debug(f"Querying: {query}")

    query_job = _client.query(query)
    result_df = query_job.result().to_dataframe()

    logger.info(f"Return: {len(result_df.index)}")

    return result_df


def get_table_info(dataset:str, table:str) -> dict:
    """ Get table information from biguqery

    Args:
        dataset (str): desintated dataset it the project
        table (str): destinated table in the dataset in the project

    Returns:
        dict: a dictionary contains table information
    """

    logger.debug(f"Getting table info: {table}")

    info = _client().get_table(f"{_client.project}.{dataset}.{table}")

    logger.info(f"Info get")

    return info



