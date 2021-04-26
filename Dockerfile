FROM python:3.6

ENV FLASK_APP run.py

COPY run.py gunicorn-cfg.py requirements.txt config.py .env ./
COPY app app

RUN pip install Flask-Authlib-Client
RUN pip install requests 
RUN pip install -r requirements.txt


EXPOSE 5000

# CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
CMD ["python", "run.py", "--port", "5000"]
