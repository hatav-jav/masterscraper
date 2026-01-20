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

def get_latest_leads(limit: int = 100) -> List[Dict]:
    """Obtiene los últimos leads."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
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
