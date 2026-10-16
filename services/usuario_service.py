import hashlib
from datetime import datetime
from typing import List, Optional, Union
from sqlmodel import Session
from models.usuario_model import UsuarioModel
from repositories import usuario_repo
from repositories import reclamo_repo


class UsuarioService:
    def __init__(self, session: Session):
        self.session = session

    # ==========================
    # MÉTODOS DE SEGURIDAD
    # ==========================
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash SHA-256 de la contraseña (o texto plano según legado)."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def authenticate(self, usuario: str, clave: str) -> Union[UsuarioModel, str, bool, None]:
        """
        Valida credenciales según los casos esperados por usuario_router:
        - None: Usuario no encontrado
        - "NO ACTIVO": Usuario inhabilitado
        - False: Clave errónea
        - UsuarioModel: Credenciales válidas
        """
        user = usuario_repo.get_by_usuarioName(self.session, usuario.strip().upper())
        if not user:
            return None

        if not user.activo:
            return "NO ACTIVO"

        # Compara tanto con hash SHA-256 como en texto plano directo
        clave_hasheada = self.hash_password(clave)
        if user.clave != clave and user.clave != clave_hasheada:
            return False

        return user

    def actualizar_fechaUltimoLogin(self, usuario: UsuarioModel) -> UsuarioModel:
        """Actualiza la marca temporal del último inicio de sesión exitoso."""
        usuario.fechaUltimoLogin = datetime.now()
        return usuario_repo.update(self.session, usuario)

    def actualizar_clave(self, usuario: UsuarioModel) -> Optional[UsuarioModel]:
        """Persiste el cambio de contraseña."""
        user_db = usuario_repo.get_by_idUsuario(self.session, usuario.idUsuario)
        if not user_db:
            return None
        user_db.clave = usuario.clave
        return usuario_repo.update(self.session, user_db)

    # ==========================
    # OPERACIONES CRUD
    # ==========================
    def listar_usuarios(self) -> List[UsuarioModel]:
        return usuario_repo.get_all(self.session)

    def obtener_por_id(self, id_usuario: int) -> Optional[UsuarioModel]:
        return usuario_repo.get_by_idUsuario(self.session, id_usuario)

    def obtener_por_nombre_usuario(self, usuario: str) -> Optional[UsuarioModel]:
        return usuario_repo.get_by_usuarioName(self.session, usuario)

    def crear_usuario(self, nuevo_usuario: UsuarioModel) -> UsuarioModel:
        # Asegurar usuario en mayúsculas y clave procesada
        nuevo_usuario.usuario = nuevo_usuario.usuario.upper()
        if nuevo_usuario.clave:
            nuevo_usuario.clave = self.hash_password(nuevo_usuario.clave)
        return usuario_repo.create(self.session, nuevo_usuario)

    def actualizar_usuario(self, update_usuario: UsuarioModel) -> Optional[UsuarioModel]:
        usuario = usuario_repo.get_by_idUsuario(self.session, update_usuario.idUsuario)
        if not usuario:
            return None
        usuario.usuario = update_usuario.usuario.upper()
        usuario.idRol = update_usuario.idRol
        usuario.activo = update_usuario.activo
        if update_usuario.clave:
            usuario.clave = self.hash_password(update_usuario.clave)
        return usuario_repo.update(self.session, usuario)

    def eliminar_usuario(self, id_usuario: int) -> str:
        usuario = usuario_repo.get_by_idUsuario(self.session, id_usuario)
        if not usuario:
            return "no existe"

        reclamos_asociados = [
            r for r in reclamo_repo.get_all(self.session) 
            if r.idInspector == id_usuario or r.idUsuarioCrear == id_usuario
        ]
        if reclamos_asociados:
            return "relacionado"

        usuario_repo.delete(self.session, usuario)
        return "exito"