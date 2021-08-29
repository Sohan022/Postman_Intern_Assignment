FROM python:3.6

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY crawler.py /app

COPY .env /app

CMD python crawler.py