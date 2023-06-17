import os
import sys
from typing import List, Optional

from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            relationship)
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


def inserting_rows(engine: Engine) -> None:
    squidward = User(name="squidward", fullname="Squidward Tentacles")
    krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")

    print(squidward)
    # User(id=None, name='squidward', fullname='Squidward Tentacles')
    with Session(engine) as session:
    # session = Session(engine)
        session.add(squidward)
        session.add(krabs)
        print(session.new)
        # IdentitySet([
        #   User(id=None, name='squidward', fullname='Squidward Tentacles'),
        #   User(id=None, name='ehkrabs', fullname='Eugene H. Krabs')
        # ])
        session.flush()

        print(squidward.id)
        print(krabs.id)

        some_squidward = session.get(User, squidward.id)
        print(some_squidward)
        # User(id=45, name='squidward', fullname='Squidward Tentacles')
        print(f'some_squidward is squidward: {some_squidward is squidward}')

        session.commit()


def getting_object_by_primary_key(engine: Engine) -> None:
    with Session(engine) as session:
        some_squidward = session.get(User, 45)
        print(some_squidward)
        # User(id=45, name='squidward', fullname='Squidward Tentacles')


def updating_orm_objects(engine: Engine) -> None:
    with Session(engine) as session:
        sandy = session.execute(select(User).filter_by(name="sandy")).scalar_one()
        # User(id=5, name='sandy', fullname='Sandy Cheeks')
        print(sandy)
        sandy.fullname = "Sandy Squirrel"
        print(session.dirty)
        # IdentitySet([User(id=5, name='sandy', fullname='Sandy Squirrel')])
        print(f'sandy in session.dirty: {sandy in session.dirty}')

        # When the Session next emits a flush, an UPDATE will be emitted that updates this value in the database.
        # As mentioned previously, a flush occurs automatically before we emit any SELECT, using a behavior known as autoflush.
        sandy_fullname = session.execute(select(User.fullname).where(User.id == 5)).scalar_one()
        print(sandy_fullname)

        print(f'sandy in session.dirty: {sandy in session.dirty}')

        # no actual DB change since not commited


def deleting_orm_objects(engine: Engine) -> None:
    with Session(engine) as session:
        patrick = session.get(User, 6)
        print(patrick)
        # User(id=6, name='patrick', fullname='Patrick McStar')
        print(f'patrick in session: {patrick in session}')

        session.delete(patrick)
        session.execute(select(User).where(User.name == "patrick")).first()

        print(f'patrick in session: {patrick in session}')

        # no actual DB change since not commited


def rolling_back(engine: Engine) -> None:
    with Session(engine) as session:
        sandy = session.execute(select(User).filter_by(name="sandy")).scalar_one()
        # User(id=5, name='sandy', fullname='Sandy Cheeks')
        print(sandy)
        sandy.fullname = "Sandy Squirrel"
        print(session.dirty)
        # IdentitySet([User(id=5, name='sandy', fullname='Sandy Squirrel')])
        print(f'sandy in session.dirty: {sandy in session.dirty}')

        # When the Session next emits a flush, an UPDATE will be emitted that updates this value in the database.
        # As mentioned previously, a flush occurs automatically before we emit any SELECT, using a behavior known as autoflush.
        sandy_fullname = session.execute(select(User.fullname).where(User.id == 5)).scalar_one()
        print(sandy_fullname)

        print(f'sandy in session.dirty: {sandy in session.dirty}')

        session.rollback()
        print(f'sandy.__dict__: {sandy.__dict__}')
        # sandy.__dict__: {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x102649910>}
        print(f'sandy.fullname: {sandy.fullname}')
        print(f'sandy.__dict__: {sandy.__dict__}')
        # {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x102649910>, 'id': 5, 'name': 'sandy', 'fullname': 'Sandy Cheeks'}


        patrick = session.get(User, 6)
        print(patrick)
        # User(id=6, name='patrick', fullname='Patrick McStar')
        print(f'patrick in session: {patrick in session}')

        session.delete(patrick)
        session.execute(select(User).where(User.name == "patrick")).first()

        print(f'patrick in session: {patrick in session}')
        session.rollback()
        print(f'patrick in session: {patrick in session}')



if __name__ == '__main__':
    load_env()
    test_db = os.getenv('LOCAL_TEST_DB')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)

    # inserting_rows(engine=engine)
    # getting_object_by_primary_key(engine=engine)
    # updating_orm_objects(engine=engine)
    # deleting_orm_objects(engine=engine)
    rolling_back(engine=engine)
