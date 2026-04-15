import React from 'react';
import { 
  ChartBarIcon, 
  BeakerIcon, 
  ArrowPathIcon, 
  Cog6ToothIcon,
  ShieldCheckIcon,
  AcademicCapIcon,
  CursorArrowRaysIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  activeView: string;
  setActiveView: (view: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeView, setActiveView }) => {
  const menuItems = [
    { id: 'trading', name: 'Trading', icon: ChartBarIcon },
    { id: 'replay', name: 'Replay Mode', icon: ArrowPathIcon },
    { id: 'strategy', name: 'Quant Lab', icon: BeakerIcon },
    { id: 'education', name: 'Academy', icon: AcademicCapIcon },
  ];

  const secondaryItems = [
    { id: 'risk', name: 'Risk Engine', icon: ShieldCheckIcon },
    { id: 'settings', name: 'Settings', icon: Cog6ToothIcon },
  ];

  return (
    <div className="w-[var(--sidebar-width)] h-screen glass border-r border-[var(--border-subtle)] flex flex-col fixed left-0 top-0 z-50">
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-[0_0_20px_rgba(37,99,235,0.4)]">
          <CursorArrowRaysIcon className="w-5 h-5 text-white" />
        </div>
        <span className="text-xl font-black tracking-tighter text-[var(--text-main)]">QuantBot<span className="text-blue-500">FX</span></span>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-1">
        <div className="panel-header px-2">Core terminal</div>
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
              activeView === item.id 
              ? 'bg-blue-500/10 text-[var(--accent-primary)] border border-blue-500/20' 
              : 'text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[#ffffff05]'
            }`}
          >
            <item.icon className={`w-5 h-5 transition-colors ${activeView === item.id ? 'text-[var(--accent-primary)]' : 'text-[var(--text-muted)] group-hover:text-[var(--text-main)]'}`} />
            <span className="font-medium">{item.name}</span>
            {activeView === item.id && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)] glow-blue" />}
          </button>
        ))}

        <div className="panel-header px-2 pt-8">Security & Tools</div>
        {secondaryItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
              activeView === item.id 
              ? 'bg-blue-500/10 text-[var(--accent-primary)] border border-blue-500/20' 
              : 'text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[#ffffff05]'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium text-sm">{item.name}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 mt-auto border-t border-[var(--border-subtle)]">
        <div className="bg-[#ffffff05] rounded-xl p-3 border border-[var(--border-subtle)]">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] font-bold">Terminal Status</span>
          </div>
          <div className="text-xs text-[var(--text-main)] flex justify-between font-medium">
            <span>Latency</span>
            <span className="data-value text-green-400">12ms</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
