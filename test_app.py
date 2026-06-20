import unittest
from app import app, db, Book


class BookAppTestCase(unittest.TestCase):
    def setUp(self):
        """Налаштування тестового середовища перед кожним тестом"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Очищення бази даних після кожного тесту"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_book_with_genre(self):
        """1. Тест додавання книги з жанром"""
        data = {
            'title': 'Гаррі Поттер',
            'author': 'Дж. К. Ролінґ',
            'year': 1997,
            'genre': 'Фентезі'
        }
        response = self.client.post('/book/add', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            book = Book.query.filter_by(title='Гаррі Поттер').first()
            self.assertIsNotNone(book)
            self.assertEqual(book.author, 'Дж. К. Ролінґ')
            self.assertEqual(book.genre, 'Фентезі')

    def test_edit_book(self):
        """2. Тест редагування книги (включаючи зміну жанру)"""
        with app.app_context():
            book = Book(title='Старий і море', author='Ернест Гемінґвей', year=1952, genre='Повість')
            db.session.add(book)
            db.session.commit()
            book_id = book.id

        updated_data = {
            'title': 'Старий і море (Оновлено)',
            'author': 'Ернест Гемінґвей',
            'year': 1952,
            'genre': 'Класика'
        }

        response = self.client.post(f'/book/edit/{book_id}', data=updated_data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        with app.app_context():
            updated_book = Book.query.get(book_id)
            self.assertEqual(updated_book.title, 'Старий і море (Оновлено)')
            self.assertEqual(updated_book.genre, 'Класика')

    def test_list_books_contains_genre(self):
        """3. Тест перегляду списку книг із новим полем (жанром)"""
        with app.app_context():
            book = Book(title='Дюна', author='Френк Герберт', year=1965, genre='Кіберпанк-Тест')
            db.session.add(book)
            db.session.commit()

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        html_content = response.data.decode('utf-8')
        self.assertIn('Дюна', html_content)
        self.assertIn('Кіберпанк-Тест', html_content)

    def test_search_functionality(self):
        """4. Тест пошуку за назвою або автором (Завдання 4)"""
        with app.app_context():
            book1 = Book(title='1984', author='Джордж Орвелл', genre='Антиутопія')
            book2 = Book(title='Тигролови', author='Іван Багряний', genre='Пригоди')
            db.session.add_all([book1, book2])
            db.session.commit()

        response = self.client.get('/?search=Орвелл')
        self.assertEqual(response.status_code, 200)
        html_content = response.data.decode('utf-8')

        self.assertIn('1984', html_content)
        self.assertNotIn('Тигролови', html_content)

        response = self.client.get('/?search=Тигро')
        html_content = response.data.decode('utf-8')

        self.assertIn('Тигролови', html_content)
        self.assertNotIn('1984', html_content)


if __name__ == '__main__':
    unittest.main()
