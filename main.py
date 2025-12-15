from fastapi import FastAPI
from sqlmodel import Session, select
import uuid

from database.connection import engine, create_db_and_tables
from database.books import create_book, get_or_create_user
from models.books import Book, BookCreate, User, UserBook
from routes.admin import router as admin_router
from routes.user import router as user_router

create_db_and_tables()


def create_test_data():
    with Session(engine) as session:
        books = session.exec(select(Book)).all()

        if not books:
            test_books = [
                BookCreate(
                    title="Преступление и наказание",
                    author="Федор Достоевский",
                    year=1866,
                    genre="Роман",
                    description="Философский роман о моральных дилеммах"
                ),
                BookCreate(
                    title="Мастер и Маргарита",
                    author="Михаил Булгаков",
                    year=1967,
                    genre="Роман",
                    description="Мистический роман о добре и зле"
                ),
                BookCreate(
                    title="Война и мир",
                    author="Лев Толстой",
                    year=1869,
                    genre="Роман-эпопея",
                    description="Масштабное произведение о войне 1812 года"
                ),
                BookCreate(
                    title="1984",
                    author="Джордж Оруэлл",
                    year=1949,
                    genre="Антиутопия",
                    description="Роман о тоталитарном обществе"
                ),
                BookCreate(
                    title="Гарри Поттер и философский камень",
                    author="Джоан Роулинг",
                    year=1997,
                    genre="Фэнтези",
                    description="Первая книга о юном волшебнике"
                )
            ]

            for book_data in test_books:
                create_book(session, book_data)

            test_user = get_or_create_user(session, "test_user")

            user_book1 = UserBook(
                user_id=test_user.id,
                book_id=1,
                is_read=True,
                rating=5
            )

            user_book2 = UserBook(
                user_id=test_user.id,
                book_id=2,
                is_read=False
            )

            session.add_all([user_book1, user_book2])
            session.commit()

            print("Тестовые данные созданы:")
            print(f"- 5 книг")
            print(f"- Пользователь: test_user")
            print(f"- 2 книги в библиотеке пользователя")


app = FastAPI(
    title="Библиотека API",
    description="API для управления библиотекой книг с базой данных",
    version="1.0.0"
)

app.include_router(admin_router)
app.include_router(user_router)


@app.on_event("startup")
def on_startup():
    create_test_data()


@app.get("/")
async def root():
    return {
        "message": "Библиотечное API с базой данных",
        "database": "SQLite (library.db)",
        "endpoints": {
            "admin": {
                "GET /admin/books": "Получить все книги",
                "GET /admin/books/{id}": "Получить книгу по ID",
                "POST /admin/books": "Создать новую книгу",
                "PUT /admin/books/{id}": "Обновить книгу",
                "DELETE /admin/books/{id}": "Удалить книгу",
                "GET /admin/books/search/": "Поиск книг"
            },
            "user": {
                "GET /user/books": "Просмотреть книги",
                "GET /user/books/{id}": "Детали книги",
                "GET /user/search/": "Поиск книг",
                "GET /user/library": "Личная библиотека (параметр: username)",
                "POST /user/library": "Добавить в библиотеку (тело: book_id, username)",
                "PATCH /user/library/{book_id}/read": "Отметить прочитанной (параметр: username)",
                "PATCH /user/library/{book_id}/unread": "Отметить непрочитанной",
                "DELETE /user/library/{book_id}": "Удалить из библиотеки"
            }
        },
        "test_user": {
            "username": "test_user",
            "password": "нет (только username)"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Библиотечная система с БД работает!"}


@app.get("/create-test-user")
async def create_test_user_endpoint():
    with Session(engine) as session:
        username = f"user_{str(uuid.uuid4())[:8]}"
        user = get_or_create_user(session, username)
        return {"message": "Тестовый пользователь создан", "username": username}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)