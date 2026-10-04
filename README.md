# 🌐 Herz - Friend Connector

Herz is a full-stack web application built with **Flask**, **MySQL**, and **JavaScript** designed to connect users based on shared interests, allow them to send connection requests, and chat in real-time. It features an interactive community photo grid, dynamic background themes, and a clean glassmorphism UI.

---

## 🚀 Features

* **User Authentication:** Secure sign-up and login sessions with interest selection for Day-1 matching.
* **Smart Recommendations:** Automatically suggests other users who share similar interests.
* **Connection System:** Send and manage friend connection requests.
* **Real-time Messaging:** Chat live with connected friends with auto-scrolling message history.
* **Community Gallery:** A vibrant photo grid showcasing memories and community highlights.
* **Dynamic UI:** Rotating background imagery, clean layout styling, and custom brand assets.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, PyMySQL, Werkzeug
* **Database:** MySQL
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla).

---
Store index.html in a folder and name it "templates"

Required Python Libraries
->pip install flask flask-cors pymysql
->pip install pymysql flask flask-cors

## ⚙️ Setup and Installation
Steps to Run
In PowerShell,
run: python init_db.py

Then run: python app.py

Go to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser!
### 1. Clone the Repository
```bash

For Creation of the database:
Push in PowerShell
"mysql -u root -p"

Then,
"CREATE DATABASE friend_db";
Your new database will be generated

Then, 
"USE friend_db;"
you will be switched to the friend_db database.

-- Create Database
CREATE DATABASE IF NOT EXISTS friend_db;
USE friend_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Interests Table
CREATE TABLE IF NOT EXISTS user_interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    interest VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Friendships Table
CREATE TABLE IF NOT EXISTS friendships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    friend_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

Your database will be created.
