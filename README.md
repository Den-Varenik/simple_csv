# My FastAPI Application

This is my FastAPI application that uses a SQLite database and Alembic for database migrations.

## Getting Started

To run this application, you'll need to have Docker installed on your system.

### Building the Docker Image

1. Clone this repository to your local machine:

```shell
git clone git@gitlab.com:varenik.denisua/simple_csv.git
```

2. Navigate to the root directory of the cloned repository:

```shell
cd simple_csv
```

3. Build the Docker image using the `Dockerfile`:

```shell
docker build -t simple_csv .
```

### Running the Docker Container

After building the Docker image, you can run the Docker container using the following command:

```shell
docker run -p 8000:80 -v "$(pwd)":/data simple_csv
```

This will start the container and map port 80 on the container to port 8000 on your local machine. You can access the application by visiting `http://localhost:8000` in your web browser.

## Configuration

The application uses a `.env` file in the root directory to store environment variables. You can copy the `.env.example` file to `.env` and modify the values as needed.

The application also uses Alembic for database migrations. The `alembic.ini` file in the root directory contains the configuration for Alembic. To perform a database migration, run the following command:

```shell
docker exec -it $(docker ps -f "ancestor=simple_csv" -q) /bin/bash

alembic upgrade head

exit
```

This will start a new container and run the `alembic upgrade head` command inside the container to apply any pending database migrations.

## API Documentation

To access the API documentation with Swagger UI:

1. After starting the Docker container using the docker run command as described in the previous section of the `README`, open a web browser.


2. In the address bar of the web browser, type `http://localhost:8000/docs` and press Enter. This will open the Swagger UI interface in the web browser.


3. Use the Swagger UI interface to explore and test the API endpoints. You can click on the different endpoints to see their details, and use the "Try it out" button to make requests to the API.

That's it! The Swagger UI interface should provide a convenient way to explore and test the API endpoints.
