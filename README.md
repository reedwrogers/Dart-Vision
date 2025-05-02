# 🎯 Dart-Vision

Welcome to **Dart-Vision** - a system for automatically capturing and scoring dart games using computer vision! Specifically, we are attempting <strong>single-camera</strong> scoring. This project was built for CS 445: *Computational Photography* at the University of Illinois Urbana-Champaign.

It was used as a learning experience to conclude our course and is still under development. The main goal was to gain hands-on experience with several key topics in computational photography through a real-world application.

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

## Glossary

This repository is divided into two main parts:

- **[main.ipynb](#mainipynb)** - our primary **Jupyter Notebook**, where we explored and tested multiple methods of detecting and scoring darts using computer vision. This was the core of our experimentation and learning.
  
- **[Local Web App Implementation of Dart-Vision](#setting-up-your-dart-board)** - the **front-end web application**, where we configure a working system to score darts in real-time using a phone camera, a local server, and a Postgres backend. In this seciton, you can set up our system to run at home with your own dartboard.

Put simply, main.ipynb contains the bulk of where our work was done for this project - look there for more information on our thought processes and ideas for dart-vision. The section for the web app is really just a proof-of-concept on how we might apply our methods into some sort of application for an end-user. If you have no interest in running the system locally, you can ignore that section, or simply view our video for an idea of how the system works on the front-end (<a href="https://youtu.be/ukSuz6VD6F0">here</a>).

---

## ⭐ main.ipynb <a id="mainipynb"></a>

In this notebook, we experimented with:

- Different image processing techniques to isolate dart tips
- Use of ArUco markers for board calibration
- Matching templates for numbers or segments
- Use of machine learning and object segmentation for region detection
- Accuracy testing on sample images

While we used a more manual, potentially less "smart" method of scoring darts for our proof-of-concept of the front-end application, our experimentation and learning with different computaitonal photography methods as it relates to this problem occured within this notebook. Please browse our clearly documented methods as you see how we approached solving the problem of automatic dart scoring in several different ways. 

You can find the notebook inside the `Python Files/` directory, or click this link <a href="https://github.com/reedwrogers/Dart-Vision/blob/main/Python%20Files/main.ipynb">here.</a> 

---

## Prerequisites <a id="setting-up-your-dart-board"></a>

Before getting started, make sure you have the following:

- A **Linux-based machine** to run the server and handle image processing tasks. A few commands in this readme, as well as sections of the PHP code assume Linux is being used. 
- A **dart board** securely mounted and ready for play.
- **Neon Yellow spray paint** to coat your darts for improved visibility in photos.

---

## Setting Up Your Dart Board 

To achieve accurate scoring, make sure your dart board is properly set up:

1. **Mount your dart board** securely on a wall.
2. **Lighting**: Ensure even lighting around the board to minimize shadows.
3. **Calibration**: Place your ArUco markers in each corner of the dart board.
   - Use the "classic" dictionary.
   - Markers 7, 8, 9, and 10 should be used, generated from [https://chev.me/arucogen/](https://chev.me/arucogen/)
   - Note: as our web-app uses the manual region detection method, you may need to play around with the distances of your ArUco marking for the best possible results.

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

At the end of this step, ensure that your Postgres database is up and running, such that the Python script we provide can connect to it.

---

## Cloning the Repository

```bash
git clone https://github.com/reedwrogers/Dart-Vision.git
cd dart-vision-scoring
```

Certainly! Here's the revised and complete **"Setting up the Environment"** section with clear steps and bash commands:

---

## Setting up the Environment

This project requires a Python virtual environment named `jupyter`. The PHP scripts are configured to run within this environment, so it must be activated on your Linux system.

### 1. Create and Activate the Environment

```bash
# Install virtualenv if you don't have it
pip install virtualenv

# Create the 'jupyter' environment
virtualenv jupyter

# Activate the environment
source jupyter/bin/activate
```

### 2. Install Required Dependencies

Once the environment is activated, install all required Python packages:

```bash
pip install -r requirements.txt
```

Your Python environment is now ready to run the backend scripts.

---

## Running the Application

The app runs on a local web server. I would reccomend hosting it on your Linux device via Apache, and then redirecting Apache to look into this GitHub repository as its source. Doing so will allow you to vitit the local IP address of your Linux device, and then navigate to the `Web Interface` folder to be taken to our index.html file. 

Once configured, you can visit your web app in a browser:

```
http://192.168.40.72
```

Replace that with the IP of your local server.

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
