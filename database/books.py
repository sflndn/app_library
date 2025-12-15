from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime
from models.books import Book, BookCreate, BookUpdate, User, UserBook, UserBookCreate, UserBookUpdate


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


def get_or_create_user(session: Session, username: str) -> User:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        user = User(username=username)
        session.add(user)
        session.commit()
        session.refresh(user)

    return user


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def add_book_to_user_library(session: Session, username: str, user_book_create: UserBookCreate) -> Optional[UserBook]:
    user = get_or_create_user(session, username)

    book = get_book_by_id(session, user_book_create.book_id)
    if not book:
        return None

    statement = select(UserBook).where(
        (UserBook.user_id == user.id) &
        (UserBook.book_id == user_book_create.book_id)
    )
    existing = session.exec(statement).first()

    if existing:
        return existing

    user_book = UserBook(
        user_id=user.id,
        **user_book_create.dict()
    )

    session.add(user_book)
    session.commit()
    session.refresh(user_book)

    return user_book


def get_user_library(session: Session, username: str) -> List[UserBook]:
    user = get_user_by_username(session, username)
    if not user:
        return []

    statement = select(UserBook).where(UserBook.user_id == user.id)
    user_books = session.exec(statement).all()

    return user_books


def get_user_book(session: Session, username: str, book_id: int) -> Optional[UserBook]:
    user = get_user_by_username(session, username)
    if not user:
        return None

    statement = select(UserBook).where(
        (UserBook.user_id == user.id) &
        (UserBook.book_id == book_id)
    )
    return session.exec(statement).first()


def update_user_book(session: Session, username: str, book_id: int,
                     user_book_update: UserBookUpdate) -> Optional[UserBook]:
    user_book = get_user_book(session, username, book_id)
    if not user_book:
        return None

    update_data = user_book_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user_book, key, value)

    session.add(user_book)
    session.commit()
    session.refresh(user_book)

    return user_book


def remove_book_from_user_library(session: Session, username: str, book_id: int) -> bool:
    user_book = get_user_book(session, username, book_id)
    if not user_book:
        return False

    session.delete(user_book)
    session.commit()

    return True


def get_user_read_books(session: Session, username: str) -> List[UserBook]:
    user = get_user_by_username(session, username)
    if not user:
        return []

    statement = select(UserBook).where(
        (UserBook.user_id == user.id) &
        (UserBook.is_read == True)
    )
    return session.exec(statement).all()


def get_user_unread_books(session: Session, username: str) -> List[UserBook]:
    user = get_user_by_username(session, username)
    if not user:
        return []

    statement = select(UserBook).where(
        (UserBook.user_id == user.id) &
        (UserBook.is_read == False)
    )
    return session.exec(statement).all()


def get_user_library_with_details(session: Session, username: str) -> List[dict]:
    user_books = get_user_library(session, username)

    result = []
    for user_book in user_books:
        book = get_book_by_id(session, user_book.book_id)
        if book:
            user_data = {
                "id": user_book.id,
                "book_id": user_book.book_id,
                "is_read": user_book.is_read,
                "rating": user_book.rating,
                "notes": user_book.notes,
                "added_at": user_book.added_at,
                "book": {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "year": book.year,
                    "genre": book.genre,
                    "description": book.description,
                    "is_available": book.is_available,
                    "created_at": book.created_at
                }
            }
            result.append(user_data)

    return result