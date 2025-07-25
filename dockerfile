FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y \
    g++ \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE OJ.settings

# RUN pip install gunicorn

CMD ["python","manage.py","runserver","0.0.0.0:8000"]

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "OJ.wsgi:application"]
