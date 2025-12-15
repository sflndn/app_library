from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from database.connection import get_session
from database.books import (
    create_book, get_all_books, get_book_by_id,
    update_book, delete_book, search_books
)
from models.books import BookCreate, BookUpdate, BookResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/books", response_model=List[BookResponse])
def get_all_books_admin(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    return get_all_books(session, skip, limit)


@router.get("/books/{book_id}", response_model=BookResponse)
def get_book_admin(
    book_id: int,
    session: Session = Depends(get_session)
):
    book = get_book_by_id(session, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )
    return book


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_new_book(
    book_create: BookCreate,
    session: Session = Depends(get_session)
):
    return create_book(session, book_create)


@router.put("/books/{book_id}", response_model=BookResponse)
def update_book_admin(
    book_id: int,
    book_update: BookUpdate,
    session: Session = Depends(get_session)
):
    book = update_book(session, book_id, book_update)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )
    return book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_admin(
    book_id: int,
    session: Session = Depends(get_session)
):
    success = delete_book(session, book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена"
        )


@router.get("/books/search/")
def search_books_admin(
    title: str = None,
    author: str = None,
    genre: str = None,
    session: Session = Depends(get_session)
):
    return search_books(session, title, author, genre)