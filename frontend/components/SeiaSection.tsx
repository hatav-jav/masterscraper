'use client';

import { useState } from 'react';
import DataTable from './DataTable';
import TopProjects from './TopProjects';
import EstadoChanges from './EstadoChanges';
import ScraperButton from './ScraperButton';
import LastRuns from './LastRuns';

type Tab = 'data' | 'top20' | 'changes' | 'runs';

interface SeiaSectionProps {
  refreshKey: number;
  onRefresh: () => void;
}

const TABS = [
  { id: 'data' as Tab, label: 'Report Data' },
  { id: 'top20' as Tab, label: 'Top 20 Leads' },
  { id: 'changes' as Tab, label: 'Status Changes' },
  { id: 'runs' as Tab, label: 'Latest Runs' },
];

export default function SeiaSection({ refreshKey, onRefresh }: SeiaSectionProps) {
  const [activeTab, setActiveTab] = useState<Tab>('data');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-white">SEIA</h2>
        <p className="text-zinc-400 mt-1">Environmental Impact Assessment System</p>
        
        {/* Scraper Card */}
        <div className="mt-4 inline-block">
          <ScraperButton
            source="seia"
            label="Run SEIA Scraper"
            description="Fetch latest projects"
            onComplete={onRefresh}
            compact
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-zinc-800">
        <nav className="flex gap-1">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors
                ${activeTab === tab.id
                  ? 'bg-zinc-800 text-white border-b-2 border-emerald-500'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[500px]">
        {activeTab === 'data' && (
          <DataTable key={`table-${refreshKey}`} filterSource="seia" />
        )}

        {activeTab === 'top20' && (
          <TopProjects key={`top-${refreshKey}`} />
        )}

        {activeTab === 'changes' && (
          <EstadoChanges key={`changes-${refreshKey}`} />
        )}

        {activeTab === 'runs' && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <LastRuns key={`runs-${refreshKey}`} filterSource="seia" />
          </div>
        )}
      </div>
    </div>
  );
}
