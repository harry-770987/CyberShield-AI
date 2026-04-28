import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';

const SeverityBadge = ({ severity }) => {
  const styles = {
    Critical: 'bg-red-500/10 text-red-500 border-red-500/20',
    High: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
    Medium: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    Low: 'bg-green-500/10 text-green-500 border-green-500/20'
  };

  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded border ${styles[severity] || styles.Low}`}>
      {severity}
    </span>
  );
};

export default function LogsTable({ logs }) {
  return (
    <div className="glass-panel overflow-hidden h-full flex flex-col">
      <div className="p-4 border-b border-cyber-border bg-black/20">
        <h3 className="font-bold text-white tracking-wide">Threat Log Feed</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-[#111118] text-gray-400 sticky top-0 z-10">
            <tr>
              <th className="py-3 px-4 font-medium">Time</th>
              <th className="py-3 px-4 font-medium">Module</th>
              <th className="py-3 px-4 font-medium">Classification</th>
              <th className="py-3 px-4 font-medium">Severity</th>
              <th className="py-3 px-4 font-medium">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cyber-border">
            {logs.length === 0 ? (
              <tr>
                <td colSpan="5" className="text-center py-8 text-gray-500">
                  No scan logs available.
                </td>
              </tr>
            ) : (
              logs.map((log, idx) => {
                const isThreat = !log.label.includes('Safe');
                return (
                <tr key={idx} className={`hover:bg-cyber-blue/5 transition-colors animate-slide-down ${isThreat ? 'bg-red-500/5' : ''}`}>
                  <td className="py-3 px-4 text-gray-400 font-mono text-xs">{log.time}</td>
                  <td className="py-3 px-4 text-gray-200 font-medium">{log.module}</td>
                  <td className="py-3 px-4">
                    <span className={`flex items-center font-bold ${isThreat ? (log.severity === 'Critical' ? 'text-red-400' : 'text-orange-400') : 'text-green-500'}`}>
                      {!isThreat ? (
                        <ShieldCheck className="w-4 h-4 mr-2" />
                      ) : (
                        log.severity === 'Critical' ? <ShieldAlert className="w-4 h-4 mr-2" /> : <AlertTriangle className="w-4 h-4 mr-2" />
                      )}
                      {log.label}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <SeverityBadge severity={log.severity} />
                  </td>
                  <td className="py-3 px-4 text-gray-400 font-mono">
                    <div className="flex items-center">
                      <div className="w-16 h-1.5 bg-black rounded-full mr-2 overflow-hidden">
                         <div className={`h-full ${isThreat ? 'bg-red-500' : 'bg-cyber-blue'}`} style={{ width: `${log.confidence * 100}%` }}></div>
                      </div>
                      {(log.confidence * 100).toFixed(0)}%
                    </div>
                  </td>
                </tr>
              )})
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
