from typing import List, Optional
from sqlmodel import Session
from models.estadoReclamo_model import EstadoReclamoModel
from repositories import estadoReclamo_repo, reclamo_repo


class EstadoReclamoService:
    def __init__(self, session: Session):
        self.session = session

    def listar_estados(self) -> List[EstadoReclamoModel]:
        return estadoReclamo_repo.get_all(self.session)

    def obtener_por_id(self, id_estado: int) -> Optional[EstadoReclamoModel]:
        return estadoReclamo_repo.get_by_id(self.session, id_estado)

    def crear_estado(self, nuevo_estado: EstadoReclamoModel) -> EstadoReclamoModel:
        return estadoReclamo_repo.create(self.session, nuevo_estado)

    def actualizar_estado(self, update_estado: EstadoReclamoModel) -> Optional[EstadoReclamoModel]:
        estado = estadoReclamo_repo.get_by_id(self.session, update_estado.idEstadoReclamo)
        if not estado:
            return None
        estado.nombre = update_estado.nombre
        estado.descripcion = update_estado.descripcion
        return estadoReclamo_repo.update(self.session, estado)

    def eliminar_estado(self, id_estado: int) -> str:
        estado = estadoReclamo_repo.get_by_id(self.session, id_estado)
        if not estado:
            return "no existe"

        reclamos_con_este_estado = reclamo_repo.get_by_estado(self.session, id_estado)
        if reclamos_con_este_estado:
            return "relacionado"

        estadoReclamo_repo.delete(self.session, estado)
        return "exito"