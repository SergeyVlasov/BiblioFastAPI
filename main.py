from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5444/test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
async def get_data():
    async with async_session() as session:
        async with session.begin():
            # Your query logic here
            pass



app = FastAPI()

books = [
    {
        "id": 1,
        "name": "book1",
        "author": "author1"
    },
    {
        "id": 2,
        "name": "book2",
        "author": "author2"
    }
]


@app.get("/books")
def read_books():
    return books


@app.get("/books/{book_id}")
def read_books(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="book no find")


class Book(BaseModel):
    title: str
    author: str

class Author(BaseModel):
    name: str = Field(..., description="Name field that accepts only letters.")
    bio: str = Field(..., max_length=1000)
    born: str

    @field_validator('name')
    def only_letters(cls, value):
        if not value.isalpha():
            raise ValueError('The field must only contain only letters.')
        return value

@app.post("/books")
def create_books(new_book: Book):
   books.append({
       "id": len(books) + 1,
       "title": new_book.title,
       "author": new_book.author,
   })
   return {"success": True}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)