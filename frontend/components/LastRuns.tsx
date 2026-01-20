'use client';

import { useState, useEffect } from 'react';
import { getRuns } from '@/lib/api';

interface Run {
  id: number;
  source: string;
  status: string;
  total_leads: number;
  started_at: string;
  completed_at: string | null;
}

export default function LastRuns() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRuns();
    const interval = setInterval(loadRuns, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadRuns = async () => {
    try {
      const data = await getRuns(10);
      setRuns(data.runs || []);
    } catch (error) {
      console.error('Error loading runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleString('es-CL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1.5 badge badge-success">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
            </svg>
            Completed
          </span>
        );
      case 'running':
        return (
          <span className="inline-flex items-center gap-1.5 badge badge-warning">
            <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Running
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center gap-1.5 badge badge-error">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
            </svg>
            Error
          </span>
        );
      default:
        return (
          <span className="badge bg-dark-dim/20 text-dark-muted">
            {status}
          </span>
        );
    }
  };

  const getSourceLabel = (source: string) => {
    switch (source.toLowerCase()) {
      case 'seia':
        return 'SEIA';
      case 'hechos_esenciales':
        return 'Hechos Esenciales';
      default:
        return source;
    }
  };

  if (loading) {
    return (
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4 text-dark-text">Latest Runs</h2>
        <div className="card p-6">
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <span className="ml-3 text-dark-muted">Loading runs...</span>
          </div>
        </div>
      </section>
    );
  }

  if (runs.length === 0) {
    return (
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4 text-dark-text">Latest Runs</h2>
        <div className="card p-6">
          <p className="text-center text-dark-muted py-4">No hay ejecuciones registradas</p>
        </div>
      </section>
    );
  }

  // Mostrar solo los últimos 5 runs en el resumen
  const recentRuns = runs.slice(0, 5);

  return (
    <section className="mb-8">
      <h2 className="text-lg font-semibold mb-4 text-dark-text">Latest Runs</h2>
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="table-header">
                <th className="px-4 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider">
                  Source
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider">
                  Last Run
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider">
                  Total Leads
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {recentRuns.map((run) => (
                <tr key={run.id} className="table-row">
                  <td className="px-4 py-3">
                    <span className="font-medium text-dark-text">
                      {getSourceLabel(run.source)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-dark-muted font-mono">
                      {formatDate(run.completed_at || run.started_at)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {getStatusBadge(run.status)}
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-2xl font-semibold text-primary-light">
                      {run.total_leads}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
