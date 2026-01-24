'use client';

import { useState, useEffect, useRef } from 'react';
import { scrapeSource, getScrapeProgress, cancelScrape } from '@/lib/api';

interface ScraperButtonProps {
  source: string;
  label: string;
  description?: string;
  onComplete?: () => void;
  compact?: boolean;
}

export default function ScraperButton({ source, label, description, onComplete, compact = false }: ScraperButtonProps) {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<{ percent: number; message: string } | null>(null);
  const [result, setResult] = useState<{ success: boolean; message: string; count?: number; estadoChanges?: number } | null>(null);
  const progressInterval = useRef<NodeJS.Timeout | null>(null);

  // Limpiar intervalo al desmontar
  useEffect(() => {
    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    };
  }, []);

  const startProgressPolling = () => {
    // Polling cada 1 segundo para obtener progreso
    progressInterval.current = setInterval(async () => {
      try {
        const progressData = await getScrapeProgress(source);
        setProgress(progressData);
      } catch (e) {
        // Ignorar errores de polling
      }
    }, 1000);
  };

  const stopProgressPolling = () => {
    if (progressInterval.current) {
      clearInterval(progressInterval.current);
      progressInterval.current = null;
    }
  };

  const handleClick = async () => {
    setLoading(true);
    setResult(null);
    setProgress({ percent: 0, message: 'Iniciando...' });
    
    try {
      // Iniciar el scraper (retorna inmediatamente)
      const startResponse = await scrapeSource(source);
      
      if (startResponse.status === 'already_running') {
        setProgress(startResponse.progress);
      }
      
      // Iniciar polling de progreso
      startProgressPolling();
      
      // Esperar a que termine el scraper
      await new Promise<void>((resolve) => {
        const checkCompletion = setInterval(async () => {
          try {
            const progressData = await getScrapeProgress(source);
            setProgress({ percent: progressData.percent, message: progressData.message });
            
            // Si hay resultado, el scraper terminó
            if (progressData.result) {
              clearInterval(checkCompletion);
              stopProgressPolling();
              
              if (progressData.result.status === 'success') {
                setResult({
                  success: true,
                  message: 'Completed',
                  count: progressData.result.total_leads,
                  estadoChanges: progressData.result.estado_changes || 0,
                });
                onComplete?.();
              } else if (progressData.result.status === 'cancelled') {
                setResult({
                  success: false,
                  message: 'Cancelado',
                });
              } else {
                setResult({
                  success: false,
                  message: progressData.result.error || 'Error',
                });
              }
              setProgress(null);
              setLoading(false);
              resolve();
            }
          } catch (e) {
            // Ignorar errores de polling
          }
        }, 1000);
      });
    } catch (error: any) {
      stopProgressPolling();
      setResult({
        success: false,
        message: error.message || 'Error',
      });
      setProgress(null);
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    try {
      await cancelScrape(source);
      setProgress({ percent: 0, message: 'Cancelando...' });
    } catch (e) {
      // Ignorar errores
    }
  };

  // Versión compacta (tarjeta pequeña)
  if (compact) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 inline-flex items-center gap-3 hover:border-emerald-600/50 transition-all">
        <button
          onClick={handleClick}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
              {label}
            </>
          )}
        </button>
        
        {loading && (
          <button
            onClick={handleCancel}
            className="px-2 py-1.5 rounded text-red-400 text-sm hover:bg-red-500/20 transition-all"
            title="Stop"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
        
        {/* Progress */}
        {loading && progress && (
          <div className="flex items-center gap-2">
            <div className="w-20 bg-zinc-800 rounded-full h-1.5 overflow-hidden">
              <div 
                className="bg-emerald-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${progress.percent}%` }}
              />
            </div>
            <span className="text-xs text-zinc-400">{progress.percent}%</span>
          </div>
        )}
        
        {/* Result */}
        {result && !loading && (
          <span className={`text-xs ${result.success ? 'text-zinc-400' : 'text-red-400'}`}>
            {result.success ? (
              <>
                <span className="text-green-400">{result.count} leads</span>
                {result.estadoChanges !== undefined && result.estadoChanges > 0 && (
                  <span className="text-amber-400 ml-2">{result.estadoChanges} changes</span>
                )}
                {result.estadoChanges === 0 && (
                  <span className="text-zinc-500 ml-2">0 changes</span>
                )}
              </>
            ) : result.message}
          </span>
        )}
      </div>
    );
  }

  // Versión normal (tarjeta completa)
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
          
          {/* Progress indicator */}
          {loading && progress && (
            <div className="mt-3">
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-surface-elevated rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-primary h-full rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress.percent}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-primary min-w-[3rem] text-right">
                  {progress.percent}%
                </span>
              </div>
            </div>
          )}
          
          {/* Result indicator */}
          {result && !loading && (
            <div className={`mt-3 flex items-center gap-2 text-sm ${result.success ? 'text-green-400' : 'text-red-400'}`}>
              {result.success ? (
                <>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                  </svg>
                  <span>{result.count} leads</span>
                  {result.estadoChanges !== undefined && result.estadoChanges > 0 && (
                    <span className="text-amber-400">• {result.estadoChanges} status changes</span>
                  )}
                  {result.estadoChanges === 0 && (
                    <span className="text-zinc-500">• 0 changes</span>
                  )}
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
        
        <div className="flex gap-2 ml-4">
          {loading && (
            <button
              onClick={handleCancel}
              className="px-3 py-2 rounded-lg bg-red-500/20 border border-red-500/30 text-red-400 text-sm font-medium hover:bg-red-500/30 transition-all flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Stop
            </button>
          )}
          <button
            onClick={handleClick}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-surface-elevated border border-border text-dark-text text-sm font-medium hover:bg-border transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
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
    </div>
  );
}
