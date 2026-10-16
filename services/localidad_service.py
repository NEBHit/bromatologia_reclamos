from typing import List, Optional
from sqlmodel import Session
from models.localidad_model import LocalidadModel
from repositories import localidad_repo
from repositories import reclamo_repo


class LocalidadService:
    def __init__(self, session: Session):
        self.session = session

    def listar_localidades(self) -> List[LocalidadModel]:
        return localidad_repo.get_all(self.session)

    def obtener_por_id(self, idLocalidad: int) -> Optional[LocalidadModel]:
        return localidad_repo.get_by_id(self.session, idLocalidad)

    def crear_localidad(self, nueva_localidad: LocalidadModel) -> LocalidadModel:
        return localidad_repo.create(self.session, nueva_localidad)

    def actualizar_localidad(self, update_localidad: LocalidadModel) -> Optional[LocalidadModel]:
        localidad = localidad_repo.get_by_id(self.session, update_localidad.idLocalidad)
        if not localidad:
            return None
        localidad.nombre = update_localidad.nombre
        localidad.codPostal = update_localidad.codPostal
        return localidad_repo.update(self.session, localidad)

    def eliminar_localidad(self, idLocalidad: int) -> str:
        localidad = localidad_repo.get_by_id(self.session, idLocalidad)
        if not localidad:
            return "no existe"

        # Validación de integridad: no borrar si existen reclamos asociados
        reclamos_vinculados = [
            r for r in reclamo_repo.get_all(self.session) 
            if r.idLocalidad == idLocalidad
        ]
        if reclamos_vinculados:
            return "relacionado"

        localidad_repo.delete(self.session, localidad)
        return "exito"