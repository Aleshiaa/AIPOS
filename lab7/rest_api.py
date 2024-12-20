from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:12345678@db:5432/aipos')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


@app.route('/author', methods=['GET', 'POST'])
def authors():
    if request.method == 'POST':
        data = request.json
        new_author = Author(name=data['name'])
        db.session.add(new_author)
        db.session.commit()
        return jsonify({'message': 'Author created successfully'}), 201

    authors = Author.query.all()
    return jsonify([{'id': author.id, 'name': author.name} for author in authors])


@app.route('/category', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        data = request.json
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': 'Category created successfully'}), 201

    categories = Category.query.all()
    return jsonify([{'id': category.id, 'name': category.name} for category in categories])


@app.route('/publisher', methods=['GET', 'POST'])
def publishers():
    if request.method == 'POST':
        data = request.json
        new_publisher = Publisher(name=data['name'])
        db.session.add(new_publisher)
        db.session.commit()
        return jsonify({'message': 'Publisher created successfully'}), 201

    publishers = Publisher.query.all()
    return jsonify([{'id': publisher.id, 'name': publisher.name} for publisher in publishers])


@app.route('/book', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        data = request.json
        new_book = Book(
            title=data['title'],
            author_id=data['author_id'],
            category_id=data['category_id'],
            publisher_id=data['publisher_id']
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book created successfully'}), 201

    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'category': book.category.name,
        'publisher': book.publisher.name
    } for book in books])


@app.route('/book/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def book_detail(id):
    book = Book.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author_id': book.author_id,
            'category_id': book.category_id,
            'publisher_id': book.publisher_id
        })

    if request.method == 'PUT':
        data = request.json
        book.title = data['title']
        book.author_id = data['author_id']
        book.category_id = data['category_id']
        book.publisher_id = data['publisher_id']
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'}), 200

    if request.method == 'DELETE':
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'}), 200


@app.route('/author/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def author_detail(id):
    author = Author.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({'id': author.id, 'name': author.name})

    if request.method == 'PUT':
        data = request.json
        author.name = data['name']
        db.session.commit()
        return jsonify({'message': 'Author updated successfully'}), 200

    if request.method == 'DELETE':
        for book in author.books:
            db.session.delete(book)
        db.session.delete(author)
        db.session.commit()
        return jsonify({'message': 'Author deleted successfully'}), 200


@app.route('/category/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def category_detail(id):
    category = Category.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({'id': category.id, 'name': category.name})

    if request.method == 'PUT':
        data = request.json
        category.name = data['name']
        db.session.commit()
        return jsonify({'message': 'Category updated successfully'}), 200

    if request.method == 'DELETE':
        for book in category.books:
            db.session.delete(book)
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'}), 200


@app.route('/publisher/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def publisher_detail(id):
    publisher = Publisher.query.get_or_404(id)

    if request.method == 'GET':
        return jsonify({'id': publisher.id, 'name': publisher.name})

    if request.method == 'PUT':
        data = request.json
        publisher.name = data['name']
        db.session.commit()
        return jsonify({'message': 'Publisher updated successfully'}), 200

    if request.method == 'DELETE':
        for book in publisher.books:
            db.session.delete(book)
        db.session.delete(publisher)
        db.session.commit()
        return jsonify({'message': 'Publisher deleted successfully'}), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
