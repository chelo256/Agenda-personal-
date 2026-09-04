import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
from ..models.evidence import Evidence

class EvidenceDatabase:
    """Base de datos local para gestionar metadatos de evidencias"""
    
    def __init__(self, db_path: str = "evidence.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Inicializar la base de datos y crear tablas"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()
    
    def _create_tables(self):
        """Crear las tablas necesarias"""
        cursor = self.conn.cursor()
        
        # Tabla de evidencias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id TEXT PRIMARY KEY,
                image_path TEXT NOT NULL,
                description TEXT NOT NULL,
                problem_type TEXT NOT NULL,
                project TEXT NOT NULL,
                date TEXT NOT NULL,
                cloud_provider TEXT NOT NULL,
                cloud_path TEXT,
                tags TEXT
            )
        ''')
        
        # Tabla de configuración de nubes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cloud_configs (
                provider TEXT PRIMARY KEY,
                config TEXT NOT NULL,
                is_active INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def add_evidence(self, evidence: Evidence) -> bool:
        """Agregar una evidencia a la base de datos"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO evidence 
                (id, image_path, description, problem_type, project, date, cloud_provider, cloud_path, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                evidence.id,
                evidence.image_path,
                evidence.description,
                evidence.problem_type,
                evidence.project,
                evidence.date.isoformat(),
                evidence.cloud_provider,
                evidence.cloud_path,
                json.dumps(evidence.tags)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error agregando evidencia: {e}")
            return False
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """Obtener una evidencia por ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM evidence WHERE id = ?', (evidence_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_evidence(row)
            return None
        except Exception as e:
            print(f"Error obteniendo evidencia: {e}")
            return None
    
    def get_all_evidence(self) -> List[Evidence]:
        """Obtener todas las evidencias"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM evidence')
            rows = cursor.fetchall()
            return [self._row_to_evidence(row) for row in rows]
        except Exception as e:
            print(f"Error obteniendo evidencias: {e}")
            return []
    
    def search_evidence(self, query: str = None, date_from: datetime = None,
                       date_to: datetime = None, problem_type: str = None,
                       project: str = None, tags: List[str] = None) -> List[Evidence]:
        """Buscar evidencias con múltiples filtros"""
        try:
            cursor = self.conn.cursor()
            
            sql = "SELECT * FROM evidence WHERE 1=1"
            params = []
            
            if query:
                sql += " AND description LIKE ?"
                params.append(f"%{query}%")
            
            if date_from:
                sql += " AND date >= ?"
                params.append(date_from.isoformat())
            
            if date_to:
                sql += " AND date <= ?"
                params.append(date_to.isoformat())
            
            if problem_type:
                sql += " AND problem_type = ?"
                params.append(problem_type)
            
            if project:
                sql += " AND project = ?"
                params.append(project)
            
            if tags:
                for tag in tags:
                    sql += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_evidence(row) for row in rows]
        except Exception as e:
            print(f"Error buscando evidencias: {e}")
            return []
    
    def update_evidence(self, evidence: Evidence) -> bool:
        """Actualizar una evidencia"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE evidence SET
                image_path = ?, description = ?, problem_type = ?, 
                project = ?, date = ?, cloud_provider = ?, 
                cloud_path = ?, tags = ?
                WHERE id = ?
            ''', (
                evidence.image_path,
                evidence.description,
                evidence.problem_type,
                evidence.project,
                evidence.date.isoformat(),
                evidence.cloud_provider,
                evidence.cloud_path,
                json.dumps(evidence.tags),
                evidence.id
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando evidencia: {e}")
            return False
    
    def delete_evidence(self, evidence_id: str) -> bool:
        """Eliminar una evidencia"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM evidence WHERE id = ?', (evidence_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error eliminando evidencia: {e}")
            return False
    
    def save_cloud_config(self, provider: str, config: dict, is_active: bool = False) -> bool:
        """Guardar configuración de nube"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cloud_configs (provider, config, is_active)
                VALUES (?, ?, ?)
            ''', (provider, json.dumps(config), 1 if is_active else 0))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def get_cloud_config(self, provider: str) -> Optional[dict]:
        """Obtener configuración de nube"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT config, is_active FROM cloud_configs WHERE provider = ?', (provider,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'config': json.loads(row[0]),
                    'is_active': bool(row[1])
                }
            return None
        except Exception as e:
            print(f"Error obteniendo configuración: {e}")
            return None
    
    def get_active_cloud_config(self) -> Optional[Dict[str, dict]]:
        """Obtener configuración de nube activa"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT provider, config FROM cloud_configs WHERE is_active = 1')
            row = cursor.fetchone()
            
            if row:
                return {
                    'provider': row[0],
                    'config': json.loads(row[1])
                }
            return None
        except Exception as e:
            print(f"Error obteniendo configuración activa: {e}")
            return None
    
    def _row_to_evidence(self, row) -> Evidence:
        """Convertir fila de base de datos a objeto Evidence"""
        return Evidence(
            id=row[0],
            image_path=row[1],
            description=row[2],
            problem_type=row[3],
            project=row[4],
            date=datetime.fromisoformat(row[5]),
            cloud_provider=row[6],
            cloud_path=row[7],
            tags=json.loads(row[8]) if row[8] else []
        )
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.conn:
            self.conn.close()