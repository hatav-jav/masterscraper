'use client';

import { useState } from 'react';
import { scrapeSource } from '@/lib/api';

interface ScraperButtonProps {
  source: string;
  label: string;
  description?: string;
  onComplete?: () => void;
}

export default function ScraperButton({ source, label, description, onComplete }: ScraperButtonProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string; count?: number } | null>(null);

  const handleClick = async () => {
    setLoading(true);
    setResult(null);
    
    try {
      const response = await scrapeSource(source);
      setResult({
        success: true,
        message: 'Completed',
        count: response.total_leads,
      });
      onComplete?.();
    } catch (error: any) {
      setResult({
        success: false,
        message: error.message || 'Error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card p-4 transition-all hover:border-primary/30">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-seia">{label}</span>
          </div>
          {description && (
            <p className="text-sm text-dark-muted">{description}</p>
          )}
          
          {/* Result indicator */}
          {result && (
            <div className={`mt-3 flex items-center gap-2 text-sm ${result.success ? 'text-green-400' : 'text-red-400'}`}>
              {result.success ? (
                <>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                  </svg>
                  <span>{result.count} leads obtained</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
                  </svg>
                  <span>{result.message}</span>
                </>
              )}
            </div>
          )}
        </div>
        
        <button
          onClick={handleClick}
          disabled={loading}
          className="ml-4 px-4 py-2 rounded-lg bg-surface-elevated border border-border text-dark-text text-sm font-medium hover:bg-border transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Running...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              </svg>
              Run
            </>
          )}
        </button>
      </div>
    </div>
  );
}
