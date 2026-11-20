"""Проста система обліку документів на Flask і PostgreSQL."""

import os
from datetime import date

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()
app = Flask(__name__)


def connect_db():
    # Параметри підключення беремо з файлу .env
    return psycopg2.connect(
        database=os.getenv("DB_NAME", "documents_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/document-types", methods=["GET"])
def get_document_types():
    connection = connect_db()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT type_id, type_name FROM document_types ORDER BY type_id")
        types = [
            {"type_id": row[0], "type_name": row[1]}
            for row in cursor.fetchall()
        ]
        cursor.close()
        return jsonify(types)
    finally:
        connection.close()


@app.route("/api/documents", methods=["GET"])
def get_documents():
    connection = connect_db()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT d.document_id, d.number, t.type_name,
                   d.content, d.date, d.completion_status
            FROM documents d
            JOIN document_types t ON d.type_id = t.type_id
            ORDER BY d.date DESC, d.document_id DESC
        """)
        documents = []
        for row in cursor.fetchall():
            documents.append({
                "document_id": row[0],
                "number": row[1],
                "type_name": row[2],
                "content": row[3],
                "date": row[4].isoformat(),
                "completion_status": row[5],
            })
        cursor.close()
        return jsonify(documents)
    finally:
        connection.close()


@app.route("/api/documents", methods=["POST"])
def add_document():
    data = request.get_json(silent=True) or {}
    number = str(data.get("number", "")).strip()
    content = str(data.get("content", "")).strip()
    status = data.get("completion_status", "не виконано")

    try:
        type_id = int(data.get("type_id"))
        document_date = date.fromisoformat(data.get("date", ""))
    except (TypeError, ValueError):
        return jsonify({"error": "Перевірте тип і дату документа"}), 400

    valid_statuses = ("не виконано", "в процесі", "виконано")
    if not number or not content or type_id < 1 or status not in valid_statuses:
        return jsonify({"error": "Заповніть усі поля правильно"}), 400
    if len(number) > 50:
        return jsonify({"error": "Номер документа занадто довгий"}), 400

    connection = connect_db()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO documents (number, type_id, content, date, completion_status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING document_id
        """, (number, type_id, content, document_date, status))
        document_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        return jsonify({"id": document_id, "message": "Документ додано"}), 201
    finally:
        connection.close()


@app.route("/api/documents/<int:document_id>/status", methods=["PATCH"])
def update_status(document_id):
    data = request.get_json(silent=True) or {}
    status = data.get("completion_status")
    if status not in ("не виконано", "в процесі", "виконано"):
        return jsonify({"error": "Невідомий статус"}), 400

    connection = connect_db()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE documents SET completion_status = %s
            WHERE document_id = %s
        """, (status, document_id))
        found = cursor.rowcount > 0
        connection.commit()
        cursor.close()
        if not found:
            return jsonify({"error": "Документ не знайдено"}), 404
        return jsonify({"message": "Статус змінено"})
    finally:
        connection.close()


@app.route("/api/documents/<int:document_id>", methods=["DELETE"])
def delete_document(document_id):
    connection = connect_db()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM documents WHERE document_id = %s", (document_id,))
        found = cursor.rowcount > 0
        connection.commit()
        cursor.close()
        if not found:
            return jsonify({"error": "Документ не знайдено"}), 404
        return jsonify({"message": "Документ видалено"})
    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True)
