'use client';

import { useState, useEffect } from 'react';
import { getEstadoChanges } from '@/lib/api';

interface EstadoChange {
  id: number;
  lead_id: number;
  codigo_seia: string;
  project_name: string;
  estado_anterior: string;
  estado_nuevo: string;
  detected_at: string;
  seen: boolean;
  is_aprobado: boolean;
}

export default function EstadoChanges() {
  const [changes, setChanges] = useState<EstadoChange[]>([]);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    loadChanges();
    const interval = setInterval(loadChanges, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadChanges = async () => {
    try {
      const data = await getEstadoChanges(10);
      setChanges(data.changes || []);
    } catch (error) {
      console.error('Error loading estado changes:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr + 'Z');
    return date.toLocaleString('es-CL', {
      timeZone: 'America/Santiago',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return null;
  }

  if (changes.length === 0) {
    return null;
  }

  return (
    <section className="mb-6">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setCollapsed(!collapsed)}
      >
        <h2 className="text-lg font-semibold text-dark-text flex items-center gap-2">
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 text-xs font-bold">
            {changes.length}
          </span>
          Status Changes Detected
          <svg 
            className={`w-4 h-4 text-dark-muted transition-transform ${collapsed ? '' : 'rotate-180'}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </h2>
      </div>
      
      {!collapsed && (
        <div className="mt-3 space-y-2 animate-fadeIn">
          {changes.map((change) => (
            <div 
              key={change.id}
              className={`card p-3 border-l-4 ${
                change.is_aprobado 
                  ? 'border-l-green-500 bg-green-500/5' 
                  : 'border-l-amber-500 bg-amber-500/5'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {change.is_aprobado && (
                      <span className="badge badge-success text-xs">
                        APROBADO
                      </span>
                    )}
                    <span className="font-medium text-dark-text truncate">
                      {change.project_name}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-dark-dim line-through">
                      {change.estado_anterior}
                    </span>
                    <svg className="w-4 h-4 text-dark-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                    <span className={`font-medium ${change.is_aprobado ? 'text-green-400' : 'text-amber-400'}`}>
                      {change.estado_nuevo}
                    </span>
                  </div>
                </div>
                <span className="text-xs text-dark-dim whitespace-nowrap">
                  {formatDate(change.detected_at)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
