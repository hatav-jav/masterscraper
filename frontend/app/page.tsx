'use client';

import { useState, useEffect } from 'react';
import ScraperButton from '@/components/ScraperButton';
import DataTable from '@/components/DataTable';
import LastRuns from '@/components/LastRuns';
import { scrapeAll, generateReport } from '@/lib/api';

export default function Home() {
  const [runningAll, setRunningAll] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRunAll = async () => {
    setRunningAll(true);
    try {
      await scrapeAll();
      setRefreshKey(prev => prev + 1);
    } catch (error) {
      console.error('Error running all scrapers:', error);
    } finally {
      setRunningAll(false);
    }
  };

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const result = await generateReport();
      if (result.status === 'success') {
        alert('Reporte generado y enviado exitosamente');
      } else {
        alert(result.message || 'Error al generar reporte');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error al generar reporte');
    } finally {
      setGeneratingReport(false);
    }
  };

  const handleScraperComplete = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-dark">
      {/* Header */}
      <header className="border-b border-border bg-surface/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-dark-text tracking-tight">Master Scraper</h1>
                <p className="text-sm text-dark-muted">
                  Project Financing & M&A Lead Monitor
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Action Buttons Section */}
        <section className="mb-8">
          <div className="flex flex-wrap gap-3">
            {/* Run All Scrapers Button */}
            <button
              onClick={handleRunAll}
              disabled={runningAll}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {runningAll ? (
                <>
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Running All...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Run All Scrapers
                </>
              )}
            </button>

            {/* Generate Report Button */}
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-surface-elevated border border-border text-dark-text font-medium hover:bg-border transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generatingReport ? (
                <>
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Generate AI Report
                </>
              )}
            </button>
          </div>
        </section>

        {/* Last Runs Section */}
        <LastRuns key={`runs-${refreshKey}`} />

        {/* Individual Scrapers Section */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-4 text-dark-text">Individual Scrapers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ScraperButton
              source="seia"
              label="SEIA"
              description="Environmental Impact Assessment System"
              onComplete={handleScraperComplete}
            />
            <ScraperButton
              source="hechos_esenciales"
              label="Hechos Esenciales"
              description="Material Facts & Events"
              onComplete={handleScraperComplete}
            />
          </div>
        </section>

        {/* Data Table Section */}
        <section>
          <h2 className="text-lg font-semibold mb-4 text-dark-text">Report Data</h2>
          <DataTable key={`table-${refreshKey}`} />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-dark-dim text-sm">
            Master Scraper Dashboard • Built for personal use
          </p>
        </div>
      </footer>
    </div>
  );
}
