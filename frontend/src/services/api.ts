// Central API client – all calls go through here.
// Base URL resolves from env var injected at build time, or falls back to localhost.

const BASE = process.env.REACT_APP_API_URL ?? 'http://localhost:8000';

async function api<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

// ── Market Data ───────────────────────────────────────────────────────────────
export interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export async function fetchCandles(
  symbol: string,
  timeframe: string
): Promise<Candle[]> {
  const res = await api<{ data: Candle[] }>(`/api/candles/${symbol}/${timeframe}`);
  return res.data;
}

// ── Indicators ────────────────────────────────────────────────────────────────
export interface Indicators {
  sma_20: (number | null)[];
  ema_50: (number | null)[];
  rsi_14: (number | null)[];
  macd:   (number | null)[];
}

export async function fetchIndicators(
  symbol: string,
  timeframe: string
): Promise<Indicators> {
  return api<Indicators>(`/api/indicators/${symbol}/${timeframe}`);
}

// ── Account ───────────────────────────────────────────────────────────────────
export interface AccountSummary {
  balance:     number;
  equity:      number;
  pnl_today:   number;
  pnl_percent: number;
  open_trades: number;
}

export async function fetchAccount(): Promise<AccountSummary> {
  const res = await api<{ data: AccountSummary }>('/api/trading/summary');
  return res.data;
}

// ── Trading ───────────────────────────────────────────────────────────────────
export interface TradeResult {
  success:     boolean;
  message:     string;
  position_id: string;
}

export async function executeTrade(
  symbol: string,
  type: 'buy' | 'sell',
  volume: number,
  price: number
): Promise<TradeResult> {
  return api<TradeResult>('/api/trading/execute', {
    method: 'POST',
    body: JSON.stringify({ symbol, type, volume, price }),
  });
}

export async function closePosition(id: string): Promise<{ success: boolean }> {
  return api<{ success: boolean }>(`/api/trading/close/${id}`, {
    method: 'POST',
  });
}

export interface Position {
  id:            string;
  symbol:        string;
  side:          string;
  volume:        number;
  entry_price:   number;
  current_price: number;
  pnl:           number;
  status:        string;
}

export async function fetchPositions(): Promise<Position[]> {
  const res = await api<{ data: Position[] }>('/api/trading/positions');
  return res.data;
}

// ── Replay ────────────────────────────────────────────────────────────────────
export interface ReplayStatus {
  state:         string;
  current_index: number;
  total_candles: number;
  progress_pct:  number;
  speed:         number;
  balance:       number;
  open_trades:   number;
}

export async function initReplay(
  symbol: string,
  timeframe: string
): Promise<{ success: boolean; total_candles: number }> {
  return api(`/api/replay/initialize/${symbol}/${timeframe}`);
}

export async function replayStatus(): Promise<ReplayStatus> {
  return api<ReplayStatus>('/api/replay/status');
}

export type ReplayAction = 'play' | 'pause' | 'reset' | 'step' | 'step_back' | 'seek' | 'speed';

export async function replayControl(
  action: ReplayAction,
  value?: number
): Promise<{ success: boolean; state: string; index: number }> {
  return api('/api/replay/control', {
    method: 'POST',
    body: JSON.stringify({ action, value }),
  });
}

export async function fetchReplayData(): Promise<{
  candles:  Candle[];
  state:    string;
  index:    number;
  progress: number;
}> {
  return api('/api/replay/data');
}

// ─────────────────────────────────────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  token?: string;
  error?: string;
}

export async function signup(username: string, email: string, password: string): Promise<AuthResponse> {
  return api<AuthResponse>('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  return api<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}
