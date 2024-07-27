FROM python:3.11

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r needs.txt

EXPOSE 8080

COPY . .

CMD ["python", "main.py"] 
