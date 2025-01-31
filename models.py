from pydantic import BaseModel
from datetime import date
from typing import Optional
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, Date
from pydantic import BaseModel, Field, ValidationError, field_validator, EmailStr
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import ARRAY
import asyncio
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from .DB.config import DATABASE_URL

Base = declarative_base()

class AuthorRead(BaseModel):
    id: int
    name: str
    biography: Optional[str]
    date_of_birth: Optional[date]
    
    class Config:
        orm_mode = True
        
class AuthorCreate(BaseModel):
    name: str
    biography: Optional[str]
    date_of_birth: Optional[date]
    class Config:
        orm_mode = True

class AuthorUpdate(BaseModel):
    name: str
    biography: Optional[str]
    date_of_birth: Optional[date]

    class Config:
        orm_mode = True

class BookCreate(BaseModel):
    name: str
    description: Optional[str] = None
    date_of_publication: date
    genre: str
    count_in_stock: int
    author_ids: List[int] 

class BookUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    date_of_publication: Optional[date]
    genre: Optional[str]
    count_in_stock: Optional[int]

    class Config:
        orm_mode = True

class BookRead(BaseModel):
    id: int
    name: str
    description: str
    genre: str
    count_in_stock: int
    authors: List[AuthorRead]

    class Config:
        orm_mode = True


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
    date_of_birth = Column(Date, nullable=True)
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
    password = Column(String(255), nullable=False)
    roles = relationship("Role", secondary=user_role, back_populates="users")
    borrowed_books = relationship("UserGetBook", back_populates="user", cascade="all, delete-orphan")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    access_token: str
    token_type: str
    # role: str

    class Config:
        orm_mode = True

class UserGetBook(Base):
    __tablename__ = "user_get_book"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    date_begin = Column(Date, nullable=False)
    date_end_plan = Column(Date, nullable=True)  
    date_end_fact = Column(Date, nullable=True) 

    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_by_users")

class BorrowBookRequest(BaseModel):
    book_id: int
    date_begin: date
    date_end_plan: date

class BorrowBookId(BaseModel):
    id: int
    