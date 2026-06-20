from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=True)
    year = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Book {self.title}>"  # Виправлено дужку


class BookForm(FlaskForm):
    title = StringField('Назва книги', validators=[DataRequired(), Length(max=100)])
    author = StringField('Автор', validators=[DataRequired(), Length(max=100)])
    year = IntegerField('Рік видання', validators=[Optional()])
    genre = StringField('Жанр', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Зберегти')


@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()

    if search_query:
        books = Book.query.filter(
            (Book.title.ilike(f"%{search_query}%")) |
            (Book.author.ilike(f"%{search_query}%"))
        ).all()
    else:
        books = Book.query.all()

    return render_template('list_books.html', books=books, search_query=search_query)


@app.route('/book/add', methods=['GET', 'POST'])
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            year=form.year.data,
            genre=form.genre.data or None
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Книгу успішно додано!', 'success')
        return redirect(url_for('index'))
    return render_template('add_book.html', form=form, title="Додати книгу")


@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.year = form.year.data
        book.genre = form.genre.data or None

        db.session.commit()
        flash('Дані книги оновлено!', 'success')
        return redirect(url_for('index'))

    return render_template('add_book.html', form=form, title="Редагувати книгу")


@app.route('/book/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Книгу видалено!', 'danger')
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
