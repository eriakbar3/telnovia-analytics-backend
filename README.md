# Telnovia Analytics Backend

This is the backend service for the Telnovia Analytics platform, a FastAPI-powered application designed to provide a seamless data analysis experience. It allows users to upload datasets, receive an automated data quality assessment, perform analysis through a conversational interface, and generate shareable presentations.

## ✨ Features

- **Secure User Authentication**: JWT-based authentication for user registration and login.
- **Multi-Format File Uploads**: Supports uploading datasets in `.csv`, `.xlsx`, and `.json` formats.
- **Automated Data Health Reports**: Upon upload, automatically generates a comprehensive data quality report, including:
  - Missing value analysis
  - Data type detection
  - High-cardinality and low-variance warnings
  - Anomaly/outlier detection using the IQR method
- **Conversational Analysis**: An interactive endpoint (`/analysis/query`) to perform simple data queries using natural language-like commands (e.g., "describe", "show head").
- **Persistent Notebooks**: All uploads, reports, and conversation histories are saved and linked to a user's "notebook".
- **Dynamic Presentation Generation**:
  - Generate a JSON preview of a presentation for frontend editing.
  - Create a final `.pptx` PowerPoint file based on the customized slide data.
- **Database Migrations**: Uses Alembic to manage and version the database schema, ensuring consistency across environments.

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Data Processing**: Polars
- **Authentication**: Passlib, python-jose (JWT)
- **Presentation Generation**: python-pptx
- **Async Server**: Uvicorn

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- Python 3.10+
- PostgreSQL server running

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/telnovia-analytics-backend.git
    cd telnovia-analytics-backend
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file by copying the example file.

    ```bash
    cp .env.example .env
    ```

    Now, open the `.env` file and fill in your database credentials and a secret key.

5.  **Run database migrations:**
    Apply all schema changes to your database.

    ```bash
    alembic upgrade head
    ```

6.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`, and the interactive documentation can be found at `http://127.0.0.1:8000/docs`.

## 📁 Project Structure

```
├── alembic/              # Database migration scripts
├── app/                  # Main application source code
│   ├── analysis/         # Logic for data analysis and quality checks
│   ├── auth/             # Authentication and user management
│   ├── notebooks/        # Endpoints for file uploads and notebook management
│   ├── presentation/     # Endpoints for presentation generation
│   ├── crud.py           # Database CRUD (Create, Read, Update, Delete) functions
│   ├── database.py       # Database session and engine setup
│   ├── main.py           # FastAPI app instantiation and main router
│   ├── models.py         # SQLAlchemy database models
│   └── schemas.py        # Pydantic data validation schemas
├── presentations/        # (Git-ignored) Stores generated .pptx files
├── uploads/              # (Git-ignored) Stores user-uploaded data files
├── .env.example          # Example environment variables
├── .gitignore            # Files and directories to be ignored by Git
├── alembic.ini           # Alembic configuration file
└── requirements.txt      # Project dependencies
```
