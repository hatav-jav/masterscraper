'use client';

import { useState } from 'react';
import Sidebar, { Section } from '@/components/Sidebar';
import GeneralSection from '@/components/GeneralSection';
import SeiaSection from '@/components/SeiaSection';
import HechosSection from '@/components/HechosSection';
import AuthGuard from '@/components/AuthGuard';

function Dashboard() {
  const [activeSection, setActiveSection] = useState<Section>('general');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Sidebar */}
      <Sidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        collapsed={sidebarCollapsed}
        onCollapsedChange={setSidebarCollapsed}
      />

      {/* Main Content */}
      <main className={`min-h-screen transition-all duration-300 ${sidebarCollapsed ? 'ml-16' : 'ml-60'}`}>
        <div className="p-8">
          {activeSection === 'general' && (
            <GeneralSection onRefresh={handleRefresh} />
          )}

          {activeSection === 'seia' && (
            <SeiaSection
              refreshKey={refreshKey}
              onRefresh={handleRefresh}
            />
          )}

          {activeSection === 'hechos' && (
            <HechosSection
              refreshKey={refreshKey}
              onRefresh={handleRefresh}
            />
          )}
        </div>
      </main>
    </div>
  );
}

// Proteger la página con AuthGuard
export default function Home() {
  return (
    <AuthGuard>
      <Dashboard />
    </AuthGuard>
  );
}
