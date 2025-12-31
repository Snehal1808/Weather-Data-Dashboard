CREATE DATABASE weather_db;
USE weather_db;

CREATE TABLE weather_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50),
    temperature FLOAT,
    humidity INT,
    pressure INT,
    description VARCHAR(100),
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
