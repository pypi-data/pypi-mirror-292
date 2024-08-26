import logging
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy.types import Integer, Float, String, Boolean, DateTime, TypeEngine, BigInteger

load_dotenv(override=True)

def disable_logging(func):
    def wrapper(*args, **kwargs):
        logging.disable(logging.CRITICAL)
        try:
            return func(*args, **kwargs)
        finally:
            logging.disable(logging.NOTSET)
    return wrapper

def map_types(dtype: pd.api.types) -> TypeEngine:
    if pd.api.types.is_integer_dtype(dtype):
        # Check if dtype is 64-bit integer
        if dtype == pd.Int64Dtype() or dtype == 'int64':
            return BigInteger()
        else:
            return Integer()
    elif pd.api.types.is_float_dtype(dtype):
        return Float()
    elif pd.api.types.is_bool_dtype(dtype):
        return Boolean()
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return DateTime()
    else:
        return String()
    
def create_default_uri_from_env():
    if all([os.getenv("POSTGRES_DB_USERNAME"), os.getenv("POSTGRES_DB_PASSWORD"), os.getenv("POSTGRES_DB_HOST"), os.getenv("POSTGRES_DB_PORT"), os.getenv("POSTGRES_DB_DEFAULT_NAME")]):
        return (
            f"postgresql://{os.getenv('POSTGRES_DB_USERNAME')}:{os.getenv('POSTGRES_DB_PASSWORD')}@{os.getenv('POSTGRES_DB_HOST')}:"
            f"{os.getenv('POSTGRES_DB_PORT')}/{os.getenv('POSTGRES_DB_DEFAULT_NAME')}?sslmode={os.getenv('POSTGRES_DB_SSLMODE', 'require')}"
        )
    else:
        return None