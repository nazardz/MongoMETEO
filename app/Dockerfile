FROM python:3.9-slim-buster
WORKDIR /code
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8081"]
