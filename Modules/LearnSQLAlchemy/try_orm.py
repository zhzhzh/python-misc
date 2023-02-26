import os
import sys
from typing import List, Optional

from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, aliased,
                            mapped_column, relationship)
from Utils.env_util import load_env


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]] = mapped_column(String(60))

    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id = mapped_column(ForeignKey("user_account.id"))

    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


def select_statement(engine: Engine) -> None:
    stmt = select(User).where(User.name == "spongebob")
    with Session(engine) as session:
        for row in session.execute(stmt):
            print(row)


def select_from(engine: Engine) -> None:
    print(select(User))
    with Session(engine) as session:
        row = session.execute(select(User)).first()
        print(row)
        if row is not None:
            print(f'row len: {len(row)}, {row[0]}')

        # highly recommended convenience method:
        user = session.scalars(select(User)).first()
        print(user)

        row = session.execute(select(User.name, User.fullname)).first()
        print(row)

        all = session.execute(
            select(User.name, Address).where(User.id == Address.user_id).order_by(Address.id)
        ).all()
        print(all)


def select_where(engine: Engine) -> None:
    print('\n')
    from sqlalchemy import and_, or_
    print(
        select(Address.email_address).where(
            and_(
                or_(User.name == "squidward", User.name == "sandy"),
                Address.user_id == User.id,
            )
        )
    )

    print('\n')
    print(select(User).filter_by(name="spongebob", fullname="Spongebob Squarepants"))


def select_order_by(engine: Engine) -> None:
    print(select(User).order_by(User.fullname.desc()))
    '''
    SELECT user_account.id, user_account.name, user_account.fullname
    FROM user_account ORDER BY user_account.fullname DESC
    '''


def select_aggr_with_group_by(engine: Engine) -> None:
    from sqlalchemy import func

    # The HAVING clause is then used in a similar manner as the WHERE clause, except that it filters out rows based on aggregated values rather than direct row contents.
    with engine.connect() as conn:
        result = conn.execute(
            select(User.name, func.count(Address.id).label("count"))
            .join(Address)
            .group_by(User.name)
            .having(func.count(Address.id) > 1)
        )
        print(result.all())


def select_aggr_with_group_by_a_label(engine: Engine) -> None:
    from sqlalchemy import desc, func
    stmt = (
        select(Address.user_id, func.count(Address.id).label("num_addresses"))
        .group_by("user_id")
        .order_by("user_id", desc("num_addresses"))
    )
    print(stmt)
    '''
    SELECT address.user_id, count(address.id) AS num_addresses
    FROM address
    GROUP BY address.user_id
    ORDER BY address.user_id, num_addresses DESC
    '''


def select_using_aliases(engine: Engine) -> None:
    from sqlalchemy.orm import aliased
    address_alias_1 = aliased(Address)
    address_alias_2 = aliased(Address)
    print(
        select(User)
        .join_from(User, address_alias_1)
        .where(address_alias_1.email_address == "patrick@aol.com")
        .join_from(User, address_alias_2)
        .where(address_alias_2.email_address == "patrick@gmail.com")
    )
    '''
    SELECT user_account.id, user_account.name, user_account.fullname
    FROM user_account JOIN address AS address_1 ON user_account.id = address_1.user_id
        JOIN address AS address_2 ON user_account.id = address_2.user_id
    WHERE address_1.email_address = :email_address_1 AND address_2.email_address = :email_address_2
    '''


def select_subquery(engine: Engine) -> None:
    subq = select(Address).where(~Address.email_address.like("%@aol.com")).subquery()
    address_subq = aliased(Address, subq)
    stmt = (
        select(User, address_subq)
        .join_from(User, address_subq)
        .order_by(User.id, address_subq.id)
    )
    '''
    SELECT user_account.id, user_account.name, user_account.fullname, anon_1.id AS id_1, anon_1.email_address, anon_1.user_id
    FROM user_account INNER JOIN (
        SELECT address.id AS id, address.email_address AS email_address, address.user_id AS user_id
        FROM address
        WHERE address.email_address NOT LIKE %s
    ) AS anon_1 ON user_account.id = anon_1.user_id
    ORDER BY user_account.id, anon_1.id
    '''
    with Session(engine) as session:
        for user, address in session.execute(stmt):
            print(f"{user} {address}")


def select_cte(engine: Engine) -> None:
    cte_obj = select(Address).where(~Address.email_address.like("%@aol.com")).cte()
    address_cte = aliased(Address, cte_obj) # type: ignore
    stmt = (
        select(User, address_cte)
        .join_from(User, address_cte)
        .order_by(User.id, address_cte.id)
    )
    '''
    WITH anon_1 AS
    (
        SELECT address.id AS id, address.email_address AS email_address, address.user_id AS user_id
        FROM address
        WHERE address.email_address NOT LIKE %s
    )

    SELECT user_account.id, user_account.name, user_account.fullname, anon_1.id AS id_1, anon_1.email_address, anon_1.user_id
    FROM user_account INNER JOIN anon_1 ON user_account.id = anon_1.user_id
    ORDER BY user_account.id, anon_1.id
    '''
    with Session(engine) as session:
        for user, address in session.execute(stmt):
            print(f"{user} {address}")


if __name__ == '__main__':
    load_env()
    test_db = os.getenv('LOCAL_TEST_DB')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)

    # print(Base.metadata)
    # print(Base.registry)
    # sandy = User(name="sandy", fullname="Sandy Cheeks")
    # Base.metadata.create_all(engine)

    # select data
    # select_statement(engine=engine)
    # select_from(engine=engine)
    # select_where(engine=engine)
    # select_order_by(engine=engine)
    # select_aggr_with_group_by(engine=engine)
    # select_aggr_with_group_by_a_label(engine=engine)
    # select_using_aliases(engine=engine)
    # select_subquery(engine=engine)
    select_cte(engine=engine)

