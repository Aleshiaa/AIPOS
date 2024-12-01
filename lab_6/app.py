import logging
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',
                                                       'postgresql://postgres:12345678@localhost:5432/aipos')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)


log_format = '%(asctime)s - %(levelname)s - %(message)s'
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('access.log')
file_handler.setFormatter(logging.Formatter(log_format))
app.logger.addHandler(file_handler)

app.logger.info(f"Current working directory: {os.getcwd()}")


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)

    author = db.relationship('Author', backref='books')
    category = db.relationship('Category', backref='books')
    publisher = db.relationship('Publisher', backref='books')


@app.before_request
def log_request_info():
    app.logger.info(f"Request: {request.method} {request.url} - IP: {request.remote_addr} - Data: {request.form.to_dict()}")


@app.after_request
def log_response_info(response):
    app.logger.info(f"Response: {response.status_code} {request.method} {request.url} - IP: {request.remote_addr}")
    return response


@app.route('/')
def index():
    books = Book.query.all()
    app.logger.info(f"Loaded {len(books)} books for the main page.")
    return render_template('index.html', books=books)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author_id = request.form['author_id']
        category_id = request.form['category_id']
        publisher_id = request.form['publisher_id']

        new_book = Book(title=title, author_id=author_id, category_id=category_id, publisher_id=publisher_id)
        db.session.add(new_book)
        db.session.commit()
        app.logger.info(f"Added book: {title} with author_id {author_id}, category_id {category_id}, publisher_id {publisher_id}.")
        return redirect(url_for('index'))

    authors = Author.query.all()
    categories = Category.query.all()
    publishers = Publisher.query.all()
    app.logger.info("Rendering add_book page.")
    return render_template('add_book.html', authors=authors, categories=categories, publishers=publishers)


@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        old_title = book.title
        book.title = request.form['title']
        book.author_id = request.form['author_id']
        book.category_id = request.form['category_id']
        book.publisher_id = request.form['publisher_id']
        db.session.commit()
        app.logger.info(f"Updated book from '{old_title}' to '{book.title}'.")
        return redirect(url_for('index'))

    authors = Author.query.all()
    categories = Category.query.all()
    publishers = Publisher.query.all()
    app.logger.info(f"Rendering edit_book page for book ID: {id}.")
    return render_template('edit_book.html', book=book, authors=authors, categories=categories, publishers=publishers)


@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    app.logger.info(f"Deleted book: {book.title} with ID: {id}.")
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
