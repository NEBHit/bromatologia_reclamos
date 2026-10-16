from sqlmodel import Session
from typing import List, Optional
from models.inspector_model import InspectorModel
from repositories import inspector_repo
from repositories import reclamo_repo

class InspectorService:
    def __init__(self, session: Session):
        self.session = session

    def listar_inspectores(self) -> List[InspectorModel]:
        return inspector_repo.get_all(self.session)  

    def obtener_inspector_por_id(self, id: int) -> Optional[InspectorModel]:
        return inspector_repo.get_by_id(self.session, id)

    def crear_inspector(self, nuevoInspector: InspectorModel) -> InspectorModel:
        return inspector_repo.create(self.session, nuevoInspector)

    def actualizar_inspector(self, updateInspector: InspectorModel) -> Optional[InspectorModel]:
        inspector = inspector_repo.get_by_id(self.session, updateInspector.idInspector)
        if not inspector:
            return None
        inspector.nombre = updateInspector.nombre
        inspector.apellido = updateInspector.apellido
        return inspector_repo.update(self.session, inspector)

    def eliminar_inspector(self, id: int) -> bool:
        inspector = inspector_repo.get_by_id(self.session, id)
        if not inspector:
            return "no existe"  # No encontrado

        expediente = reclamo_repo.get_by_idEstadoInspeccion(self.session, id) 

        if expediente is not None:
            return "relacionado"  #existen expedeintes con el estado
        else:
            inspector_repo.delete(self.session, id)
            return "exito"