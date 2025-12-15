from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from pydantic import validator


class BookBase(SQLModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1000, le=2025)
    genre: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    is_available: bool = Field(default=True)


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user_books: List["UserBook"] = Relationship(back_populates="book")

class BookCreate(BookBase):
    pass


class BookUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1000, le=2025)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    is_available: Optional[bool] = None


class BookResponse(BookBase):
    id: int
    created_at: datetime

class UserBase(SQLModel):
    username: str = Field(..., unique=True, index=True, max_length=50)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(..., unique=True, index=True, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_books: List["UserBook"] = Relationship(back_populates="user")

class UserBookBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    is_read: bool = Field(default=False)
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)


class UserBook(UserBookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    added_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="user_books")
    book: Book = Relationship(back_populates="user_books")


class UserBookCreate(SQLModel):
    book_id: int
    is_read: bool = False
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)


class UserBookUpdate(SQLModel):
    is_read: Optional[bool] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)


class UserBookResponse(UserBookBase):
    id: int
    added_at: datetime
    book: BookResponse


class UserBookDetail(UserBookResponse):
    user: User