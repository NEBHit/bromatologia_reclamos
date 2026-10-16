from fastapi import Depends
from typing import Annotated
from sqlmodel import Session, create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

import os

load_dotenv()

# Obtener las variables del entorno
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT","3306")
DB_NAME = os.getenv("DB_NAME")

# URL de conexión corregida
url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(url, echo=True, pool_pre_ping = True, pool_recycle=280)  # Agregué `echo=True` para depuración


# Dependencia de sesión
def get_session():
    with Session(engine) as session:
        yield session

session_dep = Annotated[Session, Depends(get_session)]