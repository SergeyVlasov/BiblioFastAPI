DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5444/test"

from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import ARRAY
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()

book_author = Table(
    "book_author",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
)

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    biography = Column(Text, nullable=True)
    date_of_burth = Column(Date, nullable=True)
    books = relationship("Book", secondary=book_author, back_populates="authors")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    date_of_publication = Column(Date, nullable=False)
    genre = Column(String(255), nullable=False)
    count_in_stock = Column(Integer, nullable=False, default=0)

    authors = relationship("Author", secondary=book_author, back_populates="books")
    borrowed_by_users = relationship("UserGetBook", back_populates="book", cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    users = relationship("User", secondary=user_role, back_populates="roles")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    roles = relationship("Role", secondary=user_role, back_populates="users")
    borrowed_books = relationship("UserGetBook", back_populates="user", cascade="all, delete-orphan")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")

class UserGetBook(Base):
    __tablename__ = "user_get_book"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    date_begin = Column(Date, nullable=False) 
    date_end = Column(Date, nullable=True)  

    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_by_users")

asyncio.run(create_tables())