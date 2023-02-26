# https://docs.sqlalchemy.org/en/20/tutorial/index.html#unified-tutorial
# Current: https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html 
import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from Utils.env_util import load_env


def core_with_text(engine: Engine) -> None:
    # not committed automatically
    with engine.connect() as conn:
        result = conn.execute(text("select 'hello world'"))
        print(result.all())


def core_with_text_commit_as_you_go(engine: Engine) -> None:
    # committing changes - commit as you go
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE some_table (x int, y int)"))
        conn.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
            )
        conn.commit()


def core_with_text_commit_begin_once(engine: Engine) -> None:
    # committing changes - begin once
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
        )


def fetch_rows(engine: Engine) -> None:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT x, y FROM some_table"))
        for row in result:
            # print(f"-->{row}")
            # print(f"row._asdict: {row._asdict()}")
            # print(f"row._fields: {row._fields}")
            # print(f"row._mapping: {row._mapping}")
            # print(f"row.count: {row.count}")
            # print(f"row.index: {row.index}")
            # print(f"row.t: {row.t}")
            # print(f"row.tuple(): {row.tuple()}")
            print(f"x: {row.x}  y: {row.y}")
        
        result = conn.execute(text("select x, y from some_table"))
        for dict_row in result.mappings():
            print(dict_row)
            x = dict_row["x"]
            y = dict_row["y"]
            print(f"x: {x}  y: {y}")


def sending_parameters(engine: Engine) -> None:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT x, y FROM some_table WHERE y > :y"), {"y": 2})
        for row in result:
            print(f"x: {row.x}  y: {row.y}")


def sending_multiple_parameters(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
        )
        conn.commit()

def orm_session(engine: Engine) -> None:
    # ommit as you go
    stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
    with Session(engine) as session:
        result = session.execute(stmt, {"y": 6})
        for row in result:
            print(f"x: {row.x}  y: {row.y}")


def orm_session_commit(engine: Engine) -> None:
    with Session(engine) as session:
        result = session.execute(
            text("UPDATE some_table SET y=:y WHERE x=:x"),
            [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
        )
        session.commit()


if __name__ == '__main__':
    load_env()
    test_db = os.getenv('LOCAL_TEST_DB')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)

    # core_with_text(engine=engine)
    # core_with_text_commit_as_you_go(engine=engine)
    # core_with_text_commit_begin_once(engine=engine)
    # fetch_rows(engine=engine)
    # sending_parameters(engine=engine)
    # sending_multiple_parameters(engine=engine)
    # orm_session(engine=engine)
    orm_session_commit(engine=engine)
