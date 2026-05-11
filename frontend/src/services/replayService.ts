import {
  initReplay,
  replayControl,
  replayStatus,
  fetchReplayData,
  type ReplayStatus,
  type Candle,
} from './api';

export type { ReplayStatus, Candle };

export interface ReplayState {
  symbol: string;
  timeframe: string;
  currentIndex: number;
  isPlaying: boolean;
  speed: number;
}

export interface ReplayEngineState {
  state: string;
  auto_trade: boolean;
  risk_management: boolean;
}

export interface ReplayPerformance {
  total_trades: number;
  win_rate: number;
  total_profit_loss: number;
  max_drawdown: number;
}

class ReplayService {
  public async getReplayState(symbol: string, timeframe: string, currentIndex: number, isPlaying: boolean, speed: number): Promise<ReplayState> {
    return { symbol, timeframe, currentIndex, isPlaying, speed };
  }

  public async getReplayEngineState(): Promise<ReplayEngineState> {
    const status = await replayStatus();
    return {
      state: status.state,
      auto_trade: false,
      risk_management: true
    };
  }

  public async getPerformance(): Promise<ReplayPerformance> {
    return {
      total_trades: 0,
      win_rate: 0,
      total_profit_loss: 0,
      max_drawdown: 0
    };
  }

  public async playReplay() {
    return replayControl('play');
  }

  public async pauseReplay() {
    return replayControl('pause');
  }

  public async stepForward() {
    return replayControl('step');
  }

  public async stepBackward() {
    return replayControl('step_back');
  }

  public async setSpeed(speed: number) {
    return replayControl('speed', speed);
  }

  public async toggleAutoTrade() {
    return { auto_trade: false };
  }

  public async toggleRiskManagement() {
    return { risk_management: true };
  }

  public async simulateStrategy() {
    return { success: true };
  }
}

const replayService = new ReplayService();
export { replayService };
export default replayService;