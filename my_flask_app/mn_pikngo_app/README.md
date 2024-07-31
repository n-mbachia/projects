# Pikngo_app

This is the README file for the `my_flask_app/mn_pikngo_app` application. 

## Overview

The `my_flask_app/mn_pikngo_app` is a Flask-based web application that serves as the backend for the MN Pikngo project. It provides APIs for managing user data, creating and updating posts, and interacting with the MN Pikngo database.

## Architecture

The application follows a typical client-server architecture, with the Flask server acting as the backend and serving API endpoints to the client applications. The server interacts with the MN Pikngo database to store and retrieve data.

The application is structured using the Model-View-Controller (MVC) design pattern. The models define the data structures and relationships, the views handle the presentation logic, and the controllers handle the business logic and API endpoints.

## Project structure
The project structure of the `my_flask_app/mn_pikngo_app` application is as follows:

```
my_flask_app/mn_pikngo_app
├── app.py
├── blueprint.py
├── CODE_OF_CONDUCT.md
├── CONTRIBUTION.md
├── extensions.py
├── forms.py
├── instance/
├── media/
├── models.py
├── __pycache__/
├── README.md
├── static/
├── templates/
└── tests/
    └── views.py
```

The `my_flask_app/mn_pikngo_app` directory contains the main application files such as `app.py`, `blueprint.py`, `forms.py`, and `models.py`. It also includes directories for static assets (`static`), templates (`templates`), and tests (`tests`). Additionally, there are files for configuration (`instance`), media storage (`media`), and documentation (`README.md`, `CODE_OF_CONDUCT.md`, and `CONTRIBUTION.md`).


## Installation

To install and run the `my_flask_app/mn_pikngo_app` application, follow these steps:

1. Clone the repository: `git clone https://github.com/mbachia-pk/.git`
2. Navigate to the project directory: `cd my_flask_app/mn_pikngo_app`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Set up the database: `python app.py db init`
5. Run the application: `python app.py`

## Application Documentation

The `my_flask_app/mn_pikngo_app` application provides the following API endpoints:

- `/api/users`: CRUD operations for managing user data.
- `/api/posts`: CRUD operations for creating and updating posts.
- `/api/comments`: CRUD operations for managing comments on posts.

For detailed documentation on how to use these endpoints, refer to the API documentation.

## Contributing

If you would like to contribute to the project `my_flask_app/mn_pikngo_app` application, please follow the guidelines outlined in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## License

The `my_flask_app/mn_pikngo_app` application is licensed under the MIT License. See the LICENSE file for more details.
