from .models import Book, BookCreate, User, BookUpdate, BookRead, Author, AuthorRead, AuthorCreate
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from .security.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .security.password import verify_password
from .security.jwtgen import create_access_token
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload 
from .DB.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)

app = FastAPI()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session

@app.post("/books/", response_model=BookRead, status_code=201)
async def add_book(book: BookCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Author).filter(Author.id.in_(book.author_ids)))
    db_authors = result.scalars().all()
    if not db_authors or len(db_authors) != len(book.author_ids):
        raise HTTPException(status_code=400, detail="One or more authors not found")
    new_book = Book(
        name=book.name,
        description=book.description,
        date_of_publication=book.date_of_publication,
        genre=book.genre,
        count_in_stock=book.count_in_stock,
    )
    new_book.authors = db_authors
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)

    return new_book

@app.delete("/books/{book_id}", status_code=204)
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Book).filter(Book.id == book_id))
    db_book = result.scalars().first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    await session.delete(db_book)
    await session.commit()
    return {"detail": "Book deleted successfully"}


@app.put("/books/{book_id}", response_model=BookUpdate)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Book).filter(Book.id == book_id))
    db_book = result.scalars().first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_data.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book

@app.get("/books/{book_id}", response_model=BookRead)
async def get_book_by_id(book_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Book)
        .where(Book.id == book_id)
        .options(joinedload(Book.authors))
    )
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.get("/books/", response_model=list[BookRead])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Book).options(joinedload(Book.authors))
    )
    books = result.unique().scalars().all() 
    return books

@app.get("/books/description/{description}", response_model=list[BookRead])
async def get_book_by_description(
    book_description: str, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Book)
        .where(Book.description.ilike(f"%{book_description}%"))  
        .options(joinedload(Book.authors))
    )
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.get("/books/author/{author_name}", response_model=list[BookRead])
async def get_books_by_author(author_name: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Author).filter(Author.name.ilike(f"%{author_name}%")))
    db_author = result.scalars().first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    books = db_author.books
    if not books:
        raise HTTPException(status_code=404, detail="No books found for this author")
    return books

@app.get("/books/name/{book_name}", response_model=list[BookRead])
async def get_book_by_name(book_name: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Book)
        .where(Book.name == book_name)
        .options(joinedload(Book.authors))
    )
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book    

@app.post("/authors/", response_model=AuthorRead, status_code=201)
async def add_author(author: AuthorCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Author).filter(Author.name == author.name))
    existing_author = result.scalars().first()
    if existing_author:
        raise HTTPException(status_code=400, detail="Author already exists")
    new_author = Author(name=author.name)
    session.add(new_author)
    await session.commit()
    await session.refresh(new_author)
    return new_author

@app.get("/authors/", response_model=list[AuthorRead])
async def get_all_authors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Author))
    authors = result.scalars().all()
    return authors

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}