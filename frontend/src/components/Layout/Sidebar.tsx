import React, { useState } from 'react';
import { 
  TrendingUp, 
  RotateCcw, 
  FlaskConical, 
  Settings,
  ShieldCheck,
  GraduationCap,
  Layout,
  PanelLeftClose,
  PanelLeftOpen
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
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
  const [isCollapsed, setIsCollapsed] = useState(false);

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
    <div 
      className={`h-screen bg-white border-r border-slate-100 flex flex-col shrink-0 transition-all duration-300 ease-in-out relative ${
        isCollapsed ? 'w-[88px]' : 'w-[280px]'
      }`}
    >
      <div className={`p-8 flex items-center gap-4 ${isCollapsed ? 'justify-center px-4' : ''}`}>
        <div className="w-12 h-12 flex items-center justify-center overflow-hidden shrink-0">
          <img src="/quantbot-logo.png" alt="QuantBot Logo" className="w-full h-full object-contain" />
        </div>
        {!isCollapsed && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="whitespace-nowrap">
            <h1 className="text-xl font-black tracking-tighter text-slate-900">QuantBot<span className="text-blue-600">FX</span></h1>
            <p className="text-[8px] font-bold text-blue-600 uppercase tracking-[0.3em]">Advanced Neural Core</p>
          </motion.div>
        )}
      </div>

      <button 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3.5 top-10 bg-white border border-slate-200 rounded-full p-1.5 text-slate-400 hover:text-blue-600 hover:border-blue-200 hover:shadow-md transition-all z-50"
      >
        {isCollapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
      </button>

      <nav className={`flex-1 py-4 space-y-2 ${isCollapsed ? 'px-4' : 'px-6'}`}>
        {!isCollapsed && <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-300 mb-4 px-2">Core System</div>}
        {isCollapsed && <div className="h-4" />}
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-4 py-3 rounded-2xl transition-all duration-300 group relative ${
              isCollapsed ? 'justify-center px-0' : 'px-4'
            } ${
              activeView === item.id 
              ? 'bg-blue-50 text-blue-600' 
              : 'text-slate-400 hover:text-slate-900 hover:bg-slate-50'
            }`}
            title={isCollapsed ? item.name : undefined}
          >
            {activeView === item.id && (
              <motion.div 
                layoutId="active-nav"
                className="absolute left-0 w-1 h-8 bg-blue-600 rounded-r-full"
              />
            )}
            <item.icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 shrink-0 ${activeView === item.id ? 'text-blue-600' : ''}`} />
            {!isCollapsed && <span className="font-bold text-sm tracking-tight whitespace-nowrap">{item.name}</span>}
          </button>
        ))}

        {!isCollapsed && <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-300 mt-12 mb-4 px-2">Security</div>}
        {isCollapsed && <div className="h-8" />}
        {secondaryItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-4 py-3 rounded-2xl transition-all duration-300 group ${
              isCollapsed ? 'justify-center px-0' : 'px-4'
            } ${
              activeView === item.id 
              ? 'bg-blue-50 text-blue-600' 
              : 'text-slate-400 hover:text-slate-900 hover:bg-slate-50'
            }`}
            title={isCollapsed ? item.name : undefined}
          >
            <item.icon className="w-5 h-5 shrink-0" />
            {!isCollapsed && <span className="font-bold text-sm tracking-tight whitespace-nowrap">{item.name}</span>}
          </button>
        ))}
      </nav>

      <div className={`mt-auto ${isCollapsed ? 'p-4' : 'p-6'}`}>
        {isCollapsed ? (
          <div className="flex flex-col items-center gap-4 bg-slate-50 py-4 rounded-2xl border border-slate-200">
             <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" title="Node: NY-04.STABLE | 1.2ms" />
             <button onClick={onLogout} className="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-all" title="Secure Logout">
               <ArrowRightOnRectangleIcon className="w-5 h-5" />
             </button>
          </div>
        ) : (
          <div className="p-5 bg-slate-50 rounded-3xl border border-slate-200 space-y-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
                <span className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-black">Secure Link</span>
              </div>
              <button 
                onClick={onLogout}
                className="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 transition-all bg-white rounded-lg border border-slate-200 shadow-sm"
                title="Secure Logout"
              >
                <ArrowRightOnRectangleIcon className="w-4 h-4" />
              </button>
            </div>

            <div className="flex bg-white border border-slate-200 p-1 rounded-xl shadow-sm">
              <button 
                onClick={() => setLeftPanelOpen(!leftPanelOpen)}
                className={`flex-1 flex items-center justify-center gap-2 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${
                  leftPanelOpen ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Layout className="w-3 h-3" />
                Left
              </button>
              <button 
                onClick={() => setRightPanelOpen(!rightPanelOpen)}
                className={`flex-1 flex items-center justify-center gap-2 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${
                  rightPanelOpen ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Layout className="w-3 h-3" />
                Right
              </button>
            </div>

            <div className="space-y-2 pt-4 border-t border-slate-200">
              <div className="flex justify-between items-center">
                <span className="text-[9px] text-slate-400 font-black uppercase tracking-widest">Node</span>
                <span className="text-[10px] text-slate-800 font-mono font-bold px-2 py-0.5 bg-white border border-slate-200 rounded-md shadow-sm">NY-04.STABLE</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[9px] text-slate-400 font-black uppercase tracking-widest">Latency</span>
                <span className="text-[11px] text-emerald-600 font-mono font-bold">1.2ms</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
