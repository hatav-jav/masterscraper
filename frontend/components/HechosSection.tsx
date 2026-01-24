'use client';

import { useState, useEffect } from 'react';
import ScraperButton from './ScraperButton';
import LastRuns from './LastRuns';
import { getLeads } from '@/lib/api';

interface HechosSectionProps {
  refreshKey: number;
  onRefresh: () => void;
}

interface Lead {
  source: string;
  project_name: string;
  date: string;
  sector: string;
  description: string;
  raw_data?: Record<string, unknown>;
}

export default function HechosSection({ refreshKey, onRefresh }: HechosSectionProps) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
  }, [refreshKey]);

  const loadLeads = async () => {
    try {
      setLoading(true);
      const data = await getLeads(500);
      // Filter only hechos_esenciales
      const hechosLeads = (data.leads || []).filter(
        (lead: Lead) => lead.source === 'hechos_esenciales'
      );
      setLeads(hechosLeads);
    } catch (error) {
      console.error('Error loading leads:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-white">Hechos Esenciales</h2>
        <p className="text-zinc-400 mt-1">Material Facts & Events from CMF</p>
      </div>

      {/* Scraper Section */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Run Scraper</h3>
        <ScraperButton
          source="hechos_esenciales"
          label="Hechos Esenciales"
          description="Scrapes material facts from CMF (Comisión para el Mercado Financiero)"
          onComplete={() => {
            onRefresh();
            loadLeads();
          }}
        />
      </div>

      {/* Recent Runs */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Runs</h3>
        <LastRuns key={`runs-${refreshKey}`} filterSource="hechos_esenciales" />
      </div>

      {/* Data Table */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Report Data
          <span className="ml-2 text-sm font-normal text-zinc-500">
            ({leads.length} records)
          </span>
        </h3>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
          </div>
        ) : leads.length === 0 ? (
          <div className="text-center py-12 text-zinc-500">
            <svg className="w-12 h-12 mx-auto mb-4 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>No data available</p>
            <p className="text-sm mt-1">Run the scraper to get data</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase">Project</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-500 uppercase">Sector</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {leads.slice(0, 50).map((lead, index) => (
                  <tr key={index} className="hover:bg-zinc-800/50 transition-colors">
                    <td className="px-4 py-3 text-sm text-white">
                      {lead.project_name}
                    </td>
                    <td className="px-4 py-3 text-sm text-zinc-400 font-mono">
                      {lead.date}
                    </td>
                    <td className="px-4 py-3 text-sm text-zinc-400">
                      {lead.sector || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {leads.length > 50 && (
              <p className="text-center text-sm text-zinc-500 py-4">
                Showing 50 of {leads.length} records
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
