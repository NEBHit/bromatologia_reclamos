import os
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile
from sqlmodel import Session

from models.constante import EstadoReclamoEnum
from models.reclamo_model import ReclamoModel
from models.detalleAlimentoReclamo_model import DetalleAlimentoReclamoModel
from models.evidencia_model import EvidenciaModel
from models.historialEstadoReclamo_model import HistorialEstadoReclamoModel
from models.reclamoCategoria_model import ReclamoCategoriaModel


from repositories import reclamo_repo
from repositories import reclamoCategoria_repo
from repositories import detalleAlimentoReclamo_repo
from repositories import historialEstadoReclamo_repo
from repositories import evidencia_repo

class ReclamoService:
    def __init__(self, session: Session):
        self.session = session

    def listar_todos(self) -> List[ReclamoModel]:
        return reclamo_repo.get_all(self.session)

    def listar_todos_conEstado(self):
        return reclamo_repo.get_all_Estado(self.session)

    def obtener_por_id(self, id_reclamo: int) -> Optional[ReclamoModel]:
        return reclamo_repo.get_by_id(self.session, id_reclamo)

    def obtener_por_expediente(self, nro_expediente: str) -> Optional[ReclamoModel]:
        return reclamo_repo.get_by_expediente(self.session, nro_expediente)

    def listar_por_estado(self, id_estado: int) -> List[ReclamoModel]:
        return reclamo_repo.get_by_estado(self.session, id_estado)

    def verificar_reclamo_duplicado_reciente(self, calle: str, minutos: int = 2) -> Optional[ReclamoModel]:
        if not calle:
            return None
        return reclamo_repo.buscar_duplicado_reciente(session=self.session, calle=calle, minutos=minutos)

    async def nuevo_reclamo_publico(
        self,
        nuevo_Reclamo: ReclamoModel,
        detalleAlimento: list[dict],
        categorias: list[dict],
        archivos_evidencias: List[UploadFile],
        upload_dir: str = "static/uploads"
    ) -> ReclamoModel:
        """
        Coordina la creación completa del reclamo público:
        1. Persiste el ReclamoModel principal vía reclamo_repo.
        2. Registra el Historial inicial vía historialEstadoReclamo_repo.
        3. Persiste Detalles de Alimentos si existen vía detalleAlimentoReclamo_repo.
        4. Guarda archivos físicos y crea registros vía evidencia_repo.
        """
        # Persistir reclamo en BD a través de su repositorio
        reclamo_guardado = reclamo_repo.create(self.session, nuevo_Reclamo)

        # Persistir relación N a N (Reclamo <-> Categorías) 
        if categorias:
            for cat in categorias:
                reclamoCategoria = ReclamoCategoriaModel(
                    idReclamo = reclamo_guardado.idReclamo,
                    idCategoria = cat.idCategoria
                )
                reclamoCategoria_repo.create(self.session, reclamoCategoria)

        # Registrar entrada inicial en el Historial a través de su repositorio
        historial_inicial = HistorialEstadoReclamoModel(
            idReclamo=reclamo_guardado.idReclamo,
            idEstadoReclamo=EstadoReclamoEnum.RECIBIDO,
            idUsuario=reclamo_guardado.idUsuarioCrear,
            fechaHistorial=datetime.now(),
            observaciones="Ingreso del reclamo desde el portal web municipal"
        )

        historialEstadoReclamo_repo.create(self.session, historial_inicial)

        # Procesar y persistir Detalle de Alimento si se proporcionó
        if detalleAlimento:
            for item in detalleAlimento:
                nuevo_detalle_alimento = DetalleAlimentoReclamoModel(
                    idReclamo=reclamo_guardado.idReclamo,
                    productoNombreMarca=item["productoNombreMarca"],
                    fechaVencimiento=item["fechaVencimiento"],
                    nroLote=item["nroLote"],
                    estadoConservacion=item["estadoConservacion"]
                )
                detalleAlimentoReclamo_repo.create(self.session, nuevo_detalle_alimento)

        
        # Procesar y guardar evidencias físicas y en BD a través de evidencia_repo
        archivos_validos = [f for f in archivos_evidencias if f and f.filename and f.filename.strip()]
        if archivos_validos:
            os.makedirs(upload_dir, exist_ok=True)
            for archivo in archivos_validos:
                contenido = await archivo.read()
                tamano = len(contenido)
                nombre_guardado = f"{reclamo_guardado.idReclamo}_{archivo.filename}"
                ruta_fisica = os.path.join(upload_dir, nombre_guardado)

                with open(ruta_fisica, "wb") as f:
                    f.write(contenido)

                nueva_evidencia = EvidenciaModel(
                    idReclamo=reclamo_guardado.idReclamo,
                    nombreArchivo=archivo.filename,
                    rutaAlmacenamiento=ruta_fisica,
                    tipoMime=archivo.content_type or "application/octet-stream",
                    tamanoBytes=tamano,
                    fechaSubida=datetime.now()
                )
                evidencia_repo.create(self.session, nueva_evidencia)

        return reclamo_guardado

    def cambiar_estado(
        self, 
        id_reclamo: int, 
        nuevo_estado_id: int, 
        id_usuario: Optional[int] = None, 
        observaciones: Optional[str] = None
    ) -> Optional[ReclamoModel]:
        reclamo = reclamo_repo.get_by_id(self.session, id_reclamo)
        if not reclamo:
            return None

        reclamo.idEstadoActual = nuevo_estado_id
        if id_usuario:
            reclamo.idUsuarioModificar = id_usuario
        reclamo.fechaMod = datetime.now()
        reclamo_actualizado = reclamo_repo.update(self.session, reclamo)

        historial = HistorialEstadoReclamoModel(
            idReclamo=id_reclamo,
            idEstadoReclamo=nuevo_estado_id,
            idUsuario=id_usuario,
            fechaHistorial=datetime.now(),
            observaciones=observaciones or f"Cambio de estado a {nuevo_estado_id}"
        )
        historialEstadoReclamo_repo.create(self.session, historial)

        return reclamo_actualizado

    def eliminar_reclamo(self, id_reclamo: int) -> str:
        reclamo = reclamo_repo.get_by_id(self.session, id_reclamo)
        if not reclamo:
            return "no existe"
        
        reclamo_repo.delete(self.session, reclamo)
        return "exito"