from pyspark.sql import SparkSession, DataFrame
from loguru import logger


def _client() ->SparkSession:
    """initialize and return a SparkSession

    Returns:
        SparkSession: return a SparkSession for further action
    """
    return SparkSession \
        .builder \
        .master("yarn") \
        .appName("spark-blob_storage") \
        .getOrCreate()


def read_parquet(path: str) ->DataFrame:
    """read parquet from google cloud storage

    Args:
        path (str): the path of the parquet(s) 
            (e.g. 'gs://your-bucket-name/your-directory-path/*.parquet')
    Returns:
        DataFrame: Spark DataFrame from the parquet
    """
    logger.info(f"reading parquet from cloud storage: {path}")

    result = _client() \
        .read \
        .format('parquet') \
        .load(path)
    
    logger.info(f"return: {result.count()} row(s)")

    return result
    
    
    
    
