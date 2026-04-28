import React from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck, Shield } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export default function SummaryPanel({ counts }) {
  const data = [
    { name: 'Critical', value: counts.Critical || 0, color: '#ef4444' },
    { name: 'High', value: counts.High || 0, color: '#f97316' },
    { name: 'Medium', value: counts.Medium || 0, color: '#eab308' },
    { name: 'Low', value: counts.Low || 0, color: '#22c55e' }
  ];

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="glass-panel p-6 flex flex-col h-full">
      <h2 className="text-xl font-bold flex items-center mb-6 text-white border-b border-cyber-border pb-3">
        <Shield className="w-5 h-5 mr-3 text-cyber-blue" />
        Threat Summary
      </h2>
      
      <div className="flex-grow flex items-center justify-between">
        {/* Left Side: Counts */}
        <div className="grid grid-cols-2 gap-4 w-1/2">
          <div className="bg-black/30 p-4 rounded-lg border border-red-500/20">
            <div className="flex items-center text-red-500 mb-1">
              <ShieldAlert className="w-4 h-4 mr-2" />
              <span className="text-sm font-semibold">Critical</span>
            </div>
            <div className="text-2xl font-bold text-white">{counts.Critical}</div>
          </div>
          
          <div className="bg-black/30 p-4 rounded-lg border border-orange-500/20">
            <div className="flex items-center text-orange-500 mb-1">
              <AlertTriangle className="w-4 h-4 mr-2" />
              <span className="text-sm font-semibold">High</span>
            </div>
            <div className="text-2xl font-bold text-white">{counts.High}</div>
          </div>
          
          <div className="bg-black/30 p-4 rounded-lg border border-yellow-500/20">
            <div className="flex items-center text-yellow-500 mb-1">
              <AlertTriangle className="w-4 h-4 mr-2" />
              <span className="text-sm font-semibold">Medium</span>
            </div>
            <div className="text-2xl font-bold text-white">{counts.Medium}</div>
          </div>
          
          <div className="bg-black/30 p-4 rounded-lg border border-green-500/20">
            <div className="flex items-center text-green-500 mb-1">
              <ShieldCheck className="w-4 h-4 mr-2" />
              <span className="text-sm font-semibold">Low</span>
            </div>
            <div className="text-2xl font-bold text-white">{counts.Low}</div>
          </div>
        </div>

        {/* Right Side: Chart */}
        <div className="w-1/2 h-40 flex flex-col items-center justify-center">
          {total > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={30}
                  outerRadius={50}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#13131a', borderColor: '#1e1e2d', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-500 flex flex-col items-center">
              <Shield className="w-8 h-8 mb-2 opacity-50" />
              <span className="text-sm">No active threats</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
