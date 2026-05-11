import React from 'react';
import { 
  TrendingUp, 
  RotateCcw, 
  FlaskConical, 
  Settings,
  ShieldCheck,
  GraduationCap,
  Cpu,
  Layout
} from 'lucide-react';
import { motion } from 'framer-motion';
import { ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';

interface SidebarProps {
  activeView: string;
  setActiveView: (view: string) => void;
  onLogout: () => void;
  leftPanelOpen: boolean;
  setLeftPanelOpen: (open: boolean) => void;
  rightPanelOpen: boolean;
  setRightPanelOpen: (open: boolean) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  activeView, 
  setActiveView, 
  onLogout,
  leftPanelOpen,
  setLeftPanelOpen,
  rightPanelOpen,
  setRightPanelOpen
}) => {
  const menuItems = [
    { id: 'trading', name: 'Live Terminal', icon: TrendingUp },
    { id: 'replay', name: 'Deep Replay', icon: RotateCcw },
    { id: 'strategy', name: 'Quant Lab', icon: FlaskConical },
    { id: 'education', name: 'Academy', icon: GraduationCap },
  ];

  const secondaryItems = [
    { id: 'risk', name: 'Risk Engine', icon: ShieldCheck },
    { id: 'settings', name: 'Preferences', icon: Settings },
  ];

  return (
    <div className="w-[var(--sidebar-width)] h-screen bg-white border-r border-slate-100 flex flex-col shrink-0">
      <div className="p-8 flex items-center gap-4">
        <div className="w-12 h-12 flex items-center justify-center overflow-hidden">
          <img src="/quantbot-logo.png" alt="QuantBot Logo" className="w-full h-full object-contain" />
        </div>
        <div>
          <h1 className="text-xl font-black tracking-tighter text-slate-900">QuantBot<span className="text-blue-600">FX</span></h1>
          <p className="text-[8px] font-bold text-blue-600 uppercase tracking-[0.3em]">Advanced Neural Core</p>
        </div>
      </div>

      <nav className="flex-1 px-6 py-4 space-y-2">
        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-300 mb-4 px-2">Core System</div>
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-300 group relative ${
              activeView === item.id 
              ? 'bg-blue-50 text-blue-600' 
              : 'text-slate-400 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            {activeView === item.id && (
              <motion.div 
                layoutId="active-nav"
                className="absolute left-0 w-1 h-8 bg-blue-600 rounded-r-full"
              />
            )}
            <item.icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${activeView === item.id ? 'text-blue-600' : ''}`} />
            <span className="font-bold text-sm tracking-tight">{item.name}</span>
          </button>
        ))}

        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-300 mt-12 mb-4 px-2">Security</div>
        {secondaryItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-300 group ${
              activeView === item.id 
              ? 'bg-blue-50 text-blue-600' 
              : 'text-slate-400 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-bold text-sm tracking-tight">{item.name}</span>
          </button>
        ))}
      </nav>

      <div className="p-6 mt-auto">
        <div className="p-5 bg-slate-50 rounded-3xl border border-slate-100 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]" />
              <span className="text-[10px] uppercase tracking-[0.2em] text-slate-400 font-black">Secure Link</span>
            </div>
            <button 
              onClick={onLogout}
              className="p-1.5 text-slate-400 hover:text-rose-500 transition-all bg-white rounded-lg border border-slate-200 shadow-sm"
              title="Secure Logout"
            >
              <ArrowRightOnRectangleIcon className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <button 
              onClick={() => setLeftPanelOpen(!leftPanelOpen)}
              className={`flex items-center justify-center gap-2 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all border ${
                leftPanelOpen ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'bg-white border-slate-200 text-slate-400 hover:text-slate-900'
              }`}
            >
              <Layout className="w-3 h-3" />
              Left
            </button>
            <button 
              onClick={() => setRightPanelOpen(!rightPanelOpen)}
              className={`flex items-center justify-center gap-2 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all border ${
                rightPanelOpen ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' : 'bg-white border-slate-200 text-slate-400 hover:text-slate-900'
              }`}
            >
              <Layout className="w-3 h-3" />
              Right
            </button>
          </div>

          <div className="space-y-3 pt-2 border-t border-slate-100">
            <div className="flex justify-between text-[10px] items-center">
              <span className="text-slate-400 font-bold uppercase tracking-widest">Node</span>
              <span className="text-slate-900 font-mono font-bold px-2 py-0.5 bg-white border border-slate-200 rounded-md">NY-04.STABLE</span>
            </div>
            <div className="flex justify-between text-[10px] items-center">
              <span className="text-slate-400 font-bold uppercase tracking-widest">Latency</span>
              <span className="text-emerald-600 font-mono font-bold">1.2ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
