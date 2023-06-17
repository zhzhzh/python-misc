import os
import sys
from typing import List, Optional

from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            relationship, selectinload)
from Utils.env_util import load_env


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]] = mapped_column(String(60))

    # addresses: Mapped[List["Address"]] = relationship(back_populates="user") # defaulat lazy='select'
    # addresses: Mapped[List["Address"]] = relationship(back_populates="user", lazy="selectin")
    addresses: Mapped[List["Address"]] = relationship(back_populates="user", lazy="raise_on_sql")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id = mapped_column(ForeignKey("user_account.id"))

    # user: Mapped[User] = relationship(back_populates="addresses")
    user: Mapped[User] = relationship(back_populates="addresses", lazy="raise_on_sql")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


def persisting_and_loading_relationships(engine: Engine) -> None:
    with Session(engine) as session:
        u1 = User(name="pkrabs", fullname="Pearl Krabs")
        print(f'u1.addresses: {u1.addresses}')
        # u1.addresses: []

        a1 = Address(email_address="pearl.krabs@gmail.com")
        u1.addresses.append(a1)
        print(f'u1.addresses: {u1.addresses}')
        # u1.addresses: [Address(id=None, email_address='pearl.krabs@gmail.com')]

        print(f'a1.user: {a1.user}')
        # User(id=None, name='pkrabs', fullname='Pearl Krabs')

        a2 = Address(email_address="pearl@aol.com", user=u1)
        print(f'u1.addresses: {u1.addresses}')
        # u1.addresses: [Address(id=None, email_address='pearl.krabs@gmail.com'), Address(id=None, email_address='pearl@aol.com')]

        # equivalent effect as a2 = Address(user=u1)
        # a2.user = u1

        session.add(u1)
        print(f'u1 in session: {u1 in session}')
        print(f'a1 in session: {a1 in session}')
        print(f'a2 in session: {a2 in session}')
        print(f'u1.id: {u1.id}')
        print(f'a1.user_id: {a1.user_id}')

        session.commit()
        print(f'u1.id: {u1.id}')
        # u1.id: 54
        print(f'u1.addresses: {u1.addresses}')
        # u1.addresses: [Address(id=10, email_address='pearl.krabs@gmail.com'), Address(id=11, email_address='pearl@aol.com')]
        print(f'a1: {a1}')
        # a1: Address(id=10, email_address='pearl.krabs@gmail.com')
        print(f'a2: {a2}')
        # a2: Address(id=11, email_address='pearl@aol.com')


def using_relationships_in_query(engine: Engine) -> None:
    # using relationships to join
    print(select(Address.email_address).select_from(User).join(User.addresses)) # this is join with relationship()
    '''
    SELECT address.email_address
    FROM user_account JOIN address ON user_account.id = address.user_id
    '''

    print(select(Address.email_address).join_from(User, Address)) # this is due to the ForeignKeyConstraint


def loader_strategies(engine: Engine) -> None:
    # Lazy loading is one of the most famous ORM patterns, and is also the one that is most controversial.
    # Above all, the first step in using ORM lazy loading effectively is to test the application, turn on SQL echoing, and watch the SQL that is emitted.
    with Session(engine) as session:
        # selectinload
        for user_obj in session.execute(
            select(User).options(selectinload(User.addresses))
        ).scalars():
            user_obj.addresses  # access addresses collection already loaded
        '''
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account

        SELECT address.user_id AS address_user_id, address.id AS address_id, address.email_address AS address_email_address
        FROM address
        WHERE address.user_id IN (%s, %s, %s, %s, %s, %s)
        '''

    # with Session(engine) as session:
    #     # lazy load when select, the N plus one problem
    #     for user_obj in session.execute(
    #         select(User)
    #     ).scalars():
    #         user_obj.addresses  # access addresses collection already loaded


def selectin_load(engine: Engine) -> None:
    # The most useful loader in modern SQLAlchemy is the selectinload() loader option.
    # This option solves the most common form of the “N plus one” problem which is that of a set of objects that refer to related collections.
    from sqlalchemy.orm import selectinload
    with Session(engine) as session:
        stmt = select(User).options(selectinload(User.addresses)).order_by(User.id)
        for row in session.execute(stmt):
            print(
                f"{row.User.name}  ({', '.join(a.email_address for a in row.User.addresses)})"
            )
        '''
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.id

        SELECT address.user_id AS address_user_id, address.id AS address_id, address.email_address AS address_email_address
        FROM address
        WHERE address.user_id IN (%s, %s, %s, %s, %s, %s)
        '''


def joined_load(engine: Engine) -> None:
    # The joinedload() eager load strategy is the oldest eager loader in SQLAlchemy
    # The joinedload() strategy is best suited towards loading related many-to-one objects
    from sqlalchemy.orm import joinedload
    with Session(engine) as session:
        stmt = (
            select(Address)
            .options(joinedload(Address.user, innerjoin=True))
            .order_by(Address.id)
        )
        for row in session.execute(stmt):
            print(f"{row.Address.email_address} {row.Address.user.name}")
            # spongebob@sqlalchemy.org spongebob
            # sandy@sqlalchemy.org sandy
            # sandy@squirrelpower.org sandy
            # spongebob@aol.com spongebob
            # sandy@aol.com sandy
            # patrick@aol.com patrick
            # pearl.krabs@gmail.com pkrabs
            # pearl@aol.com pkrabs
        '''
        SELECT
            address.id, address.email_address, address.user_id,
            user_account_1.id AS id_1, user_account_1.name, user_account_1.fullname
        FROM address INNER JOIN user_account AS user_account_1 ON user_account_1.id = address.user_id
        ORDER BY address.id
        '''


def explicit_join_and_eager_load(engine: Engine) -> None:
    from sqlalchemy.orm import contains_eager, joinedload
    with Session(engine) as session:
        stmt = (
            select(Address)
            .join(Address.user)
            .where(User.name == "pkrabs")
            .options(contains_eager(Address.user))
            .order_by(Address.id)
        )
        for row in session.execute(stmt):
            print(f"{row.Address.email_address} {row.Address.user.name}")
            # pearl.krabs@gmail.com pkrabs
            # pearl@aol.com pkrabs
        '''
        SELECT
            user_account.id, user_account.name, user_account.fullname,
            address.id AS id_1, address.email_address, address.user_id
        FROM address INNER JOIN user_account ON user_account.id = address.user_id
        WHERE user_account.name = %s
        ORDER BY address.id
        '''
        stmt = (
            select(Address)
            .join(Address.user)
            .where(User.name == "pkrabs")
            .options(joinedload(Address.user))
            .order_by(Address.id)
        )
        print(stmt)  # SELECT has a JOIN and LEFT OUTER JOIN unnecessarily
        '''
        SELECT
            address.id, address.email_address, address.user_id,
            user_account_1.id AS id_1, user_account_1.name, user_account_1.fullname
        FROM address JOIN user_account ON user_account.id = address.user_id
            LEFT OUTER JOIN user_account AS user_account_1 ON user_account_1.id = address.user_id
        WHERE user_account.name = :name_1
        ORDER BY address.id
        '''


def raise_load(engine: Engine) -> None:
    with Session(engine) as session:
        u1 = session.execute(select(User)).scalars().first()
        # print(u1.addresses)
        # sqlalchemy.exc.InvalidRequestError: 'User.addresses' is not available due to lazy='raise_on_sql'

        u1 = (
            session.execute(select(User).options(selectinload(User.addresses)))
            .scalars()
            .first()
        )
        print(u1.addresses) # type: ignore
        # [Address(id=1, email_address='spongebob@sqlalchemy.org'), Address(id=7, email_address='spongebob@aol.com')]


if __name__ == '__main__':
    load_env()
    test_db = os.getenv('LOCAL_TEST_DB')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)

    # persisting_and_loading_relationships(engine=engine)
    # using_relationships_in_query(engine=engine)
    # loader_strategies(engine=engine)
    # selectin_load(engine=engine)
    # joined_load(engine=engine)
    # explicit_join_and_eager_load(engine=engine)
    raise_load(engine=engine)
