import React from 'react';
import { 
  TrendingUp, 
  RotateCcw, 
  FlaskConical, 
  Settings,
  ShieldCheck,
  GraduationCap,
  Cpu
} from 'lucide-react';
import { motion } from 'framer-motion';

interface SidebarProps {
  activeView: string;
  setActiveView: (view: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeView, setActiveView }) => {
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
    <div className="w-[var(--sidebar-width)] h-screen glass border-r border-white/5 flex flex-col fixed left-0 top-0 z-50">
      <div className="p-8 flex items-center gap-4">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-[0_0_30px_rgba(37,99,235,0.3)]">
          <Cpu className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-black tracking-tighter text-white">QuantBot<span className="text-blue-500">FX</span></h1>
          <p className="text-[8px] font-bold text-blue-400 uppercase tracking-[0.3em]">Advanced Neural Core</p>
        </div>
      </div>

      <nav className="flex-1 px-6 py-4 space-y-2">
        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20 mb-4 px-2">Core System</div>
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-300 group relative ${
              activeView === item.id 
              ? 'bg-blue-500/10 text-white shadow-[inset_0_0_20px_rgba(59,130,246,0.1)]' 
              : 'text-gray-500 hover:text-white hover:bg-white/[0.03]'
            }`}
          >
            {activeView === item.id && (
              <motion.div 
                layoutId="active-nav"
                className="absolute left-0 w-1 h-8 bg-blue-500 rounded-r-full shadow-[0_0_15px_rgba(59,130,246,0.5)]"
              />
            )}
            <item.icon className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${activeView === item.id ? 'text-blue-400' : ''}`} />
            <span className="font-bold text-sm tracking-tight">{item.name}</span>
          </button>
        ))}

        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20 mt-12 mb-4 px-2">Security</div>
        {secondaryItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-300 group ${
              activeView === item.id 
              ? 'bg-blue-500/10 text-white' 
              : 'text-gray-500 hover:text-white hover:bg-white/[0.02]'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span className="font-bold text-sm tracking-tight">{item.name}</span>
          </button>
        ))}
      </nav>

      <div className="p-6 mt-auto">
        <div className="premium-card p-4 bg-white/[0.02] border border-white/5 rounded-3xl">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
            <span className="text-[10px] uppercase tracking-widest text-gray-500 font-black">Secure Link</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-[10px]">
              <span className="text-gray-500 font-bold uppercase">Node</span>
              <span className="text-white font-mono">NY-04.STABLE</span>
            </div>
            <div className="flex justify-between text-[10px]">
              <span className="text-gray-500 font-bold uppercase">Latency</span>
              <span className="text-green-400 font-mono">1.2ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
