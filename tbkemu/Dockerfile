# 
FROM python:3.9

# 
WORKDIR /app

# 
COPY ./requirements.txt /requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# 
# COPY ./app /code/app
# 
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]