from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Customerp(Base):
    __tablename__ = "customersp"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Customerpp(Base):
    __tablename__ = "customerspp"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class Customerppp(Base):
    __tablename__ = "customersppp"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
