FROM python:3.9.10

WORKDIR /app

COPY requirements.txt .

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["bash"]