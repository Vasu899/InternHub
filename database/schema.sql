CREATE DATABASE IF NOT EXISTS internhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE internhub;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(190) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    security_answer_1 VARCHAR(255) NULL,
    security_answer_2 VARCHAR(255) NULL,
    security_answer_3 VARCHAR(255) NULL,
    education_status VARCHAR(40) NOT NULL DEFAULT 'Currently studying',
    study_year VARCHAR(30),
    field_of_interest VARCHAR(80) NOT NULL DEFAULT 'Any field',
    is_admin TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(160) NOT NULL,
    company VARCHAR(160) NOT NULL,
    field VARCHAR(80) NOT NULL DEFAULT 'Other',
    description TEXT NOT NULL,
    skills VARCHAR(500) NOT NULL DEFAULT '',
    eligibility VARCHAR(250) NOT NULL DEFAULT 'Open to students',
    pay_type VARCHAR(30) NOT NULL DEFAULT 'Unspecified',
    stipend VARCHAR(80) NOT NULL DEFAULT 'Not specified',
    work_mode VARCHAR(30) NOT NULL DEFAULT 'Remote',
    location VARCHAR(120) NOT NULL DEFAULT 'Not specified',
    duration VARCHAR(80) NOT NULL DEFAULT 'Not specified',
    application_url VARCHAR(500) NOT NULL,
    deadline DATE NULL,
    beginner_friendly TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS user_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill VARCHAR(60) NOT NULL,
    UNIQUE KEY unique_user_skill (user_id, skill),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS saved_internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    internship_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_saved (user_id, internship_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    internship_id INT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Applied',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_application (user_id, internship_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);
