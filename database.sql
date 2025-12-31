CREATE DATABASE weather_db;
USE weather_db;

CREATE TABLE daily_weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    temperature FLOAT,
    humidity INT,
    description VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
