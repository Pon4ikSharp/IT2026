-- Дві прості таблиці для обліку документів

CREATE TABLE IF NOT EXISTS document_types (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS documents (
    document_id SERIAL PRIMARY KEY,
    number VARCHAR(50) NOT NULL,
    type_id INTEGER NOT NULL REFERENCES document_types(type_id),
    content TEXT NOT NULL,
    date DATE NOT NULL,
    completion_status VARCHAR(20) NOT NULL DEFAULT 'не виконано'
        CHECK (completion_status IN ('не виконано', 'в процесі', 'виконано'))
);

-- Приклади типів документів з заняття
INSERT INTO document_types (type_name)
VALUES ('Наказ'), ('Звіт'), ('Лист')
ON CONFLICT (type_name) DO NOTHING;
