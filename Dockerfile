FROM python:3.10-slim

WORKDIR /app/flask_app
ENV PYTHONPATH=/app/flask_app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["pytest", "tests"]

