import { fetchIndicators } from './api';

export interface ReplayLevel {
  id: string;
  price: number;
  type: 'support' | 'resistance' | 'trendline';
  timeframe: string;
  strength: number;
  label?: string;
  color?: string;
  style?: 'solid' | 'dashed' | 'dotted';
  width?: number;
}

class ReplayLevelsService {
  private subscribers: ((levels: ReplayLevel[]) => void)[] = [];
  private levels: ReplayLevel[] = [];

  public async getReplayLevels(symbol: string, timeframe: string): Promise<ReplayLevel[]> {
    return this.levels;
  }

  public getMultiTimeframeLevels(symbol: string): ReplayLevel[] {
    return this.levels;
  }

  public addLevel(level: Omit<ReplayLevel, 'id' | 'strength'> & { symbol: string }): ReplayLevel {
    const newLevel: ReplayLevel = {
      ...level,
      id: Math.random().toString(36).substr(2, 9),
      strength: 1.0
    };
    this.levels.push(newLevel);
    this.notifySubscribers();
    return newLevel;
  }

  public removeLevel(levelId: string): void {
    this.levels = this.levels.filter(l => l.id !== levelId);
    this.notifySubscribers();
  }

  public subscribe(callback: (levels: ReplayLevel[]) => void): () => void {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter(s => s !== callback);
    };
  }

  private notifySubscribers(): void {
    this.subscribers.forEach(callback => callback(this.levels));
  }
}

const replayLevelsService = new ReplayLevelsService();
export default replayLevelsService;
