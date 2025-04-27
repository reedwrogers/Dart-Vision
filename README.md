# 🎯 Dart-Vision

Welcome to **Dart-Vision** — a system for automatically capturing and scoring dart games using computer vision! This project was done for CS 445, Computational Photography, at the University of Illinois Urbana-Champaign.

The project was used as a learning experience to conclude our course. It is still under development, and has several areas for improvement. Main goal was to get exposure to several key topics in computational photography through a real application.

This guide will help you get started setting up your dart board, local database, and running the project.

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

You'll need to create a local Postgres database with the correct user, password, database, and schema.

### Install PostgreSQL
If you don't already have Postgres installed:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

---

### Create the Database, User, and Schema

1. **Switch to the `postgres` user:**

```bash
sudo -i -u postgres
```

2. **Create the database user (`dart_thrower`) and database (`darts`):**

```bash
psql
```

Inside `psql`, run:

```sql
-- Create the user
CREATE USER dart_thrower WITH PASSWORD 'darts';

-- Create the database
CREATE DATABASE darts OWNER dart_thrower;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE darts TO dart_thrower;

\q
```

3. **Connect to the new database:**

```bash
psql -h localhost -U dart_thrower -d darts
```
*(It'll prompt you for the password: `darts`)*

---

### Create the Tables

Inside the `psql` session for `darts`, run the following SQL to create your schema:

```sql
-- Create "games" table
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT now()
);

-- Create "images" table
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    player_name TEXT NOT NULL,
    image_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

-- Create "processed_images" table
CREATE TABLE processed_images (
    id SERIAL PRIMARY KEY,
    dart_1 INTEGER,
    dart_2 INTEGER,
    dart_3 INTEGER,
    game_id INTEGER REFERENCES games(id),
    player_name TEXT,
    processed_image BYTEA
);

-- Create "scores" table
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES games(id),
    dart1 INTEGER,
    dart2 INTEGER,
    dart3 INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    player TEXT
);
```
✅ After running all of these commands, your database will be ready!

# 📋 Extra Commands

If you want to inspect the database while developing:

- Connect to the database:

```bash
psql -h localhost -U dart_thrower -d darts
```

- List all tables:

```sql
\dt
```

- View a table's structure:

```sql
\d tablename
```

Example:

```sql
\d games
```
---

# 🧹 Let me know if you want me to also give you a clean `.sql` file you can import instead of manually creating the tables! (Takes 1 command to set everything up.)  
Would you like that too? 🚀

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
