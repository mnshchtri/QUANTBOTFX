import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Instrument {
  symbol: string;
  name: string;
  category: string;
  data_available: boolean;
  last_update: string;
  timeframes: string[];
  data_sources: string[];
  status: string;
  timeframe_data: { [key: string]: boolean };
}

interface DataSource {
  name: string;
  api_key_required: boolean;
  api_key_available: boolean;
  status: string;
  last_check: string;
  instruments_supported: string[];
  timeframes_supported: string[];
}

interface InstrumentManagerProps {
  onInstrumentSelect?: (instrument: Instrument) => void;
}

const InstrumentManager: React.FC<InstrumentManagerProps> = ({ onInstrumentSelect }) => {
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const categories = ['all', 'major', 'minor', 'exotic'];
  const timeframes = ['all', 'M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1'];

  useEffect(() => {
    fetchInstruments();
    fetchDataSources();
  }, []);

  const fetchInstruments = async () => {
    try {
      const response = await axios.get('/instruments');
      setInstruments(response.data.instruments);
    } catch (error) {
      // Remove fallback to mock data - fail properly if API is not available
      console.error('Failed to fetch instruments:', error);
      setInstruments([]);
      setLoading(false);
    }
  };

  const fetchDataSources = async () => {
    try {
      const response = await axios.get('/data-sources');
      setDataSources(response.data.data_sources);
    } catch (error) {
      // Remove fallback to mock data - fail properly if API is not available
      console.error('Failed to fetch data sources:', error);
      setDataSources([]);
    } finally {
      setLoading(false);
    }
  };

  // Remove mock data functions - no fallback data allowed

  const filteredInstruments = instruments.filter(instrument => {
    const matchesCategory = selectedCategory === 'all' || instrument.category === selectedCategory;
    const matchesSearch = instrument.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         instrument.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTimeframe = selectedTimeframe === 'all' || 
                            (instrument.timeframe_data && instrument.timeframe_data[selectedTimeframe]);

    return matchesCategory && matchesSearch && matchesTimeframe;
  });

  const getTimeframeStatus = (instrument: Instrument, timeframe: string) => {
    return instrument.timeframe_data && instrument.timeframe_data[timeframe];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600';
      case 'inactive': return 'text-red-600';
      case 'maintenance': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const handleInstrumentSelect = (instrument: Instrument) => {
    if (onInstrumentSelect) {
      onInstrumentSelect(instrument);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Instrument Manager</h2>
        <button
          onClick={fetchInstruments}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">Category</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Timeframe</label>
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeframes.map(timeframe => (
              <option key={timeframe} value={timeframe}>
                {timeframe}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search instruments..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-end">
          <span className="text-sm text-gray-600">
            {filteredInstruments.length} instruments available
          </span>
        </div>
      </div>

      {/* Instruments List */}
      <div className="space-y-4">
        {filteredInstruments.map((instrument) => (
          <div
            key={instrument.symbol}
            className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
              instrument.data_available ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
            }`}
            onClick={() => handleInstrumentSelect(instrument)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <h3 className="text-lg font-semibold text-gray-800">{instrument.symbol}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    instrument.data_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {instrument.data_available ? 'Available' : 'Unavailable'}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800`}>
                    {instrument.category}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{instrument.name}</p>
                
                {/* Timeframes */}
                <div className="flex flex-wrap gap-2 mt-3">
                  {instrument.timeframes.map(timeframe => (
                    <span
                      key={timeframe}
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        getTimeframeStatus(instrument, timeframe)
                          ? 'bg-green-100' : 'bg-gray-100'
                      }`}
                    >
                      {timeframe}
                    </span>
                  ))}
                </div>

                {/* Data Sources */}
                <div className="flex flex-wrap gap-2 mt-2">
                  {instrument.data_sources.map(source => (
                    <span
                      key={source}
                      className="px-2 py-1 text-xs font-medium rounded bg-purple-100 text-purple-800"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              </div>

              <div className="text-right">
                <div className={`text-sm font-medium ${getStatusColor(instrument.status)}`}>
                  {instrument.status}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Updated: {new Date(instrument.last_update).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Data Sources Summary */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Data Sources</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dataSources.map(source => (
            <div key={source.name} className="bg-white p-3 rounded-lg border">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-800">{source.name}</span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  source.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {source.status}
                </span>
              </div>
              <div className="text-xs text-gray-600 mt-2">
                {source.instruments_supported.length} instruments supported
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default InstrumentManager; 