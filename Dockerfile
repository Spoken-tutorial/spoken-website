FROM python:3.6
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /app/requirements_36.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
