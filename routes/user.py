from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from database.connection import get_session
from database.books import (
    get_all_books, get_book_by_id, search_books,
    add_book_to_user_library, get_user_library_with_details,
    get_user_book, update_user_book, remove_book_from_user_library,
    get_user_read_books, get_user_unread_books
)
from models.books import BookResponse, UserBookCreate, UserBookUpdate

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/books", response_model=List[BookResponse])
def get_all_books_user(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    return get_all_books(session, skip, limit)


@router.get("/books/{book_id}", response_model=BookResponse)
def get_book_user(
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


@router.get("/search/")
def search_books_user(
        title: str = None,
        author: str = None,
        genre: str = None,
        session: Session = Depends(get_session)
):
    return search_books(session, title, author, genre)


@router.get("/library")
def get_my_library(
        username: str,
        session: Session = Depends(get_session)
):
    return get_user_library_with_details(session, username)


@router.post("/library")
def add_to_my_library(
        user_book_create: UserBookCreate,
        username: str,
        session: Session = Depends(get_session)
):
    user_book = add_book_to_user_library(session, username, user_book_create)
    if not user_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {user_book_create.book_id} не найдена"
        )

    return user_book


@router.patch("/library/{book_id}/read")
def mark_book_as_read(
        book_id: int,
        username: str,
        session: Session = Depends(get_session)
):
    user_book_update = UserBookUpdate(is_read=True)
    user_book = update_user_book(session, username, book_id, user_book_update)

    if not user_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена в вашей библиотеке"
        )

    return user_book


@router.patch("/library/{book_id}/unread")
def mark_book_as_unread(
        book_id: int,
        username: str,
        session: Session = Depends(get_session)
):
    user_book_update = UserBookUpdate(is_read=False)
    user_book = update_user_book(session, username, book_id, user_book_update)

    if not user_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена в вашей библиотеке"
        )

    return user_book


@router.delete("/library/{book_id}")
def remove_from_my_library(
        book_id: int,
        username: str,
        session: Session = Depends(get_session)
):
    success = remove_book_from_user_library(session, username, book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книга с ID {book_id} не найдена в вашей библиотеке"
        )

    return {"message": "Книга удалена из библиотеки"}


@router.get("/library/read")
def get_my_read_books(
        username: str,
        session: Session = Depends(get_session)
):
    return get_user_read_books(session, username)


@router.get("/library/unread")
def get_my_unread_books(
        username: str,
        session: Session = Depends(get_session)
):
    return get_user_unread_books(session, username)