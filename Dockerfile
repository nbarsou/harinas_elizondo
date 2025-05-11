# Dockerfile
FROM python:3.11-slim

# set a working directory
WORKDIR /app

# copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# expose the Flask port
EXPOSE 5000

# tell Flask how to start
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# use Flask’s built-in server; for production you might switch to gunicorn
CMD ["flask", "run"]
