import os
import time
from datetime import datetime

import psycopg2
from flask import Flask

app = Flask(__name__)

# Credenciales entregadas por variables de entorno (definidas en docker-compose.yml)
DB_HOST = os.environ.get("DB_HOST", "db_container")
DB_NAME = os.environ.get("DB_NAME", "visitas_db")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres_pass")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    """Crea la tabla de visitas si no existe."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS visitas (
            id SERIAL PRIMARY KEY,
            fecha_hora TIMESTAMP NOT NULL
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()

    # Registra la visita actual
    cur.execute("INSERT INTO visitas (fecha_hora) VALUES (%s);", (datetime.now(),))
    conn.commit()

    # Cuenta el total acumulado de visitas (persistente gracias al volumen de Postgres)
    cur.execute("SELECT COUNT(*) FROM visitas;")
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    return f"""
    <html>
    <head><title>VZeta - App de Visitas</title></head>
    <body style="font-family: Arial, sans-serif; text-align:center; margin-top:60px;">
        <h1>🚀 App VZeta - Stack Dockerizado</h1>
        <p>NGINX (reverse proxy) &rarr; Flask &rarr; PostgreSQL</p>
        <h2>Total de visitas registradas: {total}</h2>
        <p>Última visita: {datetime.now()}</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    # Reintentos porque el contenedor de la app puede levantar antes que la BD esté lista
    for intento in range(15):
        try:
            init_db()
            print("Conexión a PostgreSQL establecida y tabla verificada.")
            break
        except Exception as e:
            print(f"Esperando a la base de datos... intento {intento + 1}: {e}")
            time.sleep(3)

    app.run(host="0.0.0.0", port=5000)
