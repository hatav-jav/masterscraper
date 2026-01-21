import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from backend.config import DB_PATH
import os

def init_db():
    """Crea las tablas si no existen."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de leads
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            project_name TEXT,
            date TEXT,
            sector TEXT,
            description TEXT,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de runs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            total_leads INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    
    # Tabla de cambios de estado
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estado_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            codigo_seia TEXT,
            project_name TEXT,
            estado_anterior TEXT,
            estado_nuevo TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            seen BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def save_leads(source: str, leads: List[Dict]) -> int:
    """Guarda leads en la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    saved_count = 0
    for lead in leads:
        cursor.execute('''
            INSERT INTO leads (source, project_name, date, sector, description, raw_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            source,
            lead.get('project_name', ''),
            lead.get('date', ''),
            lead.get('sector', ''),
            lead.get('description', ''),
            json.dumps(lead.get('raw_data', {}))
        ))
        saved_count += 1
    
    conn.commit()
    conn.close()
    return saved_count

def create_run(source: str) -> int:
    """Crea un nuevo run y retorna su ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO runs (source, status)
        VALUES (?, ?)
    ''', (source, 'running'))
    
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id

def update_run(run_id: int, status: str, total_leads: int = 0):
    """Actualiza el estado de un run."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE runs
        SET status = ?, total_leads = ?, completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, total_leads, run_id))
    
    conn.commit()
    conn.close()

def get_latest_leads(limit: int = 500, sort_by: str = None, sort_order: str = 'desc') -> List[Dict]:
    """Obtiene los ultimos leads."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query simple sin ordenamiento complejo
    cursor.execute('''
        SELECT source, project_name, date, sector, description, raw_data, created_at
        FROM leads
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    leads = []
    for row in rows:
        leads.append({
            'source': row['source'],
            'project_name': row['project_name'],
            'date': row['date'],
            'sector': row['sector'],
            'description': row['description'],
            'raw_data': json.loads(row['raw_data']) if row['raw_data'] else {},
            'created_at': row['created_at']
        })
    
    return leads

def get_leads_by_source(source: str, limit: int = 100) -> List[Dict]:
    """Obtiene leads filtrados por fuente."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT source, project_name, date, sector, description, raw_data, created_at
        FROM leads
        WHERE source = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (source, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    leads = []
    for row in rows:
        leads.append({
            'source': row['source'],
            'project_name': row['project_name'],
            'date': row['date'],
            'sector': row['sector'],
            'description': row['description'],
            'raw_data': json.loads(row['raw_data']) if row['raw_data'] else {},
            'created_at': row['created_at']
        })
    
    return leads

def get_all_leads_for_report() -> List[Dict]:
    """Obtiene todos los leads recientes para generar reporte."""
    return get_latest_leads(limit=500)


def get_existing_project_names(source: str) -> set:
    """Obtiene los nombres de proyectos existentes para una fuente específica."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT project_name FROM leads WHERE source = ?
    ''', (source,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return {row[0] for row in rows if row[0]}


def get_existing_seia_codes() -> set:
    """Obtiene los códigos SEIA de proyectos ya scrapeados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar tanto 'seia' como 'SEIA' por si acaso
    cursor.execute('''
        SELECT raw_data FROM leads WHERE LOWER(source) = 'seia'
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    codes = set()
    for row in rows:
        if row[0]:
            try:
                data = json.loads(row[0])
                codigo = data.get('codigo_seia')
                if codigo:
                    codes.add(str(codigo))
            except:
                pass
    
    return codes


def get_existing_seia_projects() -> Dict[str, Dict]:
    """
    Obtiene los proyectos SEIA existentes con su estado actual.
    Retorna dict: {codigo_seia: {lead_id, estado, project_name, raw_data}}
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, project_name, raw_data FROM leads WHERE LOWER(source) = 'seia'
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    projects = {}
    for row in rows:
        if row['raw_data']:
            try:
                data = json.loads(row['raw_data'])
                codigo = data.get('codigo_seia')
                if codigo:
                    projects[str(codigo)] = {
                        'lead_id': row['id'],
                        'project_name': row['project_name'],
                        'estado': data.get('estado', ''),
                        'raw_data': data
                    }
            except:
                pass
    
    return projects


def update_lead_estado(lead_id: int, nuevo_estado: str, raw_data: dict):
    """Actualiza el estado de un lead existente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Actualizar raw_data con el nuevo estado
    raw_data['estado'] = nuevo_estado
    
    # Actualizar también la descripción
    description = f"Titular: {raw_data.get('titular', 'N/A')}. Región: {raw_data.get('region', 'N/A')}, {raw_data.get('comuna', 'N/A')}. Inversión: {raw_data.get('inversion_formato', 'N/A')}. Estado: {nuevo_estado}."
    
    cursor.execute('''
        UPDATE leads
        SET raw_data = ?, description = ?
        WHERE id = ?
    ''', (json.dumps(raw_data), description, lead_id))
    
    conn.commit()
    conn.close()


def save_estado_change(lead_id: int, codigo_seia: str, project_name: str, 
                       estado_anterior: str, estado_nuevo: str):
    """Guarda un registro de cambio de estado."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO estado_changes (lead_id, codigo_seia, project_name, estado_anterior, estado_nuevo)
        VALUES (?, ?, ?, ?, ?)
    ''', (lead_id, codigo_seia, project_name, estado_anterior, estado_nuevo))
    
    conn.commit()
    conn.close()


def get_recent_estado_changes(limit: int = 20) -> List[Dict]:
    """Obtiene los cambios de estado recientes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, lead_id, codigo_seia, project_name, estado_anterior, estado_nuevo, detected_at, seen
        FROM estado_changes
        ORDER BY detected_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    changes = []
    for row in rows:
        changes.append({
            'id': row['id'],
            'lead_id': row['lead_id'],
            'codigo_seia': row['codigo_seia'],
            'project_name': row['project_name'],
            'estado_anterior': row['estado_anterior'],
            'estado_nuevo': row['estado_nuevo'],
            'detected_at': row['detected_at'],
            'seen': bool(row['seen']),
            'is_aprobado': 'aprobado' in (row['estado_nuevo'] or '').lower()
        })
    
    return changes


def mark_estado_changes_seen(change_ids: List[int]):
    """Marca cambios de estado como vistos."""
    if not change_ids:
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    placeholders = ','.join('?' * len(change_ids))
    cursor.execute(f'''
        UPDATE estado_changes SET seen = 1 WHERE id IN ({placeholders})
    ''', change_ids)
    
    conn.commit()
    conn.close()


def get_all_leads_for_markdown() -> List[Dict]:
    """Obtiene todos los leads con información completa para exportar a markdown."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, source, project_name, date, sector, description, raw_data, created_at
        FROM leads
        ORDER BY source, created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    leads = []
    for row in rows:
        raw_data = json.loads(row['raw_data']) if row['raw_data'] else {}
        leads.append({
            'id': row['id'],
            'source': row['source'],
            'project_name': row['project_name'],
            'date': row['date'],
            'sector': row['sector'],
            'description': row['description'],
            'raw_data': raw_data,
            'created_at': row['created_at']
        })
    
    return leads

def get_recent_runs(limit: int = 10) -> List[Dict]:
    """Obtiene el historial reciente de ejecuciones de scrapers."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, source, status, total_leads, started_at, completed_at
        FROM runs
        ORDER BY started_at DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    runs = []
    for row in rows:
        runs.append({
            'id': row['id'],
            'source': row['source'],
            'status': row['status'],
            'total_leads': row['total_leads'],
            'started_at': row['started_at'],
            'completed_at': row['completed_at']
        })
    
    return runs


def clear_all_data():
    """Elimina todos los datos de leads, runs y estado_changes."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM leads')
    cursor.execute('DELETE FROM runs')
    cursor.execute('DELETE FROM estado_changes')
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'message': 'Todos los datos han sido eliminados'
    }