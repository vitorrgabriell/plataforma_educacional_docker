CREATE DATABASE IF NOT EXISTS plataforma_educacional;

USE plataforma_educacional;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'professor') NOT NULL DEFAULT 'professor'
);

CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE aulas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    horario TIME NOT NULL,
    sala_id INT NOT NULL,
    professor_id INT,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ra VARCHAR(100) NOT NULL,
    idade INT NOT NULL,
    sala VARCHAR(100) NOT NULL,
    aula_id INT NULL,
    FOREIGN KEY (aula_id) REFERENCES aulas(id) ON DELETE SET NULL ON UPDATE CASCADE
);

