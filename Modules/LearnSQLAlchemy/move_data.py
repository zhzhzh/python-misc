import os
import sys

from data_model import RADDKeyUsageTable, RADDUsageReportTable
from sqlalchemy import create_engine, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from Utils.env_util import load_env


def insert_test(engine: Engine) -> None:
    with Session(engine) as session:
        record = RADDUsageReportTable(
            ruleapp='app',
            ruleset='cp',
            baseline1='1234',
            baseline2='2345'
        )
        session.add(record)
        session.commit()

def query(engine: Engine) -> None:
    with Session(engine) as session:
        stmt = select(
                RADDUsageReportTable.ruleapp,
                RADDUsageReportTable.ruleset,
                RADDUsageReportTable.baseline1,
                RADDUsageReportTable.baseline2,
                RADDUsageReportTable.reported,
                RADDUsageReportTable.insert_ts,
                RADDUsageReportTable.mod_ts,
                ).where(RADDUsageReportTable.baseline1 >= '20230223')
        result = session.execute(stmt).all()
        print(result)
        for row in result:
            print(row.ruleapp)


def copy_radd_usage_report(old_engine: Engine, new_engine: Engine) -> None:
    old_session = Session(old_engine)
    new_session = Session(new_engine)

    # here you can write your queries
    stmt = select(RADDUsageReportTable).where(RADDUsageReportTable.baseline1 >= '20230223')
    old_table_results = old_session.scalars(stmt).all()
    new_data = []
    for result in old_table_results:
        new_data.append({
            "ruleapp": result.ruleapp,
            "ruleset": result.ruleset,
            "baseline1": result.baseline1,
            "baseline2": result.baseline2,
            "reported": result.reported,
            "insert_ts": result.insert_ts,
            "mod_ts": result.mod_ts,
        })
    new_session.execute(insert(RADDUsageReportTable), new_data)
    new_session.commit()

    new_session.close()
    old_session.close()


def copy_radd_key_usage(old_engine: Engine, new_engine: Engine) -> None:
    old_session = Session(old_engine)
    new_session = Session(new_engine)

    # here you can write your queries
    stmt = select(RADDKeyUsageTable).where(RADDKeyUsageTable.baseline >= '20230223')
    old_table_results = old_session.scalars(stmt).all()
    new_data = []
    for result in old_table_results:
        new_data.append({
            "ruleapp": result.ruleapp,
            "ruleset": result.ruleset,
            "baseline": result.baseline,
            "rule_id": result.rule_id,
            "version": result.version,
            "folder": result.folder,
            "folder_cat": result.folder_cat,
            "radd_name": result.radd_name,
            "radd_variable": result.radd_variable,
            "key1": result.key1,
            "key2": result.key2,
            "key3": result.key3,
            "key4": result.key4,
            "insert_ts": result.insert_ts,
        })
    new_session.execute(insert(RADDKeyUsageTable), new_data)
    new_session.commit()

    new_session.close()
    old_session.close()


if __name__ == '__main__':
    load_env('.env.local')
    test_db = os.getenv('LOCAL_TEST_DB')
    rules_db = os.getenv('RULES_DB_2_0')
    if test_db is None or rules_db is None:
        sys.exit(1)

    test_db_engine = create_engine(test_db, echo=True)
    rules_db_engine = create_engine(rules_db, echo=True)


    # query(engine=rules_db_engine)
    copy_radd_usage_report(old_engine=rules_db_engine, new_engine=test_db_engine)
    copy_radd_key_usage(old_engine=rules_db_engine, new_engine=test_db_engine)
