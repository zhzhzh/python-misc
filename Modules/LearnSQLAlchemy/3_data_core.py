import os
import sys

from sqlalchemy import (Column, ForeignKey, Integer, MetaData, String, Table,
                        create_engine, delete, func, insert, select, update)
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


def scalar_and_correlated_subqueries(engine: Engine) -> None:
    # A scalar subquery is a subquery that returns exactly zero or one row and exactly one column.
    subq = (
        select(func.count(address_table.c.id))
        .where(user_table.c.id == address_table.c.user_id)
        .scalar_subquery()
    )
    print(subq)
    '''
    (SELECT count(address.id) AS count_1
    FROM address, user_account
    WHERE user_account.id = address.user_id)
    '''

    print('\n')
    print(subq == 5)
    '''
    (SELECT count(address.id) AS count_1
    FROM address, user_account
    WHERE user_account.id = address.user_id) = :param_1
    '''

    print('\n')
    stmt = select(user_table.c.name, subq.label("address_count"))
    print(stmt)
    '''
    SELECT user_account.name, (SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id) AS address_count
    FROM user_account
    '''

    print('\n')
    subq = (
        select(func.count(address_table.c.id))
        .where(user_table.c.id == address_table.c.user_id)
        .scalar_subquery()
        .correlate(user_table)
    )
    print(subq)
    print('\n')
    stmt = (
        select(
            user_table.c.name,
            address_table.c.email_address,
            subq.label("address_count"),
        )
        .join_from(user_table, address_table)
        .order_by(user_table.c.id, address_table.c.id)
    )
    print(stmt)
    '''
    SELECT user_account.name, address.email_address, (SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id) AS address_count
    FROM user_account JOIN address ON user_account.id = address.user_id
    ORDER BY user_account.id, address.id
    '''


def union_and_set_operations(engine: Engine) -> None:
    from sqlalchemy import union_all
    stmt1 = select(user_table).where(user_table.c.name == "sandy")
    stmt2 = select(user_table).where(user_table.c.name == "spongebob")
    u = union_all(stmt1, stmt2)
    '''
    SELECT user_account.id, user_account.name, user_account.fullname FROM user_account WHERE user_account.name = %s
    UNION ALL
    SELECT user_account.id, user_account.name, user_account.fullname FROM user_account WHERE user_account.name = %s
    '''
    with engine.connect() as conn:
        result = conn.execute(u)
        print(result.all())

    u_subq = u.subquery()
    stmt = (
        select(u_subq.c.name, address_table.c.email_address)
        .join_from(address_table, u_subq)
        .order_by(u_subq.c.name, address_table.c.email_address)
    )
    '''
    SELECT anon_1.name, address.email_address
    FROM address INNER JOIN (
        SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname FROM user_account WHERE user_account.name = %s
        UNION ALL
        SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname FROM user_account WHERE user_account.name = %s
        ) AS anon_1 ON anon_1.id = address.user_id
    ORDER BY anon_1.name, address.email_address
    '''
    with engine.connect() as conn:
        result = conn.execute(stmt)
        print(result.all())


def exists_subquery(engine: Engine) -> None:
    subq = (
        select(func.count(address_table.c.id))
        .where(user_table.c.id == address_table.c.user_id)
        .group_by(address_table.c.user_id)
        .having(func.count(address_table.c.id) > 1)
    ).exists()
    '''
    SELECT user_account.name
    FROM user_account
    WHERE EXISTS (
        SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id
        GROUP BY address.user_id
        HAVING count(address.id) > %s
    )
    '''
    with engine.connect() as conn:
        result = conn.execute(select(user_table.c.name).where(subq))
        print(result.all())

    subq = (
        select(address_table.c.id).where(user_table.c.id == address_table.c.user_id)
    ).exists()
    '''
    SELECT user_account.name
    FROM user_account
    WHERE NOT (
        EXISTS (
            SELECT address.id
            FROM address
            WHERE user_account.id = address.user_id
        )
    )
    '''
    with engine.connect() as conn:
        result = conn.execute(select(user_table.c.name).where(~subq))
        print(result.all())


def sql_functions(engine: Engine) -> None:
    print(select(func.count()).select_from(user_table))
    # SELECT count(*) AS count_1 FROM user_account

    print(select(func.lower("A String With Much UPPERCASE")))
    # SELECT lower(:lower_2) AS lower_1

    stmt = select(func.now())
    # SELECT now() AS now_1
    with engine.connect() as conn:
        result = conn.execute(stmt)
        print(result.all())

    print(select(func.some_crazy_function(user_table.c.name, 17)))
    # SELECT some_crazy_function(user_account.name, :some_crazy_function_2) AS some_crazy_function_1 FROM user_account

    from sqlalchemy.dialects import postgresql
    print(select(func.now()).compile(dialect=postgresql.dialect()))
    # SELECT now() AS now_1

    from sqlalchemy.dialects import oracle
    print(select(func.now()).compile(dialect=oracle.dialect()))
    # SELECT CURRENT_TIMESTAMP AS now_1 FROM DUAL


def sql_functions_and_return_types(engine: Engine) -> None:
    print(func.now().type) # DATETIME

    from sqlalchemy import JSON
    function_expr = func.json_object('{a, 1, b, "def", c, 3.5}', type_=JSON)
    print(function_expr) # json_object(:json_object_1)

    stmt = select(function_expr["def"])
    print(stmt) # SELECT json_object(:json_object_1)[:json_object_2] AS anon_1
    # with engine.connect() as conn:
    #     result = conn.execute(stmt)
    #     print(result.all())

    # Built-in Functions Have Pre-Configured Return Types
    m1 = func.max(Column("some_int", Integer))
    print(m1.type) # INTEGER

    m2 = func.max(Column("some_str", String))
    print(m2.type) # VARCHAR

    print(func.now().type) # DATETIME
    print(func.current_date().type) # DATE

    print(func.concat("x", "y").type) # VARCHAR

    print(func.upper("lowercase").type) # NULL

    print(select(func.upper("lowercase") + " suffix")) # SELECT upper(:upper_1) || :upper_2 AS anon_1

    print(func.count().type) # INTEGER

    print(func.json_object('{"a", "b"}').type) # NULL


def window_function(engine: Engine) -> None:
    stmt = (
        select(
            func.row_number().over(partition_by=user_table.c.name),
            user_table.c.name,
            address_table.c.email_address,
        )
        .select_from(user_table)
        .join(address_table)
    )
    '''
    SELECT
        row_number() OVER (PARTITION BY user_account.name) AS anon_1,
        user_account.name,
        address.email_address
    FROM user_account INNER JOIN address ON user_account.id = address.user_id
    '''
    with engine.connect() as conn:
        result = conn.execute(stmt)
        print(result.all())


    stmt = (
        select(
            func.count().over(order_by=user_table.c.name),
            user_table.c.name,
            address_table.c.email_address,
        )
        .select_from(user_table)
        .join(address_table)
    )
    '''
    SELECT
        count(*) OVER (ORDER BY user_account.name) AS anon_1,
        user_account.name,
        address.email_address
    FROM user_account INNER JOIN address ON user_account.id = address.user_id
    '''
    with engine.connect() as conn:
        result = conn.execute(stmt)
        print(result.all())


def select_filter(engine: Engine) -> None:
    stmt = (
        select(
            func.count(address_table.c.email_address).filter(user_table.c.name == "sandy"),
            func.count(address_table.c.email_address).filter(
                user_table.c.name == "spongebob"
            ),
        )
        .select_from(user_table)
        .join(address_table)
    )
    '''
    SELECT
        count(address.email_address) FILTER (WHERE user_account.name = %s) AS anon_1,
        count(address.email_address) FILTER (WHERE user_account.name = %s) AS anon_2
    FROM user_account INNER JOIN address ON user_account.id = address.user_id
    '''
    # not supported by MYSQL
    print(stmt)
    '''
    [SQL: SELECT anon_1.value
    FROM json_each(%s) AS anon_1
    WHERE anon_1.value IN (%s, %s)]
    [parameters: ('["one", "two", "three"]', 'two', 'three')]
    '''
    # with engine.connect() as conn:
    #     result = conn.execute(stmt)
    #     print(result.all())


def table_valued_functions(engine: Engine) -> None:
    onetwothree = func.json_each('["one", "two", "three"]').table_valued("value")
    stmt = select(onetwothree).where(onetwothree.c.value.in_(["two", "three"]))
    print(stmt)
    # not supported by MYSQL
    # with engine.connect() as conn:
    #     result = conn.execute(stmt)
    #     result.all()


def data_casts_and_type_coercion(engine: Engine) -> None:
    from sqlalchemy import cast
    stmt = select(cast(user_table.c.id, String))
    '''
    SELECT CAST(user_account.id AS CHAR) AS id
    FROM user_account
    '''
    with engine.connect() as conn:
        result = conn.execute(stmt)
        result.all()

    from sqlalchemy import JSON
    print(cast("{'a': 'b'}", JSON)["a"]) # CAST(:param_1 AS JSON)[:param_2]

    # type_coerce() - a Python-only “cast”
    import json

    from sqlalchemy import JSON, type_coerce
    from sqlalchemy.dialects import mysql
    s = select(type_coerce({"some_key": {"foo": "bar"}}, JSON)["some_key"])
    print(s.compile(dialect=mysql.dialect())) # SELECT JSON_EXTRACT(%s, %s) AS anon_1


def update_data(engine: Engine) -> None:
    stmt = (
        update(user_table)
        .where(user_table.c.name == "patrick")
        .values(fullname="Patrick the Star")
    )
    print(stmt)
    # UPDATE user_account SET fullname=:fullname WHERE user_account.name = :name_1

    stmt = update(user_table).values(fullname="Username: " + user_table.c.name)
    print(stmt)
    # UPDATE user_account SET fullname=(:name_1 || user_account.name)


def update_many(engine: Engine) -> None:
    from sqlalchemy import bindparam
    stmt = (
        update(user_table)
        .where(user_table.c.name == bindparam("oldname"))
        .values(name=bindparam("newname"))
    )
    # UPDATE user_account SET name=%s WHERE user_account.name = %s
    with engine.begin() as conn:
        conn.execute(
            stmt,
            [
                {"oldname": "jack", "newname": "ed"},
                {"oldname": "wendy", "newname": "mary"},
                {"oldname": "jim", "newname": "jake"},
            ],
        )


def correlated_updates(engine: Engine) -> None:
    scalar_subq = (
        select(address_table.c.email_address)
        .where(address_table.c.user_id == user_table.c.id)
        .order_by(address_table.c.id)
        .limit(1)
        .scalar_subquery()
    )
    update_stmt = update(user_table).values(fullname=scalar_subq)
    print(update_stmt)
    '''
    UPDATE user_account SET fullname=(
        SELECT address.email_address
        FROM address
        WHERE address.user_id = user_account.id
        ORDER BY address.id
        LIMIT :param_1
    )
    '''


def update_from(engine: Engine) -> None:
    update_stmt = (
        update(user_table)
        .where(user_table.c.id == address_table.c.user_id)
        .where(address_table.c.email_address == "patrick@aol.com")
        .values(fullname="Pat")
    )
    print(update_stmt)
    # UPDATE user_account SET fullname=:fullname FROM address WHERE user_account.id = address.user_id AND address.email_address = :email_address_1

    # MySQL, update multiple table
    update_stmt = (
        update(user_table)
        .where(user_table.c.id == address_table.c.user_id)
        .where(address_table.c.email_address == "patrick@aol.com")
        .values(
            {
                user_table.c.fullname: "Pat",
                address_table.c.email_address: "pat@aol.com",
            }
        )
    )
    from sqlalchemy.dialects import mysql
    print(update_stmt.compile(dialect=mysql.dialect()))
    # UPDATE user_account, address SET address.email_address=%s, user_account.fullname=%s WHERE user_account.id = address.user_id AND address.email_address = %s


def parameter_rrdered_updates(engine: Engine) -> None:
    # update_stmt = update(some_table).ordered_values(
    #     (some_table.c.y, 20), (some_table.c.x, some_table.c.y + 10)
    # )
    # print(update_stmt)
    # UPDATE some_table SET y=:y, x=(some_table.y + :y_1)
    pass


def delete_date(engine: Engine) -> None:
    stmt = delete(user_table).where(user_table.c.name == "patrick")
    print(stmt)
    # DELETE FROM user_account WHERE user_account.name = :name_1

    # multiple table delete
    delete_stmt = (
        delete(user_table)
        .where(user_table.c.id == address_table.c.user_id)
        .where(address_table.c.email_address == "patrick@aol.com")
    )
    from sqlalchemy.dialects import mysql
    print(delete_stmt.compile(dialect=mysql.dialect()))
    # DELETE FROM user_account USING user_account, address WHERE user_account.id = address.user_id AND address.email_address = %s


def get_affected_row_count_from_update_delete(engine: Engine) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            update(user_table)
            .values(fullname="Patrick McStar")
            .where(user_table.c.name == "patrick")
        )
        print(result.rowcount)


def using_returnning_with_update_delete(engine: Engine) -> None:
    update_stmt = (
        update(user_table)
        .where(user_table.c.name == "patrick")
        .values(fullname="Patrick the Star")
        .returning(user_table.c.id, user_table.c.name)
    )
    print(update_stmt)
    # UPDATE user_account SET fullname=:fullname WHERE user_account.name = :name_1 RETURNING user_account.id, user_account.name

    delete_stmt = (
        delete(user_table)
        .where(user_table.c.name == "patrick")
        .returning(user_table.c.id, user_table.c.name)
    )
    print(delete_stmt)
    # DELETE FROM user_account WHERE user_account.name = :name_1 RETURNING user_account.id, user_account.name


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
    # select_cte(engine=engine)
    # scalar_and_correlated_subqueries(engine=engine)
    # union_and_set_operations(engine=engine)
    # exists_subquery(engine=engine)
    # sql_functions(engine=engine)
    # sql_functions_and_return_types(engine=engine)
    # window_function(engine=engine)
    # select_filter(engine=engine)
    # table_valued_functions(engine=engine)
    # data_casts_and_type_coercion(engine=engine)

    # Update and Delete data
    # update_data(engine=engine)
    # update_many(engine=engine)
    # correlated_updates(engine=engine)
    # update_from(engine=engine)
    # delete_date(engine=engine)
    # get_affected_row_count_from_update_delete(engine=engine)
    using_returnning_with_update_delete(engine=engine)


