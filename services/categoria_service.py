from typing import List, Optional
from sqlmodel import Session
from models.categoria_model import CategoriaModel
from repositories import categoria_repo, reclamo_repo


class CategoriaService:
    def __init__(self, session: Session):
        self.session = session

    def listar_categorias(self) -> List[CategoriaModel]:
        return categoria_repo.get_all(self.session)
    
    def listar_categoriasSoloSeleccionadas(self, ) -> List[CategoriaModel]:
            return categoria_repo.get_all(self.session)
    
    def listar_categoriasSoloSeleccionadas(self, ids: List[int]) -> List[CategoriaModel]:
        """Retorna las categorías seleccionadas por el usuario."""
        # Se filtran solo valores enteros válidos por seguridad
        ids_limpios = [int(i) for i in ids if str(i).isdigit()]
        return categoria_repo.get_all_idsSelect(self.session, ids_limpios)
    
    def listar_activas(self) -> List[CategoriaModel]:
        return categoria_repo.get_activas(self.session)

    def obtener_por_id(self, id_categoria: int) -> Optional[CategoriaModel]:
        return categoria_repo.get_by_id(self.session, id_categoria)

    def crear_categoria(self, nueva_cat: CategoriaModel) -> CategoriaModel:
        return categoria_repo.create(self.session, nueva_cat)

    def actualizar_categoria(self, update_cat: CategoriaModel) -> Optional[CategoriaModel]:
        cat = categoria_repo.get_by_id(self.session, update_cat.idCategoria)
        if not cat:
            return None
        cat.nombre = update_cat.nombre
        cat.requiereDetalle = update_cat.requiereDetalle
        cat.orden = update_cat.orden
        cat.activa = update_cat.activa
        return categoria_repo.update(self.session, cat)

    def eliminar_categoria(self, id_categoria: int) -> str:
        cat = categoria_repo.get_by_id(self.session, id_categoria)
        if not cat:
            return "no existe"

        reclamos_asociados = [
            r for r in reclamo_repo.get_all(self.session) 
            if r.idCategoria == id_categoria
        ]
        if reclamos_asociados:
            return "relacionado"

        categoria_repo.delete(self.session, cat)
        return "exito"