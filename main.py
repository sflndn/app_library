from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
import urllib.parse

from database.connection import engine, create_db_and_tables
from database.books import create_book
from models.books import Book, BookCreate
from routes.admin import router as admin_router
from routes.user import router as user_router

# Создаем таблицы при запуске
create_db_and_tables()


# Создаем тестовые книги при первом запуске
def create_test_books():
    """Создание тестовых книг при первом запуске"""
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

            session.commit()
            print("Тестовые книги созданы")


app = FastAPI(
    title="Библиотека API",
    description="API для управления библиотекой книг",
    version="1.0.0"
)

# Подключаем маршруты
app.include_router(admin_router)
app.include_router(user_router)


@app.on_event("startup")
def on_startup():
    """Создание тестовых данных при запуске приложения"""
    create_test_books()


@app.get("/")
async def root():
    """Корневая страница с информацией об API"""
    return {
        "message": "Библиотечное API",
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
                "GET /user/library": "Личная библиотека (user_id параметр)",
                "POST /user/library/{book_id}": "Добавить в библиотеку",
                "PATCH /user/library/{book_id}/read": "Отметить прочитанной",
                "PATCH /user/library/{book_id}/unread": "Отметить непрочитанной",
                "DELETE /user/library/{book_id}": "Удалить из библиотеки"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy", "message": "Библиотечная система работает!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)