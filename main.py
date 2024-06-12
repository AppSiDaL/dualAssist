# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import psycopg2

load_dotenv()  # take environment variables from .env.


class Item(BaseModel):
    lastname: str


def conectar_bd():
    # Establecemos la conexión con la base de datos PostgreSQL
    cnx = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )
    return cnx


app = FastAPI()
HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
PORT = os.getenv("PORT")
DATABASE = os.getenv("DATABASE")


@app.post("/")
async def root(item: Item):
    current_time = datetime.now().isoformat()
    numeroControl = item.lastname.strip()
    print(numeroControl)
    insertar_datos(numeroControl, current_time)
    return {"numeroControl": numeroControl, "time": current_time}


def insertar_datos(numeroControl, time):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    insert_query = "INSERT INTO asistencia (numero_control,entrada) VALUES (%s, %s)"
    cursor.execute(
        insert_query,
        (
            numeroControl,
            time,
        ),
    )
    conexion.commit()
    cursor.close()
    conexion.close()