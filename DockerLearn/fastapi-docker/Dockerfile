FROM python:3.12

WORKDIR /fastapi-app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

RUN useradd app && chown -R app:app /fastapi-app

USER app

CMD ["python", "./app/main.py"]


