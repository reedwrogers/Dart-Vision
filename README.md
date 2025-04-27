# 🎯 Dart-Vision

Welcome to **Dart-Vision** — a system for automatically capturing and scoring dart games using computer vision! This project was done for CS 445, Computational Photography, at the University of Illinois Urbana-Champaign.

The project was used as a learning experience to conclude our course. It is still under development, and has several areas for improvement. Main goal was to get exposure to several key topics in computational photography through a real application.

This guide will help you get started setting up your dart board, local database, and running the project.

---

## 📋 Table of Contents
- [Setting Up Your Dart Board](#setting-up-your-dart-board)
- [Setting Up Postgres Locally](#setting-up-postgres-locally)
- [Cloning the Repository](#cloning-the-repository)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Setting Up Your Dart Board

To achieve accurate scoring, make sure your dart board is properly set up:

1. **Mount your dart board** securely on a wall.
2. **Lighting**: Ensure even lighting around the board to minimize shadows.
3. **Calibration**: Place your ArUco markers in each corner of the dart board.
   - use the "classic" dictionary. Markers 7,8,9, and 10 are what should be used at this link: https://chev.me/arucogen/

---

## 🛢️ Setting Up Postgres Locally

This project uses **PostgreSQL** as the backend database to store game sessions and scoring data. Some of these instructions assume you are using some sort of Linux device to host this database. 

### Install Postgres
If you don't have Postgres installed yet:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Or use [Postgres Downloads](https://www.postgresql.org/download/) for your platform.

### Create a Database

After installing Postgres:

```bash
# Switch to the postgres user
sudo -i -u postgres

# Create a new database
createdb dart_vision_db

# (Optional) Create a user and set a password
psql
CREATE USER dartvision_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE dart_vision_db TO dartvision_user;
\q
```

### Update your environment
Make sure to set your database credentials correctly in the `.env` file (see [Environment Configuration](#environment-configuration)).

---

## 📦 Cloning the Repository

First, clone the repo to your local machine:

```bash
git clone https://github.com/yourusername/dart-vision-scoring.git
cd dart-vision-scoring
```

Install dependencies:

```bash
# If using Python backend
pip install -r requirements.txt

# If Dart/Flutter is involved for frontend:
flutter pub get
```

*(Adjust this based on your tech stack!)*

---

## ⚙️ Environment Configuration

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following environment variables:

```
# Postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dart_vision_db
DB_USER=dartvision_user
DB_PASSWORD=yourpassword

# (Optional) Other configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

---

## 🚀 Running the Application

After setting up the environment:

```bash
# If it's a Flask backend:
flask run

# If there's a Dart/Flutter frontend:
flutter run -d chrome
```

The application should now be running!  
Visit `http://localhost:5000` (or wherever your frontend points) to start using Dart Vision Scoring.

---

## 📂 Project Structure

```bash
dart-vision-scoring/
│
├── backend/               # API and server logic
├── frontend/               # Flutter/Dart client (optional)
├── database/               # SQL setup scripts, models
├── images/                 # Example dart board images
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── .env.example            # Sample environment variables
```

---

## 🤝 Contributing

Pull requests are welcome!  
For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

# 🔥 Quick Start

```bash
# Install Postgres
# Clone repo
# Setup .env
# Run the app
```

You're ready to play!
