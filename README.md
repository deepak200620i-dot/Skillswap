# IPBL Skill Swap Platform

## Project Overview

This repository contains a **Skill Swap** web application built with **Flask**.  Users can create profiles, list their skills, and discover other users with complementary skills.  The platform supports:

- User registration & authentication
- Profile management (including profile pictures)
- Skill management and matching engine
- Requests & reviews workflow for skill exchanges
- Dynamic dashboards and matching visualisations

The codebase follows a modular structure:

- `app.py` – Flask application entry point
- `routes/` – Blueprint modules (`matching.py`, `reviews.py`, etc.)
- `templates/` – Jinja2 HTML templates for the UI
- `utils/` – Helper utilities
- `.env.example` – Example environment configuration

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IPBL
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in the required values (e.g., `SECRET_KEY`, database URL).
5. **Run the development server**
   ```bash
   flask run
   ```
   The app will be available at `http://127.0.0.1:5000/`.

## Contributing

Contributions are welcome!  Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Make your changes and ensure existing tests pass.
4. Submit a pull request with a clear description of the changes.

## License

This project is licensed under the MIT License – see the `LICENSE` file for details.
