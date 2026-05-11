-- SQL Initialization for School Vehicle Management System (PostgreSQL)

-- Create database (Note: usually done outside or with separate tool)
-- CREATE DATABASE school_parking;

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    student_code VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    student_id INT,
    vehicle_type VARCHAR(20) NOT NULL, -- Simplified ENUM for SQL script
    license_plate VARCHAR(20),
    tag_id VARCHAR(50),
    color VARCHAR(30),
    brand VARCHAR(50),
    CONSTRAINT fk_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Payment Status
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    vehicle_id INT,
    month INT NOT NULL,
    year INT NOT NULL,
    is_paid BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vehicle_payment FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

-- Access Logs
CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    vehicle_id INT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    image_path VARCHAR(255),
    direction VARCHAR(10) DEFAULT 'IN',
    confidence_score FLOAT,
    CONSTRAINT fk_vehicle_log FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL
);
