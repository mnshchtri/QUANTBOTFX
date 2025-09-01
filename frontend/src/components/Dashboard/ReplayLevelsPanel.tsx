import React, { useState, useEffect } from 'react';
import replayLevelsService, { ReplayLevel } from '../../services/replayLevelsService';

interface ReplayLevelsPanelProps {
  symbol: string;
  timeframe: string;
  onLevelAdd?: (level: ReplayLevel) => void;
  onLevelRemove?: (levelId: string) => void;
}

const ReplayLevelsPanel: React.FC<ReplayLevelsPanelProps> = ({
  symbol,
  timeframe,
  onLevelAdd,
  onLevelRemove
}) => {
  const [levels, setLevels] = useState<ReplayLevel[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newLevel, setNewLevel] = useState({
    price: 0,
    type: 'support' as const,
    color: '#3b82f6',
    style: 'solid' as const,
    width: 2,
    label: '',
    createdBy: 'replay_user'
  });

  const levelTypes = [
    { value: 'support', label: 'Support', color: '#10b981' },
    { value: 'resistance', label: 'Resistance', color: '#ef4444' },
    { value: 'trendline', label: 'Trendline', color: '#f59e0b' }
  ];

  const lineStyles = [
    { value: 'solid', label: 'Solid' },
    { value: 'dashed', label: 'Dashed' },
    { value: 'dotted', label: 'Dotted' }
  ];

  const colors = [
    { value: '#3b82f6', label: 'Blue' },
    { value: '#10b981', label: 'Green' },
    { value: '#ef4444', label: 'Red' },
    { value: '#f59e0b', label: 'Orange' },
    { value: '#8b5cf6', label: 'Purple' },
    { value: '#06b6d4', label: 'Cyan' }
  ];

  useEffect(() => {
    // Subscribe to level changes
    const unsubscribe = replayLevelsService.subscribe((allLevels) => {
      const symbolLevels = replayLevelsService.getMultiTimeframeLevels(symbol);
      setLevels(symbolLevels);
    });

    // Get initial levels
    const symbolLevels = replayLevelsService.getMultiTimeframeLevels(symbol);
    setLevels(symbolLevels);

    return unsubscribe;
  }, [symbol]);

  const handleAddLevel = () => {
    const level = replayLevelsService.addLevel({
      ...newLevel,
      symbol,
      timeframe
    });

    if (onLevelAdd) {
      onLevelAdd(level);
    }

    // Reset form
    setNewLevel({
      price: 0,
      type: 'support',
      color: '#3b82f6',
      style: 'solid',
      width: 2,
      label: '',
      createdBy: 'replay_user'
    });
    setShowAddForm(false);
  };

  const handleRemoveLevel = (levelId: string) => {
    replayLevelsService.removeLevel(levelId);
    if (onLevelRemove) {
      onLevelRemove(levelId);
    }
  };

  const getTimeframeLabel = (tf: string) => {
    const labels: Record<string, string> = {
      'M1': '1m',
      'M5': '5m',
      'M15': '15m',
      'H1': '1h',
      'H4': '4h',
      'D1': '1d'
    };
    return labels[tf] || tf;
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Replay Levels</h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
        >
          {showAddForm ? 'Cancel' : 'Add Level'}
        </button>
      </div>

      {/* Add Level Form */}
      {showAddForm && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg border">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Price</label>
              <input
                type="number"
                step="0.0001"
                value={newLevel.price}
                onChange={(e) => setNewLevel({ ...newLevel, price: parseFloat(e.target.value) || 0 })}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                placeholder="0.0000"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
              <select
                value={newLevel.type}
                onChange={(e) => setNewLevel({ ...newLevel, type: e.target.value as any })}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
              >
                {levelTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Color</label>
              <select
                value={newLevel.color}
                onChange={(e) => setNewLevel({ ...newLevel, color: e.target.value })}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
              >
                {colors.map(color => (
                  <option key={color.value} value={color.value}>{color.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Style</label>
              <select
                value={newLevel.style}
                onChange={(e) => setNewLevel({ ...newLevel, style: e.target.value as any })}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
              >
                {lineStyles.map(style => (
                  <option key={style.value} value={style.value}>{style.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Width</label>
              <input
                type="number"
                min="1"
                max="5"
                value={newLevel.width}
                onChange={(e) => setNewLevel({ ...newLevel, width: parseInt(e.target.value) || 2 })}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Label</label>
              <input
                type="text"
                value={newLevel.label}
                onChange={(e) => setNewLevel({ ...newLevel, label: e.target.value })}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                placeholder="Optional label"
              />
            </div>
          </div>
          <button
            onClick={handleAddLevel}
            className="mt-3 w-full px-3 py-2 bg-green-500 text-white rounded text-sm hover:bg-green-600 transition-colors"
          >
            Add Replay Level
          </button>
        </div>
      )}

      {/* Levels List */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {levels.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-4">
            No replay levels added yet
          </div>
        ) : (
          levels.map(level => (
            <div
              key={level.id}
              className="flex items-center justify-between p-2 bg-gray-50 rounded border"
            >
              <div className="flex items-center space-x-2">
                <div
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: level.color }}
                ></div>
                <div className="text-sm">
                  <div className="font-medium">
                    {level.price.toFixed(4)}
                    {level.label && <span className="text-gray-500 ml-1">({level.label})</span>}
                  </div>
                  <div className="text-xs text-gray-500">
                    {level.type} • {getTimeframeLabel(level.timeframe)}
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleRemoveLevel(level.id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>

      {/* Statistics */}
      {levels.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            Replay Levels: {levels.length} total • 
            {levelTypes.map(type => {
              const count = levels.filter(l => l.type === type.value).length;
              return count > 0 ? ` ${type.label}: ${count}` : '';
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReplayLevelsPanel;
