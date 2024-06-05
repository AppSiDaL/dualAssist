# main.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

class Item(BaseModel):
    lastname: str

app = FastAPI()
DATABASE_URL = os.getenv("DB_URL")
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Asistencia(Base):
    __tablename__ = "asistencia"

    id = Column(Integer, primary_key=True, index=True)
    numeroControl = Column(String)
    time = Column(DateTime)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
@app.post("/")
async def root(item: Item):
    current_time = datetime.now()
    asistencia = Asistencia(numeroControl=item.lastname, time=current_time)
    session = SessionLocal()
    session.add(asistencia)
    session.commit()
    session.refresh(asistencia)
    return {
        "numeroControl": asistencia.numeroControl,
        "time": asistencia.time.isoformat()
    }