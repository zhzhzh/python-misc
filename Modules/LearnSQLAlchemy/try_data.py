import os
import sys

from sqlalchemy import (Column, ForeignKey, Integer, MetaData, String, Table,
                        create_engine, insert, select)
from sqlalchemy.engine import Engine
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


def core_insert(engine: Engine) -> None:
    stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")
    print(stmt) # INSERT INTO user_account (name, fullname) VALUES (:name, :fullname)
    compiled = stmt.compile()
    print(compiled.params) # {'name': 'spongebob', 'fullname': 'Spongebob Squarepants'}
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
        print(result.inserted_primary_key)
        print(f"{result}")


def core_insert_many(engine: Engine) -> None:
    print(insert(user_table)) # INSERT INTO user_account (id, name, fullname) VALUES (:id, :name, :fullname)
    with engine.connect() as conn:
        result = conn.execute(
            insert(user_table),
            [
                {"name": "sandy", "fullname": "Sandy Cheeks"},
                {"name": "patrick", "fullname": "Patrick Star"},
            ],
        )
        conn.commit()
        print(result.inserted_primary_key_rows)
        print(f"{result!r}")


def core_insert_deeper(engine: Engine) -> None:
    from sqlalchemy import bindparam, select
    scalar_subq = (
        select(user_table.c.id)
        .where(user_table.c.name == bindparam("username"))
        .scalar_subquery()
    )

    with engine.connect() as conn:
        '''
        INSERT INTO address (user_id, email_address) VALUES (
            (SELECT user_account.id FROM user_account WHERE user_account.name = %s), %s)
        '''
        result = conn.execute(
            insert(address_table).values(user_id=scalar_subq),
            [
                {
                    "username": "spongebob",
                    "email_address": "spongebob@sqlalchemy.org",
                },
                {"username": "sandy", "email_address": "sandy@sqlalchemy.org"},
                {"username": "sandy", "email_address": "sandy@squirrelpower.org"},
            ],
        )
        conn.commit()


def insert_default(engine: Engine) -> None:
    print(insert(user_table).values().compile(engine)) # INSERT INTO user_account () VALUES ()


def insert_returning(engine: Engine) -> None:
    insert_stmt = insert(address_table).returning(
        address_table.c.id, address_table.c.email_address
    )
    print(insert_stmt)
    '''
    INSERT INTO address (id, user_id, email_address)
    VALUES (:id, :user_id, :email_address)
    RETURNING address.id, address.email_address
    '''


def insert_from_select(engine: Engine) -> None:
    select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
    insert_stmt = insert(address_table).from_select(
        ["user_id", "email_address"], select_stmt
    )
    print(insert_stmt.returning(address_table.c.id, address_table.c.email_address).compile(engine))
    '''
    INSERT INTO address (user_id, email_address)
        SELECT user_account.id, concat(user_account.name, %s) AS anon_1
        FROM user_account
    RETURNING address.id, address.email_address
    '''
    stmt = insert_stmt.returning(address_table.c.id, address_table.c.email_address)
    with engine.connect() as conn:
        result = conn.execute(insert_stmt)
        conn.commit()
        print(result.inserted_primary_key_rows)
        print(f"{result!r}")


def select_statement(engine: Engine) -> None:
    stmt = select(user_table).where(user_table.c.name == "spongebob")
    print(stmt.compile(engine))
    '''
    SELECT user_account.id, user_account.name, user_account.fullname
    FROM user_account
    WHERE user_account.name = %s
    '''
    with engine.connect() as conn:
        for row in conn.execute(stmt):
            print(row)


def select_from(engine: Engine) -> None:
    print(select(user_table))
    print(select(user_table.c.name, user_table.c.fullname))
    print(select(user_table.c["name", "fullname"]))
    with engine.connect() as conn:
        for row in conn.execute(select(user_table)):
            print(row)


def select_from_lable_sql_expressions(engine: Engine) -> None:
    from sqlalchemy import cast, func
    '''
    SELECT concat(%s, user_account.name) AS username
    FROM user_account
    ORDER BY user_account.name
    '''
    stmt = select(
        ("Username: " + user_table.c.name).label("username"),
    ).order_by(user_table.c.name)
    with engine.connect() as conn:
        for row in conn.execute(stmt):
            print(f"{row.username}")


def select_with_textual_column_expressions(engine: Engine) -> None:
    from sqlalchemy import text
    stmt = select(text("'some phrase'"), user_table.c.name).order_by(user_table.c.name)
    with engine.connect() as conn:
        print(conn.execute(stmt).all())

    from sqlalchemy import literal_column
    stmt = select(literal_column("'some phrase'").label("p"), user_table.c.name).order_by(
        user_table.c.name
    )
    with engine.connect() as conn:
        for row in conn.execute(stmt):
            print(f"{row.p}, {row.name}")


def select_where(engine: Engine) -> None:
    print('\n')
    print(user_table.c.name == "squidward")
    print('\n')
    print(address_table.c.user_id > 10)
    print('\n')
    print(select(user_table).where(user_table.c.name == "squidward"))

    print('\n')
    print(
        select(address_table.c.email_address)
        .where(user_table.c.name == "squidward")
        .where(address_table.c.user_id == user_table.c.id)
    )

    print('\n')
    print(
    select(address_table.c.email_address).where(
            user_table.c.name == "squidward",
            address_table.c.user_id == user_table.c.id,
        )
    )


def select_explicit_from_and_join(engine: Engine) -> None:
    print('\n')
    print(select(user_table.c.name))
    print('\n')
    print(select(user_table.c.name, address_table.c.email_address))

    print('\n')
    print(
        select(user_table.c.name, address_table.c.email_address).join_from(
            user_table, address_table
        )
    )

    print('\n')
    print(select(user_table.c.name, address_table.c.email_address).join(address_table))

    print('\n')
    print(select(address_table.c.email_address).select_from(user_table).join(address_table))
    '''
    SELECT address.email_address
    FROM user_account JOIN address ON user_account.id = address.user_id
    '''

    from sqlalchemy import func
    print('\n')
    print(select(func.count("*")).select_from(user_table))


def select_join_on(engine: Engine) -> None:
    print(
        select(address_table.c.email_address)
        .select_from(user_table)
        .join(address_table, user_table.c.id == address_table.c.user_id)
    )
    '''
    SELECT address.email_address
    FROM user_account JOIN address ON user_account.id = address.user_id
    '''

def select_outer_full_join(engine: Engine) -> None:
    print('\n')
    # There is also a method Select.outerjoin() that is equivalent to using .join(..., isouter=True).
    print(select(user_table).join(address_table, isouter=True))
    '''
    SELECT user_account.id, user_account.name, user_account.fullname
    FROM user_account LEFT OUTER JOIN address ON user_account.id = address.user_id
    '''

    print('\n')
    print(select(user_table).join(address_table, full=True))
    '''
    SELECT user_account.id, user_account.name, user_account.fullname
    FROM user_account FULL OUTER JOIN address ON user_account.id = address.user_id
    '''

def select_order_by(engine: Engine) -> None:
    print(select(user_table).order_by(user_table.c.name))
    '''
    SELECT user_account.id, user_account.name, user_account.fullname
    FROM user_account ORDER BY user_account.name
    '''

def select_aggr_with_group_by(engine: Engine) -> None:
    from sqlalchemy import func
    count_fn = func.count(user_table.c.id)
    print(count_fn)

    with engine.connect() as conn:
        '''
        SELECT user_account.name, count(address.id) AS count
        FROM user_account INNER JOIN address ON user_account.id = address.user_id
        GROUP BY user_account.name
        HAVING count(address.id) > %s
        '''
        result = conn.execute(
            select(user_table.c.name, func.count(address_table.c.id).label("count"))
            .join(address_table)
            .group_by(user_table.c.name)
            .having(func.count(address_table.c.id) > 1)
        )
        print(result.all())


def select_using_aliases(engine: Engine) -> None:
    user_alias_1 = user_table.alias()
    user_alias_2 = user_table.alias()
    print(
        select(user_alias_1.c.name, user_alias_2.c.name).join_from(
            user_alias_1, user_alias_2, user_alias_1.c.id > user_alias_2.c.id
        )
    )


def select_subquery(engine:Engine) -> None:
    from sqlalchemy import func
    subq = (
        select(func.count(address_table.c.id).label("count"), address_table.c.user_id)
        .group_by(address_table.c.user_id)
        .subquery()
    )
    print(subq)
    '''
    SELECT count(address.id) AS count, address.user_id
    FROM address GROUP BY address.user_id
    '''

    print('\n')
    print(select(subq.c.user_id, subq.c.count))
    '''
    SELECT anon_1.user_id, anon_1.count
    FROM (SELECT count(address.id) AS count, address.user_id AS user_id
    FROM address GROUP BY address.user_id) AS anon_1
    '''

    print('\n')
    stmt = select(user_table.c.name, user_table.c.fullname, subq.c.count).join_from(
        user_table, subq
    )
    print(stmt)
    '''
    SELECT user_account.name, user_account.fullname, anon_1.count
    FROM user_account JOIN (SELECT count(address.id) AS count, address.user_id AS user_id
    FROM address GROUP BY address.user_id) AS anon_1 ON user_account.id = anon_1.user_id
    '''


def select_cte(engine: Engine) -> None:
    # Common Table Expressions (CTEs)
    from sqlalchemy import func
    subq = (
        select(func.count(address_table.c.id).label("count"), address_table.c.user_id)
        .group_by(address_table.c.user_id)
        .cte()
    )

    stmt = select(user_table.c.name, user_table.c.fullname, subq.c.count).join_from(
        user_table, subq
    )

    print(stmt)
    '''
    WITH anon_1 AS
    (SELECT count(address.id) AS count, address.user_id AS user_id
    FROM address GROUP BY address.user_id)
    SELECT user_account.name, user_account.fullname, anon_1.count
    FROM user_account JOIN anon_1 ON user_account.id = anon_1.user_id
    '''


if __name__ == '__main__':
    load_env()
    test_db = os.getenv('LOCAL_TEST_DB')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)

    # insert data
    # core_insert(engine=engine)
    # core_insert_many(engine=engine)
    # core_insert_deeper(engine=engine)
    # insert_default(engine=engine)
    # insert_returning(engine=engine)
    # insert_from_select(engine=engine)

    # select data
    # select_statement(engine=engine)
    # select_from(engine=engine)
    # select_from_lable_sql_expressions(engine=engine)
    # select_with_textual_column_expressions(engine=engine)
    # select_where(engine=engine)
    # select_explicit_from_and_join(engine=engine)
    # select_join_on(engine=engine)
    # select_outer_full_join(engine=engine)
    # select_order_by(engine=engine)
    # select_aggr_with_group_by(engine=engine)
    # select_using_aliases(engine=engine)
    # select_subquery_and_cte(engine=engine)
    select_cte(engine=engine)
