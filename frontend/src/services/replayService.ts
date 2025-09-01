/**
 * Replay Service
 * Handles communication with the backend replay engine
 */

export interface ReplayState {
  current_index: number;
  total_candles: number;
  current_time: string;
  is_playing: boolean;
  speed: number;
}

export interface ReplayEngineState {
  is_playing: boolean;
  current_index: number;
  speed_multiplier: number;
  auto_trade: boolean;
  risk_management: boolean;
  data_loaded: boolean;
}

export interface ReplayPerformance {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit_loss: number;
  max_drawdown: number;
  sharpe_ratio: number;
  trade_history: any[];
  performance_history: any[];
}

class ReplayService {
  private baseUrl = '/api';

  /**
   * Load data for replay engine
   */
  async loadReplayData(
    instrument: string, 
    startDate: string, 
    endDate: string, 
    timeframe: string = "M15"
  ): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/load-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          instrument,
          start_date: startDate,
          end_date: endDate,
          timeframe
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to load replay data: ${response.statusText}`);
      }

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Error loading replay data:', error);
      return false;
    }
  }

  /**
   * Get current replay state
   */
  async getReplayState(
    symbol: string, 
    timeframe: string, 
    currentIndex: number = 0,
    isPlaying: boolean = false,
    speed: number = 1.0
  ): Promise<ReplayState | null> {
    try {
      const params = new URLSearchParams({
        current_index: currentIndex.toString(),
        is_playing: isPlaying.toString(),
        speed: speed.toString()
      });

      const response = await fetch(`${this.baseUrl}/replay-state/${symbol}/${timeframe}?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get replay state: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting replay state:', error);
      return null;
    }
  }

  /**
   * Get replay engine state
   */
  async getReplayEngineState(): Promise<ReplayEngineState | null> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/state`);
      
      if (!response.ok) {
        throw new Error(`Failed to get replay engine state: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting replay engine state:', error);
      return null;
    }
  }

  /**
   * Start replay
   */
  async playReplay(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/play`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to start replay: ${response.statusText}`);
      }

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Error starting replay:', error);
      return false;
    }
  }

  /**
   * Pause replay
   */
  async pauseReplay(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/pause`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to pause replay: ${response.statusText}`);
      }

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Error pausing replay:', error);
      return false;
    }
  }

  /**
   * Stop replay
   */
  async stopReplay(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/stop`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to stop replay: ${response.statusText}`);
      }

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Error stopping replay:', error);
      return false;
    }
  }

  /**
   * Step forward
   */
  async stepForward(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/step-forward`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to step forward: ${response.statusText}`);
      }

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Error stepping forward:', error);
      return false;
    }
  }

  /**
   * Step backward
   */
  async stepBackward(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/step-backward`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to step backward: ${response.statusText}`);
      }

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Error stepping backward:', error);
      return false;
    }
  }

  /**
   * Set replay speed
   */
  async setSpeed(speed: number): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/set-speed`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ speed })
      });

      if (!response.ok) {
        throw new Error(`Failed to set speed: ${response.statusText}`);
      }

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Error setting speed:', error);
      return false;
    }
  }

  /**
   * Toggle auto trade
   */
  async toggleAutoTrade(): Promise<{ success: boolean; auto_trade: boolean; message: string } | null> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/toggle-auto-trade`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to toggle auto trade: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error toggling auto trade:', error);
      return null;
    }
  }

  /**
   * Toggle risk management
   */
  async toggleRiskManagement(): Promise<{ success: boolean; risk_management: boolean; message: string } | null> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/toggle-risk-management`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to toggle risk management: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error toggling risk management:', error);
      return null;
    }
  }

  /**
   * Get replay performance
   */
  async getPerformance(): Promise<ReplayPerformance | null> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/performance`);
      
      if (!response.ok) {
        throw new Error(`Failed to get performance: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting performance:', error);
      return null;
    }
  }

  /**
   * Simulate strategy
   */
  async simulateStrategy(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/simulate-strategy`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to simulate strategy: ${response.statusText}`);
      }

      const result = await response.json();
      return result.success;
    } catch (error) {
      console.error('Error simulating strategy:', error);
      return false;
    }
  }

  /**
   * Get comprehensive replay status
   */
  async getStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/replay-engine/status`);
      
      if (!response.ok) {
        throw new Error(`Failed to get status: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting status:', error);
      return null;
    }
  }
}

export const replayService = new ReplayService(); 