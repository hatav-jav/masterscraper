'use client';

import { useState, useEffect } from 'react';
import { getTopProjects } from '@/lib/api';

// Colores por categoría (sincronizados con backend)
const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  'Energía Renovable': { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/50' },
  'BESS': { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/50' },
  'Infraestructura Eléctrica': { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/50' },
  'Minería': { bg: 'bg-gray-600/20', text: 'text-gray-300', border: 'border-gray-500/50' },
  'Agua': { bg: 'bg-cyan-500/20', text: 'text-cyan-400', border: 'border-cyan-500/50' },
  'Desarrollo de Proyectos': { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/50' },
  'Infraestructura y Construcción': { bg: 'bg-amber-700/20', text: 'text-amber-500', border: 'border-amber-600/50' },
  'Otros': { bg: 'bg-gray-400/20', text: 'text-gray-400', border: 'border-gray-400/50' },
};

interface TopProject {
  ranking: number;
  project_name: string;
  score_total: number;
  score_inversion: number;
  score_estado: number;
  explicacion: string;
  raw_data: {
    inversion_millones?: number;
    estado?: string;
    industria?: string;
    categorias_secundarias?: string[];
    titular?: string;
    region?: string;
    tipo?: string;
    link_ficha?: string;
  };
}

export default function TopProjects() {
  const [projects, setProjects] = useState<TopProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await getTopProjects(20);
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Error loading top projects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const getCategoryStyle = (category: string) => {
    return CATEGORY_COLORS[category] || CATEGORY_COLORS['Otros'];
  };

  const formatInversion = (value: number | undefined) => {
    if (!value) return 'N/A';
    return `US$ ${value.toLocaleString('es-CL', { maximumFractionDigits: 1 })} MM`;
  };

  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4 text-white">Top 20 Proyectos</h2>
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-zinc-800 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4 text-white">Top 20 Proyectos</h2>
        <p className="text-zinc-500 text-sm">No hay proyectos que cumplan los criterios de selección.</p>
        <p className="text-zinc-600 text-xs mt-2">
          Criterios: Estado válido + Inversión >= USD 25 MM (o >= USD 10 MM para BESS/Minería/Infra. Eléctrica)
        </p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">Top 20 Proyectos</h2>
        <button
          onClick={loadProjects}
          className="text-xs text-zinc-400 hover:text-white transition-colors"
        >
          Actualizar
        </button>
      </div>
      
      <p className="text-zinc-500 text-xs mb-4">
        Seleccionados por estado + inversión. Score máximo: 55 pts.
      </p>

      <div className="space-y-2">
        {projects.map((project) => {
          const catStyle = getCategoryStyle(project.raw_data.industria || 'Otros');
          const isExpanded = expandedId === project.ranking;
          
          return (
            <div 
              key={project.ranking}
              className="border border-zinc-800 rounded-lg overflow-hidden"
            >
              {/* Row principal */}
              <div 
                className="flex items-center gap-3 p-3 hover:bg-zinc-800/50 cursor-pointer transition-colors"
                onClick={() => setExpandedId(isExpanded ? null : project.ranking)}
              >
                {/* Ranking */}
                <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center text-sm font-bold text-zinc-300">
                  {project.ranking}
                </div>
                
                {/* Nombre + Score */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-white truncate">{project.project_name}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={`text-xs px-2 py-0.5 rounded ${catStyle.bg} ${catStyle.text} ${catStyle.border} border`}>
                      {project.raw_data.industria || 'Otros'}
                    </span>
                    <span className="text-xs text-zinc-500">{project.explicacion}</span>
                  </div>
                </div>
                
                {/* Inversión */}
                <div className="text-right">
                  <div className="text-sm font-medium text-emerald-400">
                    {formatInversion(project.raw_data.inversion_millones)}
                  </div>
                  <div className="text-xs text-zinc-500">
                    Score: {project.score_total}
                  </div>
                </div>

                {/* Chevron */}
                <svg 
                  className={`w-4 h-4 text-zinc-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              {/* Detalles expandidos */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-1 border-t border-zinc-800 bg-zinc-900/50">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-zinc-500">Estado</p>
                      <p className="text-white">{project.raw_data.estado || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-zinc-500">Tipo</p>
                      <p className="text-white">{project.raw_data.tipo || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-zinc-500">Titular</p>
                      <p className="text-white truncate">{project.raw_data.titular || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-zinc-500">Región</p>
                      <p className="text-white">{project.raw_data.region || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-zinc-500">Score Inversión</p>
                      <p className="text-white">{project.score_inversion} pts</p>
                    </div>
                    <div>
                      <p className="text-zinc-500">Score Estado</p>
                      <p className="text-white">{project.score_estado} pts</p>
                    </div>
                    {project.raw_data.categorias_secundarias && project.raw_data.categorias_secundarias.length > 0 && (
                      <div className="col-span-2">
                        <p className="text-zinc-500">Categorías secundarias</p>
                        <div className="flex gap-1 mt-1">
                          {project.raw_data.categorias_secundarias.map((cat, i) => {
                            const secStyle = getCategoryStyle(cat);
                            return (
                              <span key={i} className={`text-xs px-2 py-0.5 rounded ${secStyle.bg} ${secStyle.text} ${secStyle.border} border`}>
                                {cat}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                  {project.raw_data.link_ficha && (
                    <a
                      href={project.raw_data.link_ficha}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 mt-3 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      Ver ficha SEIA
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </a>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
