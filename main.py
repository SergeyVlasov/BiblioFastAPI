from pydantic import BaseModel
from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5444/test"
engine = create_async_engine(DATABASE_URL, echo=True)

class BookCreate(BaseModel):
    name: str
    description: Optional[str] = None
    date_of_publication: date
    genre: str
    count_in_stock: int

from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_of_publication = Column(Date, nullable=False)
    genre = Column(String(255), nullable=False)
    count_in_stock = Column(Integer, nullable=False, default=0)


from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

app = FastAPI()

# Database session dependency
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session

@app.post("/books/")
async def add_book(book: BookCreate, session: AsyncSession = Depends(get_session)):
    # Check if a book with the same name already exists
    query = select(Book).filter_by(name=book.name)
    result = await session.execute(query)
    existing_book = result.scalar_one_or_none()

    if existing_book:
        raise HTTPException(status_code=400, detail="A book with this name already exists.")

    # Create a new book instance
    new_book = Book(
        name=book.name,
        description=book.description,
        date_of_publication=book.date_of_publication,
        genre=book.genre,
        count_in_stock=book.count_in_stock,
    )

    # Add and commit the book to the database
    session.add(new_book)
    await session.commit()

    return {"message": "Book added successfully!", "book_id": new_book.id}
