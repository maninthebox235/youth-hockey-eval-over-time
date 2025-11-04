import { useState, useEffect } from 'react';
import { AccountOverview } from './components/AccountOverview';
import { PositionsList } from './components/PositionsList';
import { TradeHistory } from './components/TradeHistory';
import { LatestDecision } from './components/LatestDecision';
import { api } from './services/api';
import { AccountState, TradeExecution, TradingDecision } from './types/trading';

function App() {
  const [accountState, setAccountState] = useState<AccountState | null>(null);
  const [tradeHistory, setTradeHistory] = useState<TradeExecution[]>([]);
  const [latestDecision, setLatestDecision] = useState<TradingDecision | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoTrading, setAutoTrading] = useState(false);
  const [autoTradingInterval, setAutoTradingInterval] = useState<number | null>(null);

  // Fetch initial data
  useEffect(() => {
    fetchAccountState();
    fetchTradeHistory();
  }, []);

  const fetchAccountState = async () => {
    try {
      const state = await api.getAccountState();
      setAccountState(state);
      setError(null);
    } catch (err) {
      setError('Failed to fetch account state');
      console.error(err);
    }
  };

  const fetchTradeHistory = async () => {
    try {
      const history = await api.getTradeHistory(50);
      setTradeHistory(history);
    } catch (err) {
      console.error('Failed to fetch trade history:', err);
    }
  };

  const handleExecuteTrade = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await api.autoExecuteTrade();
      setLatestDecision(result.decision);
      setAccountState(result.account_state);
      await fetchTradeHistory();
    } catch (err) {
      setError('Failed to execute trade: ' + (err as Error).message);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCheckPositions = async () => {
    try {
      const result = await api.checkPositions();
      setAccountState(result.account_state);
      if (result.closed_positions.length > 0) {
        await fetchTradeHistory();
      }
    } catch (err) {
      setError('Failed to check positions: ' + (err as Error).message);
      console.error(err);
    }
  };

  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset the trading engine? All data will be lost.')) {
      return;
    }

    try {
      await api.resetEngine();
      setLatestDecision(null);
      await fetchAccountState();
      await fetchTradeHistory();
      setError(null);
    } catch (err) {
      setError('Failed to reset engine: ' + (err as Error).message);
      console.error(err);
    }
  };

  const toggleAutoTrading = () => {
    if (autoTrading) {
      // Stop auto trading
      if (autoTradingInterval) {
        clearInterval(autoTradingInterval);
        setAutoTradingInterval(null);
      }
      setAutoTrading(false);
    } else {
      // Start auto trading (every 3 minutes)
      setAutoTrading(true);
      const interval = window.setInterval(() => {
        handleExecuteTrade();
        handleCheckPositions();
      }, 180000); // 3 minutes
      setAutoTradingInterval(interval);

      // Execute first trade immediately
      handleExecuteTrade();
    }
  };

  if (!accountState) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            AI Trading System
          </h1>
          <p className="text-slate-400">
            LLM-powered autonomous trading based on nof1.ai Alpha Arena
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 mb-6">
            <div className="text-red-400">{error}</div>
          </div>
        )}

        {/* Control Buttons */}
        <div className="bg-slate-800 rounded-lg p-6 shadow-xl mb-6">
          <div className="flex flex-wrap gap-4">
            <button
              onClick={handleExecuteTrade}
              disabled={isLoading || autoTrading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              {isLoading ? 'Executing...' : 'Execute Trade'}
            </button>

            <button
              onClick={handleCheckPositions}
              disabled={autoTrading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              Check Positions
            </button>

            <button
              onClick={toggleAutoTrading}
              className={`${
                autoTrading
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-purple-600 hover:bg-purple-700'
              } text-white px-6 py-3 rounded-lg font-semibold transition-colors`}
            >
              {autoTrading ? 'Stop Auto Trading' : 'Start Auto Trading'}
            </button>

            <button
              onClick={handleReset}
              disabled={autoTrading}
              className="bg-slate-600 hover:bg-slate-700 disabled:bg-slate-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              Reset
            </button>

            <button
              onClick={fetchAccountState}
              className="bg-slate-600 hover:bg-slate-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              Refresh
            </button>
          </div>

          {autoTrading && (
            <div className="mt-4 text-yellow-400 text-sm flex items-center gap-2">
              <span className="animate-pulse">●</span>
              Auto-trading enabled - executing trades every 3 minutes
            </div>
          )}
        </div>

        {/* Account Overview */}
        <div className="mb-6">
          <AccountOverview accountState={accountState} />
        </div>

        {/* Latest Decision and Positions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <LatestDecision decision={latestDecision} />
          <PositionsList positions={accountState.positions} />
        </div>

        {/* Trade History */}
        <TradeHistory trades={tradeHistory} />
      </div>
    </div>
  );
}

export default App;
