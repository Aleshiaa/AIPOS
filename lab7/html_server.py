from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://rest_api:5001')


@app.route('/')
def index():
    books = requests.get(f'{API_BASE_URL}/books').json()
    return render_template('index.html', books=books)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'author_id': request.form['author_id'],
            'category_id': request.form['category_id'],
            'publisher_id': request.form['publisher_id']
        }
        requests.post(f'{API_BASE_URL}/books', json=data)
        return redirect(url_for('index'))

    authors = requests.get(f'{API_BASE_URL}/authors').json()
    categories = requests.get(f'{API_BASE_URL}/categories').json()
    publishers = requests.get(f'{API_BASE_URL}/publishers').json()
    return render_template('add_book.html', authors=authors, categories=categories, publishers=publishers)


@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = requests.get(f'{API_BASE_URL}/books/{id}').json()
    authors = requests.get(f'{API_BASE_URL}/authors').json()
    categories = requests.get(f'{API_BASE_URL}/categories').json()
    publishers = requests.get(f'{API_BASE_URL}/publishers').json()

    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'author_id': request.form['author_id'],
            'category_id': request.form['category_id'],
            'publisher_id': request.form['publisher_id']
        }
        requests.put(f'{API_BASE_URL}/books/{id}', json=data)
        return redirect(url_for('index'))

    return render_template('edit_book.html', book=book, authors=authors, categories=categories, publishers=publishers)


@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    requests.delete(f'{API_BASE_URL}/books/{id}')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
