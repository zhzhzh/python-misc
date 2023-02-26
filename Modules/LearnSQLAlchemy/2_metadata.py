# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html
import os
import sys

from sqlalchemy import (Column, ForeignKey, Integer, MetaData, String, Table,
                        create_engine)
from Utils.env_util import load_env

metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30)),
    Column("fullname", String(60)),
)

address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String(120), nullable=False),
)

if __name__ == '__main__':
    load_env()
    test_db = os.getenv('LOCAL_TEST_DB')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)

    # print(user_table.c.name)
    # print(user_table.c.keys())
    # print(user_table.primary_key)

    metadata_obj.create_all(engine)
    # metadata_obj.drop_all(engine)

