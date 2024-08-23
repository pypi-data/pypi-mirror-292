from pyspark.sql import SparkSession, DataFrame
from loguru import logger

def _client() ->SparkSession:
    """initialize and return a SparkSession

    Returns:
        SparkSession: return a SparkSession for further action
    """
    return SparkSession \
        .builder \
        .master('yarn') \
        .appName('spark-bigquery') \
        .getOrCreate()
        
        
def query(query:str) ->DataFrame:
    """query from bigquery sql

    Args:
        query (str): the query itself

    Returns:
        DataFrame: a Spark DataFrame from the query result
    """
    logger.info(f"query from bigquery: {query}")

    result = _client() \
        .read \
        .format("bigquery") \
        .option("query", query) \
        .load()
    
    logger.info(f"return: {result.count()} row(s)")

    return result