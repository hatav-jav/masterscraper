'use client';

import { useEffect, useState } from 'react';
import { getLeads } from '@/lib/api';

interface RawData {
  nombre?: string;
  link?: string;
  link_ficha?: string;
  titular?: string;
  tipo?: string;
  region?: string;
  comuna?: string;
  inversion_formato?: string;
  inversion_millones?: number;
  fecha_presentacion?: string;
  fecha_ingreso?: string;
  estado?: string;
  tipo_proyecto?: string;
  sector_economico?: string;
  razon_ingreso?: string;
  codigo_seia?: string;
  descripcion_completa?: string;
  industria?: string;
}

interface Lead {
  source: string;
  project_name: string;
  date: string;
  sector: string;
  description: string;
  raw_data?: RawData;
  created_at?: string;
}

type SortField = 'inversion' | 'date' | null;
type SortOrder = 'asc' | 'desc';

interface DataTableProps {
  filterSource?: string;
}

export default function DataTable({ filterSource: propFilterSource }: DataTableProps = {}) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [filterIndustria, setFilterIndustria] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>(null);
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);

  useEffect(() => {
    loadLeads();
    const interval = setInterval(loadLeads, 30000);
    return () => clearInterval(interval);
  }, []);

  // Resetear a página 1 cuando cambian filtros o sorting
  useEffect(() => {
    setCurrentPage(1);
  }, [filterIndustria, sortField, sortOrder]);

  const loadLeads = async () => {
    try {
      // Cargar un número grande para tener todos los proyectos disponibles
      // El backend tiene límite de 1000, pero podemos hacer múltiples requests si es necesario
      const data = await getLeads(10000);
      setLeads(data.leads || []);
    } catch (error) {
      console.error('Error loading leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRow = (index: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  // Filtrar por source si se especifica en props
  const sourceFilteredLeads = propFilterSource 
    ? leads.filter(lead => lead.source.toLowerCase() === propFilterSource.toLowerCase())
    : leads;

  // Obtener industrias únicas para el filtro
  const uniqueIndustrias = Array.from(
    new Set(sourceFilteredLeads.map(lead => lead.raw_data?.industria).filter(Boolean))
  ).sort();

  // Filtrar por industria
  const filteredLeads = sourceFilteredLeads.filter(lead => {
    return filterIndustria === 'all' || lead.raw_data?.industria === filterIndustria;
  });

  // Parsear fecha DD/MM/YYYY a Date
  const parseDate = (dateStr: string): Date => {
    if (!dateStr) return new Date(0);
    const parts = dateStr.split('/');
    if (parts.length === 3) {
      // DD/MM/YYYY -> YYYY-MM-DD
      const [day, month, year] = parts;
      return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    }
    return new Date(dateStr);
  };

  // Ordenar leads
  const sortedLeads = [...filteredLeads].sort((a, b) => {
    if (!sortField) return 0;
    
    if (sortField === 'inversion') {
      const aVal = a.raw_data?.inversion_millones ?? 0;
      const bVal = b.raw_data?.inversion_millones ?? 0;
      return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
    } else if (sortField === 'date') {
      const aDate = parseDate(a.date || '');
      const bDate = parseDate(b.date || '');
      return sortOrder === 'desc' ? bDate.getTime() - aDate.getTime() : aDate.getTime() - bDate.getTime();
    }
    
    return 0;
  });

  // Paginación
  const totalPages = Math.ceil(sortedLeads.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedLeads = sortedLeads.slice(startIndex, endIndex);

  const formatCurrency = (value?: number | string) => {
    if (!value) return 'N/A';
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return value;
    return `US$ ${num.toLocaleString('es-CL')} MM`;
  };

  const getIndustriaColor = (industria?: string) => {
    // Colores sincronizados con backend/category_rules.py
    const colors: Record<string, string> = {
      'Energía Renovable': 'bg-green-500/20 text-green-400 border border-green-500/50',
      'BESS': 'bg-blue-500/20 text-blue-400 border border-blue-500/50',
      'Infraestructura Eléctrica': 'bg-orange-500/20 text-orange-400 border border-orange-500/50',
      'Minería': 'bg-gray-600/20 text-gray-300 border border-gray-500/50',
      'Agua': 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50',
      'Desarrollo de Proyectos': 'bg-purple-500/20 text-purple-400 border border-purple-500/50',
      'Infraestructura y Construcción': 'bg-amber-700/20 text-amber-500 border border-amber-600/50',
      'Otros': 'bg-gray-400/20 text-gray-400 border border-gray-400/50',
    };
    return colors[industria || ''] || colors['Otros'];
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return (
        <svg className="w-4 h-4 text-dark-dim" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    return sortOrder === 'desc' ? (
      <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    );
  };

  if (loading) {
    return (
      <div className="card p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <span className="ml-3 text-dark-muted">Loading leads...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      {/* Filters Header */}
      <div className="px-4 py-3 border-b border-border bg-surface-elevated/50">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-dark-muted">
              {sortedLeads.length} projects
              {sortedLeads.length !== leads.length && ` (${leads.length} total)`}
            </span>
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            {/* Items per page */}
            <div className="flex items-center gap-2">
              <label className="text-xs text-dark-dim uppercase tracking-wider">Per page:</label>
              <select
                value={itemsPerPage}
                onChange={(e) => {
                  setItemsPerPage(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="select text-sm py-1"
              >
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>

            {/* Filter by Industria */}
            <div className="flex items-center gap-2">
              <label className="text-xs text-dark-dim uppercase tracking-wider">Industry:</label>
              <select
                value={filterIndustria}
                onChange={(e) => setFilterIndustria(e.target.value)}
                className="select text-sm py-1"
              >
                <option value="all">All</option>
                {uniqueIndustrias.map(industria => (
                  <option key={industria} value={industria}>{industria}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="table-header">
              <th className="w-10 px-3 py-3"></th>
              <th className="px-3 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider">
                Project
              </th>
              <th className="px-3 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider">
                Industry
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider cursor-pointer hover:text-dark-text transition-colors"
                onClick={() => handleSort('date')}
              >
                <div className="flex items-center gap-1">
                  Date
                  <SortIcon field="date" />
                </div>
              </th>
              <th className="px-3 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider">
                Region
              </th>
              <th 
                className="px-3 py-3 text-left text-xs font-semibold text-dark-muted uppercase tracking-wider cursor-pointer hover:text-dark-text transition-colors"
                onClick={() => handleSort('inversion')}
              >
                <div className="flex items-center gap-1">
                  Investment
                  <SortIcon field="inversion" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {paginatedLeads.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-dark-muted">
                  <div className="flex flex-col items-center gap-2">
                    <svg className="w-12 h-12 text-dark-dim" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p>No leads available</p>
                    <p className="text-sm text-dark-dim">Run a scraper to get data</p>
                  </div>
                </td>
              </tr>
            ) : (
              paginatedLeads.map((lead, localIndex) => {
                const globalIndex = startIndex + localIndex;
                return (
                <>
                  {/* Main Row */}
                  <tr 
                    key={`row-${globalIndex}`}
                    onClick={() => toggleRow(globalIndex)}
                    className={`
                      cursor-pointer transition-colors
                      ${expandedRows.has(globalIndex) 
                        ? 'table-row-expanded' 
                        : 'table-row'
                      }
                    `}
                  >
                    <td className="px-3 py-3">
                      <button className="p-1 rounded hover:bg-border transition-transform">
                        <svg 
                          className={`w-4 h-4 text-dark-muted transition-transform duration-200 ${expandedRows.has(globalIndex) ? 'rotate-90' : ''}`} 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </td>
                    <td className="px-3 py-3">
                      <span className="font-medium text-dark-text line-clamp-2">
                        {lead.project_name}
                      </span>
                    </td>
                    <td className="px-3 py-3">
                      {lead.raw_data?.industria && (
                        <span className={`badge ${getIndustriaColor(lead.raw_data.industria)}`}>
                          {lead.raw_data.industria}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-sm text-dark-muted whitespace-nowrap font-mono">
                      {lead.date}
                    </td>
                    <td className="px-3 py-3 text-sm text-dark-muted">
                      {lead.raw_data?.region || 'N/A'}
                    </td>
                    <td className="px-3 py-3 text-sm font-medium text-dark-text whitespace-nowrap">
                      {formatCurrency(lead.raw_data?.inversion_millones)}
                    </td>
                  </tr>
                  
                  {/* Expanded Row */}
                  {expandedRows.has(globalIndex) && (
                    <tr key={`expanded-${globalIndex}`} className="bg-surface-elevated/50">
                      <td colSpan={6} className="px-3 py-0">
                        <div className="py-4 pl-10 pr-4 animate-fadeIn">
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {/* General Info */}
                            <div className="space-y-3">
                              <h4 className="font-semibold text-dark-text flex items-center gap-2 text-sm">
                                <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                General Information
                              </h4>
                              <div className="space-y-2 text-sm">
                                <div>
                                  <span className="text-dark-dim">Owner: </span>
                                  <span className="text-dark-text font-medium">
                                    {lead.raw_data?.titular || 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-dark-dim">SEIA Code: </span>
                                  <span className="text-dark-text font-mono">
                                    {lead.raw_data?.codigo_seia || 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-dark-dim">Type: </span>
                                  <span className="text-dark-text">
                                    {lead.raw_data?.tipo || lead.sector || 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-dark-dim">Status: </span>
                                  <span className={`badge ${
                                    lead.raw_data?.estado?.toLowerCase().includes('aprobado') 
                                      ? 'badge-success'
                                      : lead.raw_data?.estado?.toLowerCase().includes('rechazado')
                                        ? 'badge-error'
                                        : 'badge-warning'
                                  }`}>
                                    {lead.raw_data?.estado || 'N/A'}
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Location & Dates */}
                            <div className="space-y-3">
                              <h4 className="font-semibold text-dark-text flex items-center gap-2 text-sm">
                                <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                Location & Dates
                              </h4>
                              <div className="space-y-2 text-sm">
                                <div>
                                  <span className="text-dark-dim">Region: </span>
                                  <span className="text-dark-text">
                                    {lead.raw_data?.region || 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-dark-dim">Comuna: </span>
                                  <span className="text-dark-text">
                                    {lead.raw_data?.comuna || 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-dark-dim">Submitted: </span>
                                  <span className="text-dark-text font-mono">
                                    {lead.raw_data?.fecha_presentacion || lead.date || 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-dark-dim">Entry: </span>
                                  <span className="text-dark-text font-mono">
                                    {lead.raw_data?.fecha_ingreso || 'N/A'}
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Investment & Actions */}
                            <div className="space-y-3">
                              <h4 className="font-semibold text-dark-text flex items-center gap-2 text-sm">
                                <svg className="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Investment & Links
                              </h4>
                              <div className="space-y-2 text-sm">
                                <div>
                                  <span className="text-dark-dim">Investment: </span>
                                  <span className="text-dark-text font-semibold">
                                    {formatCurrency(lead.raw_data?.inversion_millones)}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-dark-dim">Entry Reason: </span>
                                  <span className="text-dark-text">
                                    {lead.raw_data?.razon_ingreso || 'N/A'}
                                  </span>
                                </div>
                              </div>

                              {/* Action Buttons */}
                              <div className="flex flex-wrap gap-2 pt-2">
                                {lead.raw_data?.link_ficha && (
                                  <a
                                    href={lead.raw_data.link_ficha}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    onClick={(e) => e.stopPropagation()}
                                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-medium transition-colors"
                                  >
                                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                    </svg>
                                    View SEIA File
                                  </a>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Full Description */}
                          {lead.raw_data?.descripcion_completa && (
                            <div className="mt-4 pt-4 border-t border-border">
                              <h4 className="font-semibold text-dark-text mb-2 flex items-center gap-2 text-sm">
                                <svg className="w-4 h-4 text-primary-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                Project Description
                              </h4>
                              <p className="text-sm text-dark-muted whitespace-pre-wrap">
                                {lead.raw_data.descripcion_completa}
                              </p>
                            </div>
                          )}

                          {/* Message if no description */}
                          {!lead.raw_data?.descripcion_completa && lead.source === 'SEIA' && (
                            <div className="mt-4 pt-4 border-t border-border">
                              <p className="text-sm text-dark-dim italic flex items-center gap-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                To view the full project description, click on &quot;View SEIA File&quot;
                              </p>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {sortedLeads.length > 0 && (
        <div className="px-4 py-3 border-t border-border bg-surface-elevated/50">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="text-sm text-dark-muted">
              Showing {startIndex + 1} to {Math.min(endIndex, sortedLeads.length)} of {sortedLeads.length} projects
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1.5 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-300 text-sm font-medium hover:bg-zinc-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Previous
              </button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                        currentPage === pageNum
                          ? 'bg-emerald-600 text-white'
                          : 'bg-zinc-800 border border-zinc-700 text-zinc-300 hover:bg-zinc-700'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1.5 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-300 text-sm font-medium hover:bg-zinc-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
              >
                Next
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
