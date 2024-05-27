# Acesta este Dockerfile-ul pentru crearea imaginii aplicatiei Flask-gunicorn
FROM python:3.12
# Definim directorul incare vom pune toate dependintele si modulele python
WORKDIR /app
# Copiem fisierul requirements pentru a instala toate librariile de care avem nevoie
COPY requirements.txt /app
# Instalam tot ce este in requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
# Copiem intreaga aplicatie in /app
COPY . /app



