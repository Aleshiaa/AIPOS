FROM python:3.10-slim

RUN pip install --no-cache-dir flask flask_sqlalchemy psycopg2-binary flask_migrate

COPY . /app

WORKDIR /app

EXPOSE 5000

CMD ["python", "app.py"]
