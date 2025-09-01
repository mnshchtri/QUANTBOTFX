export interface ReplayLevel {
  id: string;
  price: number;
  type: 'support' | 'resistance' | 'trendline';
  timeframe: string;
  symbol: string;
  color: string;
  style: 'solid' | 'dashed' | 'dotted';
  width: number;
  label?: string;
  createdAt: number;
  createdBy: string;
}

class ReplayLevelsService {
  private levels: Map<string, ReplayLevel> = new Map();
  private listeners: Set<(levels: ReplayLevel[]) => void> = new Set();

  // Add a new replay level
  addLevel(level: Omit<ReplayLevel, 'id' | 'createdAt'>): ReplayLevel {
    const id = `replay_level_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newLevel: ReplayLevel = {
      ...level,
      id,
      createdAt: Date.now()
    };
    
    this.levels.set(id, newLevel);
    this.notifyListeners();
    return newLevel;
  }

  // Remove a replay level
  removeLevel(levelId: string): boolean {
    const removed = this.levels.delete(levelId);
    if (removed) {
      this.notifyListeners();
    }
    return removed;
  }

  // Get levels for a specific symbol and timeframe
  getLevels(symbol: string, timeframe?: string): ReplayLevel[] {
    let filteredLevels = Array.from(this.levels.values())
      .filter(level => level.symbol === symbol);
    
    if (timeframe) {
      filteredLevels = filteredLevels.filter(level => level.timeframe === timeframe);
    }
    
    return filteredLevels.sort((a, b) => a.createdAt - b.createdAt);
  }

  // Get all levels for a symbol across all timeframes
  getMultiTimeframeLevels(symbol: string): ReplayLevel[] {
    return Array.from(this.levels.values())
      .filter(level => level.symbol === symbol)
      .sort((a, b) => a.createdAt - b.createdAt);
  }

  // Update a level
  updateLevel(levelId: string, updates: Partial<ReplayLevel>): ReplayLevel | null {
    const level = this.levels.get(levelId);
    if (!level) return null;
    
    const updatedLevel = { ...level, ...updates };
    this.levels.set(levelId, updatedLevel);
    this.notifyListeners();
    return updatedLevel;
  }

  // Subscribe to level changes
  subscribe(callback: (levels: ReplayLevel[]) => void): () => void {
    this.listeners.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  // Notify all listeners
  private notifyListeners(): void {
    const allLevels = Array.from(this.levels.values());
    this.listeners.forEach(callback => callback(allLevels));
  }

  // Clear all replay levels
  clearLevels(): void {
    this.levels.clear();
    this.notifyListeners();
  }

  // Get level statistics
  getLevelStats(symbol: string): {
    total: number;
    byType: Record<string, number>;
    byTimeframe: Record<string, number>;
  } {
    const symbolLevels = this.getLevels(symbol);
    
    const byType: Record<string, number> = {};
    const byTimeframe: Record<string, number> = {};
    
    symbolLevels.forEach(level => {
      byType[level.type] = (byType[level.type] || 0) + 1;
      byTimeframe[level.timeframe] = (byTimeframe[level.timeframe] || 0) + 1;
    });
    
    return {
      total: symbolLevels.length,
      byType,
      byTimeframe
    };
  }
}

// Create singleton instance
const replayLevelsService = new ReplayLevelsService();

export default replayLevelsService;
