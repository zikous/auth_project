# Auth Pro - Django GraphQL JWT Authentication

A Django backend with GraphQL API implementing JWT authentication using django-graphql-jwt.

## Features

- User registration and login with email and password
- Custom User model with email as the unique identifier
- JWT authentication with token generation, verification, and refresh
- Protected GraphQL queries requiring authentication
- Clean separation of schema, mutations, and models

## Installation

1. Clone the repository
2. Create a virtual environment and activate it
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Apply migrations
   ```
   python manage.py makemigrations users
   python manage.py migrate
   ```
5. Create a superuser (admin)
   ```
   python manage.py createsuperuser
   ```
6. Run the development server
   ```
   python manage.py runserver
   ```

## GraphQL Endpoint

The GraphQL API is available at http://localhost:8000/graphql/

## Authentication

This project uses JWT (JSON Web Tokens) for authentication. When a user logs in successfully, they receive:

- `token` (access token): Used to authenticate requests
- `refreshToken`: Used to get a new access token when it expires

Include the token in your GraphQL requests with the Authorization header:

```
Authorization: JWT <token>
```

## Example GraphQL Queries

Check the `example_queries.graphql` file for sample queries and mutations, including:

- User registration
- Login (token generation)
- Token refresh
- Protected queries

## JWT Configuration

- Access tokens expire after 30 minutes
- Refresh tokens expire after 7 days

You can modify these settings in `auth_pro/settings.py` under the `GRAPHQL_JWT` section.

## Project Structure

- `auth_pro/`: Main project settings and configuration
- `users/`: App handling user authentication and management
  - `models.py`: Custom User model
  - `schema.py`: GraphQL types, queries, and mutations
