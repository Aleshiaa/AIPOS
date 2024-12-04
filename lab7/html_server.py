from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://rest_api:5001')


@app.route('/')
def index():
    data = {
        'books': requests.get(f'{API_BASE_URL}/book').json(),
        'authors': requests.get(f'{API_BASE_URL}/author').json(),
        'categories': requests.get(f'{API_BASE_URL}/category').json(),
        'publishers': requests.get(f'{API_BASE_URL}/publisher').json(),
    }
    return render_template('index.html', **data)


@app.route('/entity/<entity>', methods=['GET', 'POST'])
@app.route('/entity/<entity>/<int:id>', methods=['GET', 'POST'])
def edit_or_add_entity(entity, id=None):
    is_edit = id is not None
    entity_name = entity

    if request.method == 'POST':
        data = {}

        if entity == 'book':
            data.update({
                'title': request.form['title'],
                'author_id': request.form['author_id'],
                'category_id': request.form['category_id'],
                'publisher_id': request.form['publisher_id']
            })
        else:
            data = {'name': request.form['name']}

        url = f'{API_BASE_URL}/{entity}/{id}' if is_edit else f'{API_BASE_URL}/{entity}'
        requests.post(url, json=data) if not is_edit else requests.put(url, json=data)
        return redirect(url_for('index'))

    if is_edit:
        item = requests.get(f'{API_BASE_URL}/{entity}/{id}').json()
    else:
        item = {}

    fields = []
    if entity == 'book':
        fields.extend([
            {'id': 'title', 'name': 'title', 'label': 'Title', 'type': 'text', 'value': item.get('title', '')},
            {'id': 'author_id', 'name': 'author_id', 'label': 'Author', 'type': 'select',
             'options': requests.get(f'{API_BASE_URL}/author').json(), 'value': item.get('author_id')},
            {'id': 'category_id', 'name': 'category_id', 'label': 'Category', 'type': 'select',
             'options': requests.get(f'{API_BASE_URL}/category').json(), 'value': item.get('category_id')},
            {'id': 'publisher_id', 'name': 'publisher_id', 'label': 'Publisher', 'type': 'select',
             'options': requests.get(f'{API_BASE_URL}/publisher').json(), 'value': item.get('publisher_id')}
        ])
    else:
        fields = [{'id': 'name', 'name': 'name', 'label': 'Name', 'type': 'text', 'value': item.get('name', '')}]

    return render_template('edit_or_add.html', is_edit=is_edit, entity_name=entity_name, fields=fields)


@app.route('/delete/<entity>/<int:id>', methods=['POST'])
def delete_entity(entity, id):
    requests.delete(f'{API_BASE_URL}/{entity}/{id}')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
