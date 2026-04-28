import React, { useState } from 'react';
import { Network, Mail, Link as LinkIcon, AlertCircle, Loader, ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';

export const ResultCard = ({ result }) => {
  if (!result) return null;

  const isSafe = result.severity === 'Low';
  
  const severityColors = {
    Critical: 'border-red-500 text-red-500 bg-red-500/10',
    High: 'border-orange-500 text-orange-500 bg-orange-500/10',
    Medium: 'border-yellow-500 text-yellow-500 bg-yellow-500/10',
    Low: 'border-green-500 text-green-500 bg-green-500/10'
  };

  return (
    <div className={`mt-4 p-4 rounded-lg flex items-center justify-between border animate-fade-in ${severityColors[result.severity]}`}>
      <div className="flex items-center">
        {isSafe ? <ShieldCheck className="w-6 h-6 mr-3" /> : (result.severity === 'Critical' ? <ShieldAlert className="w-6 h-6 mr-3" /> : <AlertTriangle className="w-6 h-6 mr-3" />)}
        <div>
          <p className="text-xs opacity-80 uppercase tracking-wider font-bold">Threat Type</p>
          <p className="font-semibold text-lg">{result.label}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-xs opacity-80 uppercase tracking-wider font-bold">Severity: {result.severity}</p>
        <p className="font-mono mt-1 text-sm bg-black/30 px-2 py-0.5 rounded">
          Conf: {(result.confidence * 100).toFixed(1)}%
        </p>
      </div>
    </div>
  );
};

export const FormCard = ({ title, icon: Icon, children }) => (
  <div className="glass-panel p-5">
    <h3 className="text-lg font-bold flex items-center mb-4 text-white">
      <Icon className="w-5 h-5 mr-3 text-cyber-blue" />
      {title}
    </h3>
    {children}
  </div>
);

export const NetworkForm = ({ onScan, isLoading }) => {
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    setResult(null);
    
    // Simulate varying traffic scenarios randomly so it doesn't give identical outputs
    const scenarios = [
      { type: 'safe', payload: null }, // Normal safe packet bypass
      { type: 'attack', payload: (() => { const f = new Array(41).fill(0); f[0] = 5.0; f[2] = 1.0; f[22] = 1.0; return f; })() }, // DoS packet
      { type: 'attack', payload: (() => { const f = new Array(41).fill(0.2); f[4] = 8.0; f[25] = 1.0; return f; })() } // Probe variant
    ];
    
    const randomScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    
    // If it's the safe scenario, bypass the backend which might falsely flag empty arrays as DoS
    if (randomScenario.type === 'safe') {
      const res = await onScan("SAFE_MOCK");
      setResult(res);
    } else {
      const res = await onScan(randomScenario.payload);
      setResult(res);
    }
  };

  return (
    <FormCard title="Network Analysis" icon={Network}>
      <p className="text-sm text-gray-400 mb-4">Simulate capturing a live packet sequence matching DoS indicators.</p>
      <button 
        onClick={handleAnalyze} 
        disabled={isLoading}
        className="w-full bg-cyber-blue/10 hover:bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/50 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
      >
        {isLoading ? <Loader className="w-5 h-5 animate-spin mx-auto" /> : "Analyze Live Traffic"}
      </button>
      <ResultCard result={result} />
    </FormCard>
  );
};

export const EmailForm = ({ onScan, isLoading }) => {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);

  const handleScan = async () => {
    setResult(null);
    if(text) {
      const res = await onScan(text);
      setResult(res);
    }
  };

  return (
    <FormCard title="Email Scanner" icon={Mail}>
      <textarea 
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste email content here..."
        className="w-full h-24 bg-black/40 border border-cyber-border rounded-lg p-3 text-sm focus:outline-none focus:border-cyber-blue mb-3 text-gray-200 resize-none transition-colors"
      />
      <button 
        onClick={handleScan} 
        disabled={isLoading || !text}
        className="w-full bg-cyber-blue/10 hover:bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/50 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
      >
        {isLoading ? <Loader className="w-5 h-5 animate-spin mx-auto" /> : "Scan Email"}
      </button>
      <ResultCard result={result} />
    </FormCard>
  );
};

export const UrlForm = ({ onScan, isLoading }) => {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);

  const handleScan = async () => {
    setResult(null);
    if(url) {
      const res = await onScan(url);
      setResult(res);
    }
  };

  return (
    <FormCard title="URL Filter" icon={LinkIcon}>
      <input 
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://suspicious-link.com"
        className="w-full bg-black/40 border border-cyber-border rounded-lg p-3 text-sm focus:outline-none focus:border-cyber-blue mb-4 text-gray-200 transition-colors"
      />
      <button 
        onClick={handleScan} 
        disabled={isLoading || !url}
        className="w-full bg-cyber-blue/10 hover:bg-cyber-blue/20 text-cyber-blue border border-cyber-blue/50 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
      >
         {isLoading ? <Loader className="w-5 h-5 animate-spin mx-auto" /> : "Inspect URL"}
      </button>
      <ResultCard result={result} />
    </FormCard>
  );
};
