'use client';

import { useState } from 'react';
import { generateReport } from '@/lib/api';

export default function ReportButton() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleClick = async () => {
    setLoading(true);
    setResult(null);
    
    try {
      const response = await generateReport();
      setResult({
        success: response.status === 'success',
        message: response.email_sent 
          ? '✅ Reporte generado y enviado por email'
          : '⚠️ Reporte generado pero no se pudo enviar por email',
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
    <div className="bg-gray-800 dark:bg-gray-700 rounded-lg p-6 mb-6">
      <div className="text-center">
        <h2 className="text-xl font-bold text-white mb-2">Generate Report</h2>
        <p className="text-gray-400 mb-4">Generate AI-powered report and send via email</p>
        <button
          onClick={handleClick}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
        >
          {loading ? 'Generando reporte...' : 'Generate Report & Send Email'}
        </button>
        {result && (
          <p className={`mt-4 text-sm ${result.success ? 'text-green-400' : 'text-red-400'}`}>
            {result.message}
          </p>
        )}
      </div>
    </div>
  );
}

