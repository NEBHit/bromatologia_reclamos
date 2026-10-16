import os
import shutil
import re
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile

# Carpeta base en la raíz del proyecto: bromatologia_reclamos/uploads/documentacion
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads" / "documentacion"

# Extensiones permitidas (JPG, PNG, PDF, MP4, etc.)
EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".pdf", ".mp4", ".webp"}


def sanitizar_nombre(nombre: str) -> str:
    """Limpia caracteres especiales y espacios en el nombre original."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', nombre)


def guardar_evidencias_reclamo(id_reclamo: int, archivos: list[UploadFile]) -> list[dict]:
    """
    Crea la carpeta /uploads/documentacion/{id_reclamo}/ y almacena los archivos.
    Retorna la lista de diccionarios con las propiedades que espera EvidenciaModel.
    """
    if not archivos:
        return []

    # Crear directorio si no existe: /uploads/documentacion/<id_reclamo>
    carpeta_reclamo = UPLOAD_DIR / str(id_reclamo)
    carpeta_reclamo.mkdir(parents=True, exist_ok=True)

    archivos_guardados = []

    for archivo in archivos:
        if not archivo or not archivo.filename or not archivo.filename.strip():
            continue

        ext = Path(archivo.filename).suffix.lower()
        if ext not in EXTENSIONES_PERMITIDAS:
            continue

        nombre_original = sanitizar_nombre(archivo.filename)
        # Prefijo único para evitar sobreescrituras si suben archivos con el mismo nombre
        nombre_guardado = f"{uuid4().hex[:8]}_{nombre_original}"
        ruta_completa = carpeta_reclamo / nombre_guardado

        # Guardar en disco
        try:
            with open(ruta_completa, "wb") as buffer:
                shutil.copyfileobj(archivo.file, buffer)
        finally:
            archivo.file.close()

        # Ruta relativa uniforme para guardar en la BD y servir estáticamente
        ruta_relativa = f"/uploads/documentacion/{id_reclamo}/{nombre_guardado}".replace("\\", "/")

        archivos_guardados.append({
            "nombreArchivo": archivo.filename,
            "rutaAlmacenamiento": ruta_relativa,
            "tipoMime": archivo.content_type or "application/octet-stream",
            "tamanoBytes": ruta_completa.stat().st_size
        })

    return archivos_guardados