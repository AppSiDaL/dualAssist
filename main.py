# main.py
# Importamos las librerias necesarias
# Importamos os para manejar las variables de entorno
import os

# Importamos load_dotenv para cargar las variables de entorno
from dotenv import load_dotenv

# Importamos FastAPI para crear la API
from fastapi import FastAPI

# Importamos BaseModel para tipear la entrada de la API
from pydantic import BaseModel

# Importamos datetime para obtener la fecha y hora actual
from datetime import datetime, timedelta

# Importamos psycopg2 para conectarnos a la base de datos
import psycopg2

load_dotenv()  # Cargamos las variables de entorno


# Creamos la clase Item que hereda de BaseModel para la entrada de la API
class Item(BaseModel):
    lastname: str


# Función para conectarnos a la base de datos
def conectar_bd():
    cnx = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )
    return cnx

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

class CustomLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Capturar el tipo de petición y la ruta
        method = request.method
        url = str(request.url)

        # Leer el cuerpo de la petición. Nota: Esto requiere leer el stream de la petición, lo cual puede consumir el stream.
        # Es necesario hacerlo asíncronamente y luego reconstruir el cuerpo para que la petición pueda continuar normalmente.
        body_bytes = await request.body()
        body = body_bytes.decode('utf-8')  # Asumiendo que el cuerpo es texto, ajusta la decodificación según sea necesario.

        # Imprimir los detalles
        print(f"Petición: {method} {url}")
        print(f"Cuerpo de la petición: {body}")

        # Continuar con el procesamiento normal de la petición
        response = await call_next(request)
        return response

app = FastAPI()

# Añadir el middleware personalizado a la aplicación
app.add_middleware(CustomLoggerMiddleware)

@app.get("/")
async def read_root():
    datos=get_all_datos()
    return datos
# Creamos la aplicación FastAPI
# Obtenemos las variables de entorno
HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
PORT = os.getenv("PORT")
DATABASE = os.getenv("DATABASE")


# Definimos la ruta raíz de la API
@app.post("/{numeroControl}")  # Usar el parámetro de la ruta
async def root(numeroControl: str):  # El número de control se obtiene directamente de la URL
    # Obtenemos la fecha y hora actual
    hoy = datetime.now().date()
    hora_actual = datetime.now().time()
    # Obtenemos el número de control del alumno y recortamos los espacios
    numeroControl = numeroControl.strip()
    # Consultamos si el alumno ya registro asistencia antes
    resultado = consultar_entrada(numeroControl)
    # Si el alumno ya registro asistencia antes
    if resultado:
        # Retornamos un mensaje de que el alumno ya registro asistencia antes
        return {
            "numeroControl": numeroControl,
            "fecha": hoy,
            "hora": hora_actual,
            "mensaje": "El alumno ya registro asistencia antes.",
        }
    # Si el alumno no ha registrado asistencia antes
    else:
        # Consultamos si el alumno ya registro asistencia hoy
        resultado = consultar_entrada_hoy(numeroControl)
        # Si el alumno ya registro asistencia hoy
        if resultado:
            # Insertamos el registro de salida del alumno
            insertar_dato_salida(numeroControl, hoy, hora_actual)
            # Retornamos un mensaje de que el alumno ha registrado su salida
            return {
                "numeroControl": numeroControl,
                "fecha": hoy,
                "hora": hora_actual,
                "mensaje": "El alumno ha registrdo su salida.",
            }
        else:
            # Insertamos el registro de asistencia del alumno
            insertar_dato_entrada(numeroControl, hoy, hora_actual)
            # Retornamos un mensaje de que el alumno ha registrado su asistencia
            return {
                "numeroControl": numeroControl,
                "fecha": hoy,
                "hora": hora_actual,
                "mensaje": "El alumno ha registrado su asistencia.",
            }


def consultar_entrada(numeroControl):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    hoy = datetime.now().date()
    hora_actual = datetime.now().time()
    # Calcular la hora 30 minutos antes
    hora_inicio = (datetime.now() - timedelta(minutes=30)).time()
    # Consultar si el alumno ya registro asistencia
    query = """
    SELECT * FROM asistencia
    WHERE numero_control = %s AND fecha = %s
    AND hora_entrada BETWEEN %s AND %s
    """
    cursor.execute(
        query,
        (
            numeroControl,
            str(hoy),
            str(hora_inicio),
            str(hora_actual),
        ),
    )
    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()
    return resultado


def consultar_entrada_hoy(numeroControl):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    hoy = datetime.now().date()
    # Consultar si el alumno ya registro asistencia hoy
    query = """
    SELECT * FROM asistencia
    WHERE numero_control = %s AND fecha = %s
    """
    cursor.execute(
        query,
        (
            numeroControl,
            str(hoy),
        ),
    )
    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()
    return resultado


def insertar_dato_entrada(numeroControl, fecha, hora_actual):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    # Insertar el registro de asistencia del alumno
    insert_query = (
        "INSERT INTO asistencia (numero_control,fecha,hora_entrada) VALUES (%s,%s, %s)"
    )
    cursor.execute(
        insert_query,
        (
            numeroControl,
            str(fecha),
            str(hora_actual),
        ),
    )
    conexion.commit()
    cursor.close()
    conexion.close()


def insertar_dato_salida(numeroControl, fecha, hora_actual):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    # Insertar el registro de salida del alumno
    insert_query = (
        "UPDATE asistencia SET hora_salida = %s WHERE numero_control = %s AND fecha = %s"
    )
    cursor.execute(
        insert_query,
        (
            str(hora_actual),
            numeroControl,
            str(fecha),
        ),
    )
    conexion.commit()
    cursor.close()
    conexion.close()


def get_all_datos():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    # Consultar todos los registros de asistencia
    query = """
    SELECT * FROM asistencia
    """
    cursor.execute(query)
    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()
    return resultado