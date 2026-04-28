import React, { useState, useEffect } from 'react';
import { Shield, Activity, XOctagon } from 'lucide-react';
import { checkHealth } from '../services/api';

export default function Navbar() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const poll = async () => {
      try {
        await checkHealth();
        setIsOnline(true);
      } catch (err) {
        setIsOnline(false);
      }
    };
    poll(); // initial
    const interval = setInterval(poll, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="w-full h-16 border-b border-cyber-border bg-cyber-panel/90 text-white flex items-center justify-between px-6 backdrop-blur-md sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <Shield className="w-8 h-8 text-cyber-blue shadow-cyber-blue drop-shadow-md" />
        <h1 className="text-xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyber-blue">
          CYBERSHIELD SOC
        </h1>
      </div>
      
      <div className="flex items-center space-x-4">
        {isOnline ? (
          <div className="flex items-center px-4 py-1.5 rounded-full bg-green-500/10 border border-green-500/30 text-green-500 text-sm font-medium transition-all">
            <Activity className="w-4 h-4 mr-2 animate-pulse" />
            🟢 SYSTEM ACTIVE
          </div>
        ) : (
          <div className="flex items-center px-4 py-1.5 rounded-full bg-red-500/10 border border-red-500/30 text-red-500 text-sm font-medium transition-all">
            <XOctagon className="w-4 h-4 mr-2" />
            🔴 OFFLINE
          </div>
        )}
      </div>
    </nav>
  );
}
