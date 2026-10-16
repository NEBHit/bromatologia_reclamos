from typing import List, Optional
from sqlmodel import Session
from models.recurrenciaHecho_model import RecurrenciaHechoModel
from repositories import recurrenciaHecho_repo
from repositories import reclamo_repo


class RecurrenciaHechoService:
    def __init__(self, session: Session):
        self.session = session

    def listar_recurrencias(self) -> List[RecurrenciaHechoModel]:
        return recurrenciaHecho_repo.get_all(self.session)

    def obtener_por_id(self, idRecurrenciaHecho: int) -> Optional[RecurrenciaHechoModel]:
        return recurrenciaHecho_repo.get_by_id(self.session, idRecurrenciaHecho)

    def crear_recurrencia(self, nueva_recurrencia: RecurrenciaHechoModel) -> RecurrenciaHechoModel:
        return recurrenciaHecho_repo.create(self.session, nueva_recurrencia)

    def actualizar_localidad(self, update_recurrencia: RecurrenciaHechoModel) -> Optional[RecurrenciaHechoModel]:
        recurrencia = recurrenciaHecho_repo.get_by_id(self.session, update_recurrencia.idRecurrenciaHecho)
        if not recurrencia:
            return None
        recurrencia.nombre = update_recurrencia.nombre
        recurrencia.codPostal = update_recurrencia.codPostal
        return recurrenciaHecho_repo.update(self.session, recurrencia)

    def eliminar_recurrencia(self, idRecurrenciaHecho: int) -> str:
        recurrencia = recurrenciaHecho_repo.get_by_id(self.session, idRecurrenciaHecho)
        if not recurrencia:
            return "no existe"

        # Validación de integridad: no borrar si existen reclamos asociados
        reclamos_vinculados = [
            r for r in reclamo_repo.get_all(self.session) 
            if r.idRecurrenciaHecho == idRecurrenciaHecho
        ]
        if reclamos_vinculados:
            return "relacionado"

        recurrenciaHecho_repo.delete(self.session, recurrencia)
        return "exito"