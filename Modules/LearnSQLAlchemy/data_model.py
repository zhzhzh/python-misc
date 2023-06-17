import os
import sys
from datetime import datetime

from pandas import DataFrame
from sqlalchemy import (Boolean, Index, String, create_engine, distinct, func,
                        select, text, tuple_)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.schema import FetchedValue
from Utils.env_util import load_env


class Base(DeclarativeBase):
    pass


class RADDKeyUsageTable(Base):
    __tablename__ = "radd_key_usage"

    id: Mapped[int] = mapped_column(primary_key=True)
    ruleapp: Mapped[str] = mapped_column(String(64))
    ruleset: Mapped[str] = mapped_column(String(64))
    baseline: Mapped[str] = mapped_column(String(32))
    rule_id: Mapped[int]
    version: Mapped[int]
    folder: Mapped[str] = mapped_column(String(64))
    folder_cat: Mapped[str] = mapped_column(String(32))
    radd_name: Mapped[str] = mapped_column(String(64))
    radd_variable: Mapped[str] = mapped_column(String(64))
    key1: Mapped[str] = mapped_column(String(256))
    key2: Mapped[str] = mapped_column(String(256))
    key3: Mapped[str] = mapped_column(String(256))
    key4: Mapped[str] = mapped_column(String(256))
    insert_ts: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        Index('idx_radd_key_usage', "ruleapp", "ruleset", "baseline"),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
        },
    )

    def __repr__(self) -> str:
        return (
            f"RADDKeyUsageTable(id={self.id!r}, ruleapp={self.ruleapp!r}, ruleset={self.ruleset!r}, "
            f"baseline={self.baseline!r}, rule_id={self.rule_id!r}, version={self.version!r}, "
            f"folder={self.folder!r}, folder_cat={self.folder_cat!r}, radd_name={self.radd_name!r}, "
            f"radd_variable={self.radd_variable!r}, key1={self.key1!r}, key2={self.key2!r}, "
            f"key3={self.key3!r}, key4={self.key4!r}, insert_ts={self.insert_ts!r})"
        )


class RADDUsageReportTable(Base):
    __tablename__ = "radd_usage_report"

    id: Mapped[int] = mapped_column(primary_key=True)
    ruleapp: Mapped[str] = mapped_column(String(64))
    ruleset: Mapped[str] = mapped_column(String(64))
    baseline1: Mapped[str] = mapped_column(String(32))
    baseline2: Mapped[str] = mapped_column(String(32))
    reported: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"))
    insert_ts: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))
    mod_ts: Mapped[datetime] = mapped_column(server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), server_onupdate=FetchedValue())

    __table_args__ = (
        Index('idx_radd_usage_report', "ruleapp", "ruleset", "baseline1", "baseline2", unique=True),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
        },
    )

    def __repr__(self) -> str:
        return (
            f"RADDUsageReportTable(id={self.id!r}, ruleapp={self.ruleapp!r}, ruleset={self.ruleset!r}, "
            f"baseline1={self.baseline1!r}, baseline2={self.baseline2!r}, reported={self.reported!r}, "
            f"insert_ts={self.insert_ts!r}, mod_ts={self.mod_ts!r})"
        )

    @staticmethod
    def insert_not_exists(engine: Engine, ruleapp: str, checkpoint: str, baseline1: str, baseline2: str, reported: bool = False) -> bool:
         with Session(engine) as session:
            stmt = (
                select(RADDUsageReportTable)
                .where(RADDUsageReportTable.ruleapp == ruleapp)
                .where(RADDUsageReportTable.ruleset == checkpoint)
                .where(RADDUsageReportTable.baseline1 == baseline1)
                .where(RADDUsageReportTable.baseline2 == baseline2)
            )

            result = session.scalars(stmt).one_or_none()
            if result is None:
                # insert new record
                new_record = RADDUsageReportTable(
                    ruleapp=ruleapp,
                    ruleset=checkpoint,
                    baseline1=baseline1,
                    baseline2=baseline2,
                    reported=reported
                )
                session.add(new_record)
                session.commit()
                return True
            else:
                return False


def emit_create_table_ddl(engine: Engine) -> None:
    Base.metadata.create_all(engine)
    '''
    CREATE TABLE radd_key_usage (
        id INTEGER NOT NULL AUTO_INCREMENT,
        ruleapp VARCHAR(64) NOT NULL,
        ruleset VARCHAR(64) NOT NULL,
        baseline VARCHAR(32) NOT NULL,
        rule_id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        folder VARCHAR(64) NOT NULL,
        folder_cat VARCHAR(32) NOT NULL,
        radd_name VARCHAR(64) NOT NULL,
        radd_variable VARCHAR(64) NOT NULL,
        key1 VARCHAR(256) NOT NULL,
        key2 VARCHAR(256) NOT NULL,
        key3 VARCHAR(256) NOT NULL,
        key4 VARCHAR(256) NOT NULL,
        insert_ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id)
    ) CHARSET=utf8mb4 ENGINE=InnoDB
    CREATE INDEX idx_radd_key_usage ON radd_key_usage (ruleapp, ruleset, baseline)

    CREATE TABLE radd_usage_report (
        id INTEGER NOT NULL AUTO_INCREMENT,
        ruleapp VARCHAR(64) NOT NULL,
        ruleset VARCHAR(64) NOT NULL,
        baseline1 VARCHAR(32) NOT NULL,
        baseline2 VARCHAR(32) NOT NULL,
        reported BOOL NOT NULL DEFAULT FALSE,
        insert_ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        mod_ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (id)
    ) CHARSET=utf8mb4 ENGINE=InnoDB
    CREATE UNIQUE INDEX idx_radd_usage_report ON radd_usage_report (ruleapp, ruleset, baseline1, baseline2)
    '''

def select_usage_cnt(engine: Engine):
    ruleapp = 'riskunifiedpaymentserv'
    checkpoint = 'ConsolidatedFunding'
    baseline = '20230228_173215'

    with Session(engine) as session:
        stmt = (
            select(
                RADDKeyUsageTable.baseline,
                func.count(distinct(RADDKeyUsageTable.rule_id)).label("rule_cnt"),
                func.count(distinct(text('radd_name, key1, key2, key3, key4'))).label("radd_usage_cnt")
            )
            .where(RADDKeyUsageTable.ruleapp == ruleapp)
            .where(RADDKeyUsageTable.ruleset == checkpoint)
            .where(RADDKeyUsageTable.baseline == baseline)
        )
        result = session.execute(stmt).one()
        if result is not None:
            print(f'{type(result)}, {result._asdict()}, {result._mapping}, {result.tuple()}')
        else:
            print(f'Get {result} for query: {stmt}')

def load_radd_usage(engine: Engine):
    ruleapp = 'riskunifiedpaymentserv'
    checkpoint = 'ConsolidatedFunding'
    baseline = '20230228_173215'

    with Session(engine) as session:
        stmt = (
            select(
                RADDKeyUsageTable.radd_name,
                RADDKeyUsageTable.key1,
                RADDKeyUsageTable.key2,
                RADDKeyUsageTable.key3,
                RADDKeyUsageTable.key4,
                func.group_concat(RADDKeyUsageTable.rule_id).label("rule_ids")
            )
            .where(RADDKeyUsageTable.ruleapp == ruleapp)
            .where(RADDKeyUsageTable.ruleset == checkpoint)
            .where(RADDKeyUsageTable.baseline == baseline)
            .group_by(
                RADDKeyUsageTable.radd_name,
                RADDKeyUsageTable.key1,
                RADDKeyUsageTable.key2,
                RADDKeyUsageTable.key3,
                RADDKeyUsageTable.key4
            )
        )
        results = session.execute(stmt)
        df = DataFrame(results.all())
        df.to_excel('data.xlsx')
        for result in results:
            # print(f'{type(result)}, {result._asdict()}, {result._mapping}, {result.tuple()}')
            print(result)


def insert_report_record(engine: Engine):
    ruleapp = 'riskunifiedpaymentserv'
    checkpoint = 'ConsolidatedFunding'
    baseline1 = '20230226_232601'
    baseline2 = '20230228_173215'
    inserted = RADDUsageReportTable.insert_not_exists(
        engine=engine,
        ruleapp=ruleapp,
        checkpoint=checkpoint,
        baseline1=baseline1,
        baseline2=baseline2
    )

    print(inserted)



def select_data(engine: Engine):
    with Session(engine) as session:
        stmt = select(RADDKeyUsageTable).where(RADDKeyUsageTable.id == 1)
        result = session.scalar(stmt)
        print(f'{type(result)}, {result}')

if __name__ == '__main__':
    load_env('.env.local')
    test_db = os.getenv('LOCAL_TEST_DB')
    # rules_db = os.getenv('RULES_DB_2_0')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)

    # emit_create_table_ddl(engine=engine)
    # select_data(engine=engine)
    # select_usage_cnt(engine=engine)
    # load_radd_usage(engine=engine)
    insert_report_record(engine=engine)
