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
    fullname: Mapped[Optional[str]]

    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped["User"] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


def emit_create_table_ddl(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def create_onjects_and_persist(engine: Engine) -> None:
    with Session(engine) as session:
        spongebob = User(
            name="spongebob",
            fullname="Spongebob Squarepants",
            addresses=[Address(email_address="spongebob@sqlalchemy.org")],
        )
        sandy = User(
            name="sandy",
            fullname="Sandy Cheeks",
            addresses=[
                Address(email_address="sandy@sqlalchemy.org"),
                Address(email_address="sandy@squirrelpower.org"),
            ],
        )
        patrick = User(name="patrick", fullname="Patrick Star")
        session.add_all([spongebob, sandy, patrick])
        session.commit()


def simple_select(engine: Engine) -> None:
    with Session(engine) as session:
        stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))
        for user in session.scalars(stmt):
            print(user)


def select_with_join(engine: Engine) -> None:
    with Session(engine) as session:
        stmt = (
            select(Address)
            .join(Address.user)
            .where(User.name == "sandy")
            .where(Address.email_address == "sandy@sqlalchemy.org")
        )
        sandy_address = session.scalars(stmt).one()
        print(sandy_address)


def make_changes(engine: Engine) -> None:
    with Session(engine) as session:
        stmt = (
            select(Address)
            .join(Address.user)
            .where(User.name == "sandy")
            .where(Address.email_address == "sandy@sqlalchemy.org")
        )
        sandy_address = session.scalars(stmt).one()
        print(sandy_address)

        stmt = select(User).where(User.name == "patrick")
        patrick = session.scalars(stmt).one()
        patrick.addresses.append(Address(email_address="patrickstar@sqlalchemy.org"))
        sandy_address.email_address = "sandy_cheeks@sqlalchemy.org"

        session.commit()


def some_deletes(engine: Engine) -> None:
    with Session(engine) as session:
        stmt = (
            select(Address)
            .join(Address.user)
            .where(User.name == "sandy")
            .where(Address.email_address == "sandy_cheeks@sqlalchemy.org")
        )
        sandy_address = session.scalars(stmt).one()
        print(sandy_address)

        sandy = session.get(User, 5)
        print(sandy)
        sandy.addresses.remove(sandy_address) # type: ignore

        session.flush()
        # DELETE FROM address WHERE address.id = %s

        stmt = select(User).where(User.name == "patrick")
        patrick = session.scalars(stmt).one()
        session.delete(patrick)
        session.flush()


if __name__ == '__main__':
    load_env()
    test_db = os.getenv('LOCAL_TEST_DB')
    if test_db is None:
        sys.exit(1)

    engine = create_engine(test_db, echo=True)

    # emit_create_table_ddl(engine=engine)
    # create_onjects_and_persist(engine=engine)
    # simple_select(engine=engine)
    # select_with_join(engine=engine)
    # make_changes(engine=engine)
    some_deletes(engine=engine)

