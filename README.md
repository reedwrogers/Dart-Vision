# 🎯 Dart-Vision

Welcome to **Dart-Vision** — a system for automatically capturing and scoring dart games using computer vision! This project was built for CS 445: *Computational Photography* at the University of Illinois Urbana-Champaign.

It was used as a learning experience to conclude our course and is still under development. The main goal was to gain hands-on experience with several key topics in computational photography through a real-world application.

---

## Glossary

This repository is divided into two main parts:

- **[main.ipynb](#mainipynb)** — our primary **Jupyter Notebook**, where we explored and tested multiple methods of detecting and scoring darts using computer vision. This was the core of our experimentation and learning.
  
- **[Setting Up Your Dart Board](#setting-up-your-dart-board)** — the **production pipeline**, where we configure a working system to score darts in real-time using a phone camera, a local server, and a Postgres backend.

---

## main.ipynb <a id="mainipynb"></a>

In this notebook, we experimented with:

- Different image processing techniques to isolate dart tips
- Use of ArUco markers for board calibration
- Matching templates for numbers or segments
- Custom scoring heuristics
- Accuracy testing on sample images

You can find the notebook inside the `Python Files/` directory. It documents the full journey from raw image input to a working scoring prototype.

---

## Setting Up Your Dart Board <a id="setting-up-your-dart-board"></a>

To achieve accurate scoring, make sure your dart board is properly set up:

1. **Mount your dart board** securely on a wall.
2. **Lighting**: Ensure even lighting around the board to minimize shadows.
3. **Calibration**: Place your ArUco markers in each corner of the dart board.
   - Use the "classic" dictionary.
   - Markers 7, 8, 9, and 10 should be used, generated from [https://chev.me/arucogen/](https://chev.me/arucogen/)

---

## Setting Up Postgres Locally

This project uses **PostgreSQL** as the backend database to store game sessions and scoring data.

### Install PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Create the Database, User, and Schema

1. Switch to the `postgres` user:

```bash
sudo -i -u postgres
```

2. Create the user and database:

```bash
psql
```

```sql
-- Create the user
CREATE USER dart_thrower WITH PASSWORD 'darts';

-- Create the database
CREATE DATABASE darts OWNER dart_thrower;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE darts TO dart_thrower;

\q
```

3. Connect to the database:

```bash
psql -h localhost -U dart_thrower -d darts
```

Password: `darts`

---

### Create the Tables

Run the following schema:

```sql
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    player_name TEXT NOT NULL,
    image_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE processed_images (
    id SERIAL PRIMARY KEY,
    dart_1 INTEGER,
    dart_2 INTEGER,
    dart_3 INTEGER,
    game_id INTEGER REFERENCES games(id),
    player_name TEXT,
    processed_image BYTEA
);

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

---

## Inspecting the Database

- List all tables:

```sql
\dt
```

- View a table’s structure:

```sql
\d tablename
```

Example:

```sql
\d games
```

---

## Cloning the Repository

```bash
git clone https://github.com/yourusername/dart-vision-scoring.git
cd dart-vision-scoring
```

Install dependencies:

```bash
pip install -r requirements.txt       # For Python backend
flutter pub get                      # If using Flutter frontend
```

---

## Setting up the Environment

Create a Python environment called `jupyter` and install the required packages. This is necessary because the PHP scripts are configured to run inside this environment (on Linux).

*TODO: Add specific environment setup instructions.*

---

## Running the Application

The app runs on a local web server.

*TODO: Add details on how you configured Apache (or other web server) to host this.*

Once configured, you can visit your web app in a browser:

```
http://192.168.40.72
```

Replace that with the IP of your local server.

---

## Project Structure

```bash
dart-vision-scoring/
│
├── Python Files/           # Experimental notebooks and image-processing code
├── Sample Images/          # Contains sample dart images
├── Templates/              # Templates used for number/segment recognition
├── Web Interface/          # HTML, CSS, JS, PHP, and Python for frontend/backend
├── README.md               # This file
├── requirements.txt        # Python requirements
```

---

## Quick Start Summary

```bash
# 1. Install PostgreSQL
# 2. Clone the repo
# 3. Set up the database
# 4. Configure the web server
# 5. Run the app
```

You're ready to play darts with vision-based scoring!
