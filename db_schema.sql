CREATE DATABASE secure_access_db;

CREATE TABLE accounts_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(50),
    org_id INT,
    is_verified BOOLEAN DEFAULT FALSE,
    otp_code VARCHAR(6),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE organization (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    admin_id INT,
    payment_status VARCHAR(20),
    FOREIGN KEY (admin_id) REFERENCES accounts_user(id)
);

CREATE TABLE file_storage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT,
    org_id INT,
    filename VARCHAR(255),
    path VARCHAR(255),
    qr_code VARCHAR(255),
    shared_link VARCHAR(255),
    FOREIGN KEY (owner_id) REFERENCES accounts_user(id)
);

CREATE TABLE chat_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE anomaly_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    event VARCHAR(255),
    risk_score FLOAT,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
