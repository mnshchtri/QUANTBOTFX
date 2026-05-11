import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, Mail, User as UserIcon, ArrowRight, Eye, EyeOff } from 'lucide-react';
import { login, signup, type User, type AuthResponse } from '../../services/api';

interface AuthPageProps {
  onAuthSuccess: (user: User) => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess }) => {
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let res: AuthResponse;
      if (mode === 'login') {
        res = await login(formData.username, formData.password);
      } else {
        res = await signup(formData.username, formData.email, formData.password);
      }

      if (res.success && res.user) {
        onAuthSuccess(res.user);
      } else {
        setError(res.error || 'Authentication failed');
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col lg:flex-row-reverse relative overflow-hidden font-inter">
      {/* Right Panel: Narrow Auth Workspace */}
      <div className="w-full lg:w-[420px] xl:w-[460px] h-screen z-10 bg-white flex flex-col items-center justify-center p-8 lg:p-12 relative border-l border-slate-100 shadow-[-20px_0_100px_rgba(0,0,0,0.02)]">
        <motion.div 
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="w-full max-w-[320px] relative z-10"
        >
          <div className="text-center mb-10 flex flex-col items-center">
            <div className="relative mb-2">
              <img 
                src="/quantbot-logo.png" 
                alt="QuantBotFX Logo" 
                className="h-12 w-auto select-none pointer-events-none drop-shadow-sm"
              />
            </div>
            <h2 className="text-[12px] font-black text-slate-900 uppercase tracking-[0.4em] ml-[0.4em]">
              QuantBotFX
            </h2>
          </div>

          <div className="relative">
            {/* Tab Selector */}
            <div className="flex bg-slate-50 p-1 rounded-xl mb-8 border border-slate-100">
              <button 
                onClick={() => setMode('login')}
                className={`flex-1 py-2 text-[10px] font-bold uppercase tracking-[0.2em] rounded-lg transition-all ${mode === 'login' ? 'bg-white text-blue-600 shadow-sm border border-slate-100' : 'text-slate-400 hover:text-slate-600'}`}
              >
                Authenticate
              </button>
              <button 
                onClick={() => setMode('signup')}
                className={`flex-1 py-2 text-[10px] font-bold uppercase tracking-[0.2em] rounded-lg transition-all ${mode === 'signup' ? 'bg-white text-blue-600 shadow-sm border border-slate-100' : 'text-slate-400 hover:text-slate-600'}`}
              >
                Establish
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.3em] ml-1">Terminal ID</label>
                <div className="relative group">
                  <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300 group-focus-within:text-blue-600 transition-colors" />
                  <input 
                    type="text"
                    required
                    placeholder="Username"
                    className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3.5 pl-12 pr-4 text-[13px] text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600/40 focus:bg-white transition-all shadow-sm"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                  />
                </div>
              </div>

              <AnimatePresence mode="wait">
                {mode === 'signup' && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-2 overflow-hidden"
                  >
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.3em] ml-1">Network Hub</label>
                    <div className="relative group">
                      <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300 group-focus-within:text-blue-600 transition-colors" />
                      <input 
                        type="email"
                        required
                        placeholder="Email Address"
                        className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3.5 pl-12 pr-4 text-[13px] text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600/40 focus:bg-white transition-all shadow-sm"
                        value={formData.email}
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="space-y-2">
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.3em] ml-1">Access Key</label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300 group-focus-within:text-blue-600 transition-colors" />
                  <input 
                    type={showPassword ? "text" : "password"}
                    required
                    placeholder="Password"
                    className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3.5 pl-12 pr-12 text-[13px] text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600/40 focus:bg-white transition-all shadow-sm"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-300 hover:text-blue-600 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {error && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-red-50 border border-red-100 text-red-500 text-[10px] font-bold p-3 rounded-xl text-center uppercase tracking-wider"
                >
                  {error}
                </motion.div>
              )}

              <button 
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-600/20 transition-all flex items-center justify-center gap-3 group mt-2"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span className="uppercase tracking-[0.2em] text-[11px]">
                      {mode === 'login' ? 'Initialize Session' : 'Create Node'}
                    </span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>
          </div>
        </motion.div>
      </div>

      {/* Left Panel: Large Vision Workspace */}
      <div className="flex-1 relative bg-slate-50 overflow-hidden hidden lg:flex items-center justify-center">
        <div className="relative z-10 w-full max-w-[900px] flex flex-col lg:flex-row items-center gap-16 p-16">
          <motion.div
            key={mode}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="flex-1"
          >
            <div className="space-y-8 max-w-[550px]">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-600 rounded-full">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-pulse" />
                <span className="text-[10px] font-bold uppercase tracking-widest">Neural Intelligence Active</span>
              </div>
              <h1 className="text-5xl xl:text-6xl font-extrabold text-slate-900 leading-[1.15] tracking-tight">
                {mode === 'login' ? (
                  <>Precision Trading, <br/><span className="text-blue-600">Reimagined.</span></>
                ) : (
                  <>Join the Future of <br/><span className="text-blue-600">Quant Finance.</span></>
                )}
              </h1>
              <p className="text-slate-500 text-xl leading-relaxed">
                Experience the power of neural-driven market analysis. QuantBotFX delivers institutional-grade precision directly to your terminal.
              </p>
              
              <div className="grid grid-cols-2 gap-6 pt-6">
                <div className="space-y-2">
                  <div className="text-blue-600 font-bold text-xl">0.1ms</div>
                  <div className="text-slate-400 text-[10px] uppercase font-bold tracking-widest">Latency</div>
                </div>
                <div className="space-y-2">
                  <div className="text-blue-600 font-bold text-xl">99.9%</div>
                  <div className="text-slate-400 text-[10px] uppercase font-bold tracking-widest">Accuracy</div>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            key={`${mode}-visual`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            className="flex-1 flex justify-start pl-12"
          >
            {mode === 'login' ? (
              <img 
                src="/man.svg" 
                alt="QuantBot Insight" 
                className="w-full max-w-[400px] h-auto drop-shadow-[0_20px_50px_rgba(0,0,0,0.05)] scale-x-[-1]"
              />
            ) : (
              <div className="flex items-center -space-x-48">
                <img 
                  src="/man2.png" 
                  alt="QuantBot Advisor" 
                  className="max-w-[300px] h-auto drop-shadow-[0_20px_50px_rgba(0,0,0,0.05)] relative z-10"
                />
                <img 
                  src="/10865297.png" 
                  alt="QuantBot Member" 
                  className="max-w-[300px] h-auto drop-shadow-[0_20px_50px_rgba(0,0,0,0.05)]"
                />
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
