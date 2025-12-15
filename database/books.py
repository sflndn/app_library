from sqlmodel import Session, select
from typing import Optional, List
from models.books import Book, BookCreate, BookUpdate
from datetime import datetime

user_libraries = {}

def create_book(session: Session, book_create: BookCreate) -> Book:
    book = Book(**book_create.dict())

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


def get_book_by_id(session: Session, book_id: int) -> Optional[Book]:
    return session.get(Book, book_id)


def get_all_books(session: Session, skip: int = 0, limit: int = 100) -> List[Book]:
    statement = select(Book).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_book(session: Session, book_id: int, book_update: BookUpdate) -> Optional[Book]:
    book = get_book_by_id(session, book_id)
    if not book:
        return None

    update_data = book_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(book, key, value)

    book.updated_at = datetime.utcnow()

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


def delete_book(session: Session, book_id: int) -> bool:
    book = get_book_by_id(session, book_id)
    if not book:
        return False

    session.delete(book)
    session.commit()

    return True


def search_books(session: Session, title: Optional[str] = None,
                 author: Optional[str] = None, genre: Optional[str] = None) -> List[Book]:
    statement = select(Book)

    if title:
        statement = statement.where(Book.title.ilike(f"%{title}%"))
    if author:
        statement = statement.where(Book.author.ilike(f"%{author}%"))
    if genre:
        statement = statement.where(Book.genre.ilike(f"%{genre}%"))

    return session.exec(statement).all()


def get_user_library(session: Session, user_id: str) -> List[dict]:
    if user_id not in user_libraries:
        user_libraries[user_id] = []

    library_with_details = []
    for user_book in user_libraries[user_id]:
        book = get_book_by_id(session, user_book["book_id"])
        if book:
            book_dict = book.dict()
            book_dict.update(user_book)
            library_with_details.append(book_dict)

    return library_with_details


def add_book_to_user_library(session: Session, user_id: str, book_id: int) -> Optional[dict]:
    book = get_book_by_id(session, book_id)
    if not book:
        return None

    if user_id not in user_libraries:
        user_libraries[user_id] = []

    for book_entry in user_libraries[user_id]:
        if book_entry["book_id"] == book_id:
            return book_entry

    user_book = {
        "book_id": book_id,
        "is_read": False,
        "rating": None,
        "notes": None
    }

    user_libraries[user_id].append(user_book)

    book_dict = book.dict()
    book_dict.update(user_book)
    return book_dict


def get_user_book(session: Session, user_id: str, book_id: int) -> Optional[dict]:
    if user_id not in user_libraries:
        return None

    for book_entry in user_libraries[user_id]:
        if book_entry["book_id"] == book_id:
            book = get_book_by_id(session, book_id)
            if book:
                book_dict = book.dict()
                book_dict.update(book_entry)
                return book_dict

    return None


def update_user_book(session: Session, user_id: str, book_id: int, is_read: Optional[bool] = None,
                     rating: Optional[int] = None, notes: Optional[str] = None) -> Optional[dict]:
    if user_id not in user_libraries:
        return None

    for book_entry in user_libraries[user_id]:
        if book_entry["book_id"] == book_id:
            if is_read is not None:
                book_entry["is_read"] = is_read
            if rating is not None:
                book_entry["rating"] = rating
            if notes is not None:
                book_entry["notes"] = notes

            book = get_book_by_id(session, book_id)
            if book:
                book_dict = book.dict()
                book_dict.update(book_entry)
                return book_dict

    return None


def remove_book_from_user_library(user_id: str, book_id: int) -> bool:
    if user_id not in user_libraries:
        return False

    for i, book_entry in enumerate(user_libraries[user_id]):
        if book_entry["book_id"] == book_id:
            user_libraries[user_id].pop(i)
            return True

    return False


def get_user_read_books(session: Session, user_id: str) -> List[dict]:
    if user_id not in user_libraries:
        return []

    read_books = []
    for book_entry in user_libraries[user_id]:
        if book_entry.get("is_read", False):
            book = get_book_by_id(session, book_entry["book_id"])
            if book:
                book_dict = book.dict()
                book_dict.update(book_entry)
                read_books.append(book_dict)

    return read_books


def get_user_unread_books(session: Session, user_id: str) -> List[dict]:
    if user_id not in user_libraries:
        return []

    unread_books = []
    for book_entry in user_libraries[user_id]:
        if not book_entry.get("is_read", False):
            book = get_book_by_id(session, book_entry["book_id"])
            if book:
                book_dict = book.dict()
                book_dict.update(book_entry)
                unread_books.append(book_dict)

    return unread_books