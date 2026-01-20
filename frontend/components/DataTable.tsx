'use client';

import { useEffect, useState } from 'react';
import { getLeads } from '@/lib/api';

interface Lead {
  source: string;
  project_name: string;
  date: string;
  sector: string;
  description: string;
  created_at?: string;
}

export default function DataTable() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
    // Refresh cada 30 segundos
    const interval = setInterval(loadLeads, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadLeads = async () => {
    try {
      const data = await getLeads(100);
      setLeads(data.leads || []);
    } catch (error) {
      console.error('Error loading leads:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-gray-400">
        Cargando leads...
      </div>
    );
  }

  return (
    <div className="bg-gray-800 dark:bg-gray-700 rounded-lg p-4 overflow-x-auto">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">Latest Leads</h3>
        <p className="text-sm text-gray-400">Total: {leads.length} leads</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="py-2 px-4 text-gray-400 font-medium">Source</th>
              <th className="py-2 px-4 text-gray-400 font-medium">Project Name</th>
              <th className="py-2 px-4 text-gray-400 font-medium">Date</th>
              <th className="py-2 px-4 text-gray-400 font-medium">Sector</th>
              <th className="py-2 px-4 text-gray-400 font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            {leads.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-gray-400">
                  No hay leads disponibles
                </td>
              </tr>
            ) : (
              leads.map((lead, index) => (
                <tr key={index} className="border-b border-gray-700 hover:bg-gray-700/50">
                  <td className="py-2 px-4 text-white">{lead.source}</td>
                  <td className="py-2 px-4 text-white font-medium">{lead.project_name}</td>
                  <td className="py-2 px-4 text-gray-300">{lead.date}</td>
                  <td className="py-2 px-4 text-gray-300">{lead.sector}</td>
                  <td className="py-2 px-4 text-gray-300">{lead.description}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

