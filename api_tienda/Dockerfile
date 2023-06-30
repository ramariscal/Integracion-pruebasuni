FROM python:3.11.3
WORKDIR /app
COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

CMD ["python3", "-m", "flask", "--debug", "run", "--host=0.0.0.0"]