from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import json

@dataclass
class Evidence:
    """Modelo para representar una evidencia de problema"""
    id: str
    image_path: str
    description: str
    problem_type: str
    project: str
    date: datetime
    cloud_provider: str
    cloud_path: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para almacenamiento"""
        return {
            'id': self.id,
            'image_path': self.image_path,
            'description': self.description,
            'problem_type': self.problem_type,
            'project': self.project,
            'date': self.date.isoformat(),
            'cloud_provider': self.cloud_provider,
            'cloud_path': self.cloud_path,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Evidence':
        """Crear instancia desde diccionario"""
        return cls(
            id=data['id'],
            image_path=data['image_path'],
            description=data['description'],
            problem_type=data['problem_type'],
            project=data['project'],
            date=datetime.fromisoformat(data['date']),
            cloud_provider=data['cloud_provider'],
            cloud_path=data.get('cloud_path'),
            tags=data.get('tags', [])
        )
    
    def matches_search(self, query: str = None, date_from: datetime = None, 
                       date_to: datetime = None, problem_type: str = None,
                       project: str = None, tags: List[str] = None) -> bool:
        """Verificar si la evidencia coincide con los criterios de búsqueda"""
        if query and query.lower() not in self.description.lower():
            return False
        
        if date_from and self.date < date_from:
            return False
        
        if date_to and self.date > date_to:
            return False
        
        if problem_type and self.problem_type != problem_type:
            return False
        
        if project and self.project != project:
            return False
        
        if tags and not any(tag in self.tags for tag in tags):
            return False
        
        return True