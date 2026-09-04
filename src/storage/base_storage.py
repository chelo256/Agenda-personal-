from abc import ABC, abstractmethod
from typing import Optional, List
import os

class BaseStorage(ABC):
    """Clase base para conectores de almacenamiento en la nube"""
    
    def __init__(self, config: dict):
        self.config = config
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Establecer conexión con el servicio de nube"""
        pass
    
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> str:
        """Subir archivo a la nube"""
        pass
    
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Descargar archivo de la nube"""
        pass
    
    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Eliminar archivo de la nube"""
        pass
    
    @abstractmethod
    def list_files(self, folder_path: str = "") -> List[str]:
        """Listar archivos en la nube"""
        pass
    
    @abstractmethod
    def search_files(self, query: str) -> List[str]:
        """Buscar archivos en la nube"""
        pass
    
    def disconnect(self):
        """Desconectar del servicio"""
        self.is_connected = False