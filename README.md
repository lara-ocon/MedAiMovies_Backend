
# MedAiMovies_Backend

## Setup and Deployment

Follow these steps to get the project up and running:

1. **Clone the repository:**
    
    ```bash
    git clone <repository-url>
    cd MedAiMovies_Backend
    ```


2. **Set up the virtual environment:**
- Open the command line (CMD) or terminal.
- Navigate to the project directory where you have cloned your repo.
- Create a virtual environment:
  ```
  python -m venv .venv
  ```
- Activate the virtual environment:
  - On Windows:
    ```
    .\.venv\Scripts\activate
    ```
  - On macOS and Linux:
    ```
    source .venv/bin/activate
    ```
- Install the required packages:
  ```
  pip install -r requirements.txt
  ```

3. **Set up the database:**
- Delete `db.sqlite3` if it exists from previous setups to start fresh.
- Run migrations to set up your database schema:
  ```
  python manage.py migrate
  ```

4. **Load initial data into the database (optional):**
- The project includes a JSON file `peliculas.json` with sample data for movies. You can load this data into the database using the following command:
  ```
  python manage.py loaddata peliculas.json
  ```


5. **Create an admin user:**
To access the Django admin interface, you need to create an admin user. Run the following command:
```
python manage.py createsuperuser --username admin --email admin@email.com

```
Follow the prompts to set a password for the admin user.

6. **Run the server:**

    ```bash
    python manage.py runserver
    ```

This starts the development server on `http://127.0.0.1:8000/` where you can access the application.

## Accessing the Admin Interface

- Navigate to `http://127.0.0.1:8000/admin` and log in using the admin credentials you created to manage users, movies, and reviews directly through Django’s built-in admin interface.

## API Endpoints

The backend supports several endpoints that you can interact with through HTTP requests:

- **User Registration**: `POST /api/users/`
- **User Login**: `POST /api/users/login/` (manages sessions and tokens)
- **User Details**: `GET /api/users/me/` (retrieve or update user details)
- **User Logout**: `POST /api/users/logout/`
- **List/Create Movies**: `GET, POST /api/peliculas/`
- **Movie Details**: `GET, PUT, DELETE /api/peliculas/<int:pk>/`
- **List/Create Reviews**: `GET, POST /api/reviews/`
- **Search Movies**: `GET /api/peliculas/search/` (supports searching by various fields like title, director, etc.)

## Models

- **Usuario**: Custom user model that extends Django’s `AbstractUser`.
- **Pelicula**: Represents movies with fields for title, release date, genre, duration, country, director, synopsis, poster, and average rating.
- **Review**: Represents reviews for movies, linked to both the movie and the user who wrote the review.

## Schema and API Documentation

- **Swagger UI**: `GET /api/schema/swagger-ui/`

- **OpenAPI Schema**: `GET /api/schema/`
Another option to see the schema is to run the command:
```
python manage.py spectacular --file schema.yml
```
To obtain in json format:
```
python manage.py spectacular --file schema.json --format openapi-json
```
- **ReDoc Documentation**: `GET /api/schema/redoc/`

These endpoints provide a schema and human-readable documentation for the API.

## Further Information

For more detailed usage, you can refer to the DRF (Django REST Framework) documentation and Django documentation to understand how views, serializers, and routing are handled in this project.
