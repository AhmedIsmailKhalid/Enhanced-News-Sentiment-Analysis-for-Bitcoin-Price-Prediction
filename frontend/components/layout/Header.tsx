'use client';

import { useEffect, useState } from 'react';

export default function Header() {
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isLive, setIsLive] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Set initial time only on client
    setMounted(true);
    setLastUpdated(new Date());

    const interval = setInterval(() => {
      setLastUpdated(new Date());
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  const getRelativeTime = (date: Date) => {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} min ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-gray-900">
              Bitcoin Sentiment MLOps
            </h1>
            {isLive && (
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                LIVE
              </span>
            )}
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              {mounted && lastUpdated ? `Last Updated: ${getRelativeTime(lastUpdated)}` : 'Loading...'}
            </span>
            <div className={`h-2 w-2 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
          </div>
        </div>
      </div>
    </header>
  );
}