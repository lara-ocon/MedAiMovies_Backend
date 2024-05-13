# MedAiMovies_Backend

## Steps

1. Clone the repository
2. Create environment CTRL + SHIFT + P -> Python: Select Interpreter -> Create New Environment (select requirements.txt from requirements) To activate move to .venv/Scrits and activate
3. try python manage.py runserver 
4. If does not work, delete db.sqlite3 and python manage.py migrate
5. python manage.py runserver

# cargar los datos
python manage.py loaddata peliculas.json

# crear admin
python manage.py createsuperuser --username admin --email admin@email.com
