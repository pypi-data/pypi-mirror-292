# Pegasus App

<div align="center">
    <img src="public/logo128.png" alt="Pegasus Logo" width="128" height="128">
</div>

Pegasus is a next generation tech stack that combines the power of Python with React.

It supports Server Side Rendering (SSR) which is great for SEO and performance.

## Structure

```text
|-- app
    |-- api
        |-- home.py     # Homepage API
        |-- users.py    # User API
    |-- lib
        |-- auth.py     # Authentication
        |-- db.py       # Database connection (SQLModel)
        |-- errors.py   # Custom exceptions
        |-- models.py   # SQLModel models (compatible with FastAPI)
        |-- seo.py      # SEO metadata
        |-- settings.py # Environment settings
        |-- utils.py    # Utility functions
    |-- routers
        |-- users.py    # User API
|-- logs                # Application logs
|-- public              # Static files
    |-- fonts           # Fonts
    |-- js              # JavaScript (output by webpack)
    |-- logo.png        # Logo
    |-- manifest.json   # PWA manifest
    |-- robots.txt      # Robots.txt
|-- ui
    |-- routes
        |-- Errors.tsx  # Error pages
        |-- Home.tsx    # Homepage
    |-- App.tsx         # App router
    |-- index.css       # CSS entrypoint
    |-- index.html      # Homepage entrypoint
    |-- index.tsx       # React entrypoint
|-- .env.dev            # Development environment
|-- .env.prod           # Production environment
```

## Development

In the root directory of the project, run:

```bash
npm install
python -m venv env
source env/bin/activate
pip install -r requirements.txt

npm run dev                               # Starts webpack dev and backend servers
```

Open `http://localhost:8000` to see the homepage.
Open `http://localhost:8000/docs` to see the Swagger UI.

## Documentation

### Swagger UI

<div align="center">
    <img src="public/docs/swagger.png" alt="Swagger UI" width="80%">
</div>

### Learn More

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [Webpack](https://webpack.js.org/)