CREATE DATABASE regista;

use regista;

CREATE TABLE job (
    jid INT PRIMARY KEY,
    name VARCHAR(40) UNIQUE,
    type VARCHAR(10),
    queue VARCHAR(20),
    author VARCHAR(10),
    cron VARCHAR(30),
    max_run_count INT,
)

CREATE TABLE job_schedule (
    jid INT PRIMARY KEY,
    jdate DATE,
    status INT DEFAULT 0,
    scheduled_time DATETIME DEFAULT NULL,
    start_time DATETIME DEFAULT NULL,
    end_time DATETIME DEFAULT NULL,
    run_count INT DEFAULT 0,
    max_run_count INT,
)

CREATE TABLE job_schedule_hist (
    id INT PRIMARY KEY AUTOINCREMENT,
    jid INT,
    jdate DATE,
    status INT,
    start_time DATETIME,
    end_time DATETIME,
    run_count INT,
)

CREATE TABLE job_dependent (
    id INT PRIMARY KEY AUTOINCREMENT,
    jid INT,
    dependent_jid INT,
)