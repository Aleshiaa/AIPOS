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
    authors = Author.query.all()
    categories = Category.query.all()
    publishers = Publisher.query.all()
    return render_template('index.html', books=books, authors=authors, categories=categories, publishers=publishers)


@app.route('/edit_or_add/<entity>/<int:id>', methods=['GET', 'POST'])
@app.route('/edit_or_add/<entity>', methods=['GET', 'POST'])
def edit_or_add_entity(entity, id=None):
    is_edit = id is not None
    if entity == 'book':
        entity_name = 'Book'
        fields = [
            {'id': 'title', 'name': 'title', 'label': 'Title', 'type': 'text'},
            {'id': 'author_id', 'name': 'author_id', 'label': 'Author', 'type': 'select',
             'options': [{'id': a.id, 'name': a.name} for a in Author.query.all()]},
            {'id': 'category_id', 'name': 'category_id', 'label': 'Category', 'type': 'select',
             'options': [{'id': c.id, 'name': c.name} for c in Category.query.all()]},
            {'id': 'publisher_id', 'name': 'publisher_id', 'label': 'Publisher', 'type': 'select',
             'options': [{'id': p.id, 'name': p.name} for p in Publisher.query.all()]},
        ]
        if is_edit:
            book = Book.query.get_or_404(id)
            fields[0]['value'] = book.title
            fields[1]['value'] = book.author_id
            fields[2]['value'] = book.category_id
            fields[3]['value'] = book.publisher_id
    elif entity == 'author':
        entity_name = 'Author'
        fields = [{'id': 'name', 'name': 'name', 'label': 'Name', 'type': 'text'}]
        if is_edit:
            author = Author.query.get_or_404(id)
            fields[0]['value'] = author.name
    elif entity == 'category':
        entity_name = 'Category'
        fields = [{'id': 'name', 'name': 'name', 'label': 'Name', 'type': 'text'}]
        if is_edit:
            category = Category.query.get_or_404(id)
            fields[0]['value'] = category.name
    elif entity == 'publisher':
        entity_name = 'Publisher'
        fields = [{'id': 'name', 'name': 'name', 'label': 'Name', 'type': 'text'}]
        if is_edit:
            publisher = Publisher.query.get_or_404(id)
            fields[0]['value'] = publisher.name
    else:
        return "Unknown entity", 404

    if request.method == 'POST':
        data = {field['name']: request.form[field['name']] for field in fields}
        if is_edit:
            if entity == 'book':
                book.title = data['title']
                book.author_id = data['author_id']
                book.category_id = data['category_id']
                book.publisher_id = data['publisher_id']
            elif entity == 'author':
                author.name = data['name']
            elif entity == 'category':
                category.name = data['name']
            elif entity == 'publisher':
                publisher.name = data['name']
        else:
            if entity == 'book':
                db.session.add(Book(**data))
            elif entity == 'author':
                db.session.add(Author(**data))
            elif entity == 'category':
                db.session.add(Category(**data))
            elif entity == 'publisher':
                db.session.add(Publisher(**data))
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_or_add.html', is_edit=is_edit, entity_name=entity_name, fields=fields)




@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    app.logger.info(f"Deleted book: {book.title} with ID: {id}.")
    return redirect(url_for('index'))


@app.route('/delete_author/<int:id>', methods=['POST'])
def delete_author(id):
    author = Author.query.get_or_404(id)
    for book in author.books:
        db.session.delete(book)
    db.session.delete(author)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete_category/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    for book in category.books:
        db.session.delete(book)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_publisher/<int:id>', methods=['POST'])
def delete_publisher(id):
    publisher = Publisher.query.get_or_404(id)
    for book in publisher.books:
        db.session.delete(book)
    db.session.delete(publisher)
    db.session.commit()
    return redirect(url_for('index'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
