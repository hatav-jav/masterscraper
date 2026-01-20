'use client';

import { useState } from 'react';
import { scrapeSource } from '@/lib/api';

interface ScraperButtonProps {
  source: string;
  label: string;
  description?: string;
}

export default function ScraperButton({ source, label, description }: ScraperButtonProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleClick = async () => {
    setLoading(true);
    setResult(null);
    
    try {
      const response = await scrapeSource(source);
      setResult({
        success: true,
        message: `✅ ${response.total_leads} leads obtenidos`,
      });
    } catch (error: any) {
      setResult({
        success: false,
        message: `❌ Error: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 dark:bg-gray-700 rounded-lg p-4 mb-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-white">{label}</h3>
          {description && (
            <p className="text-sm text-gray-400 mt-1">{description}</p>
          )}
        </div>
        <div className="flex flex-col items-end gap-2">
          <button
            onClick={handleClick}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
          >
            {loading ? 'Ejecutando...' : 'Run'}
          </button>
          {result && (
            <span className={`text-sm ${result.success ? 'text-green-400' : 'text-red-400'}`}>
              {result.message}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

