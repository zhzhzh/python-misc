import os
import sys

from sqlalchemy import create_engine
from Utils.env_util import load_env

if __name__ == '__main__':
    load_env()
    test_db = os.getenv('LOCAL_TEST_DB')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)
