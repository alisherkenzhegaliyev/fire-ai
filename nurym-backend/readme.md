# FastAPI Backend Template

![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-green)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

Welcome to the FastAPI Backend Template! This project serves as a boilerplate for building scalable and efficient backend applications using [FastAPI](https://fastapi.tiangolo.com/), a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python-type hints.

## Features

- **FastAPI**: Leverages FastAPI for rapid development and high performance. 
- **Asynchronous PostgreSQL**: Utilizes asynchronous SQLAlchemy with AsyncPG for non-blocking database operations.
- **Modular Structure**: Organized codebase following best practices for scalability and maintainability.

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)
- PostgreSQL

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/Dimakoua/fastapi_backend_template.git
    cd fastapi_backend_template
    ```

2. **Create a virtual environment**:

    ```bash
    python -m venv .venv
    ```

3. **Activate the virtual environment**:

    - On **Linux/macOS**:

        ```bash
        source .venv/bin/activate
        ```

    - On **Windows** (PowerShell):

        ```powershell
        .venv\Scripts\Activate.ps1
        ```

4. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

5. **Set up environment variables**:

    Rename `.envrc.example` to `.envrc` and adjust the configurations as needed.

6. **Start the application**:

    ```bash
    uvicorn main:app --reload
    ```

    The API will be accessible at `http://127.0.0.1:8000`.

2. **Access the Docs**:

    The API will be accessible at `http://127.0.0.1:8000/docs`.

## Project Structure

```plaintext
fastapi_backend_template/
├── application/
│   └── register_user/
├── controllers/
│   └── auth_controller/
├── middlewares/
├── models/
│   └── user/
├── repositories/
│   └── user_repository/
├── shared/
├── static/
├── .devcontainer/
├── .github/
│   └── workflows/
├── .envrc.example
├── .gitignore
├── .pylintrc
├── LICENSE
├── config.py
├── conftest.py
├── create_db.py
├── database.py
├── facade.py
├── main.py
├── readme.md
└── requirements.txt
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.  

