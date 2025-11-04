import { TradeExecution } from '../types/trading';

interface Props {
  trades: TradeExecution[];
}

export function TradeHistory({ trades }: Props) {
  if (trades.length === 0) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
        <h2 className="text-xl font-bold mb-4 text-white">Recent Trades</h2>
        <div className="text-slate-400 text-center py-8">No trades yet</div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'executed': return 'text-green-400';
      case 'closed': return 'text-blue-400';
      case 'failed': return 'text-red-400';
      case 'held': return 'text-slate-400';
      default: return 'text-slate-400';
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy_to_enter': return 'bg-green-500/20 text-green-400';
      case 'sell_to_enter': return 'bg-red-500/20 text-red-400';
      case 'close': return 'bg-blue-500/20 text-blue-400';
      case 'hold': return 'bg-slate-500/20 text-slate-400';
      default: return 'bg-slate-500/20 text-slate-400';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
      <h2 className="text-xl font-bold mb-4 text-white">Recent Trades</h2>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {trades.slice().reverse().map((trade) => (
          <div key={trade.id} className="bg-slate-700 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white">{trade.decision.coin}</span>
                <span className={`text-xs px-2 py-1 rounded ${getSignalColor(trade.decision.signal)}`}>
                  {trade.decision.signal.replace('_', ' ').toUpperCase()}
                </span>
                <span className={`text-xs ${getStatusColor(trade.status)}`}>
                  {trade.status}
                </span>
              </div>

              <div className="text-xs text-slate-400">
                {new Date(trade.timestamp).toLocaleString()}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-slate-400">Price:</span>
                <span className="text-white ml-2">${trade.execution_price.toFixed(2)}</span>
              </div>

              {trade.pnl !== null && (
                <div>
                  <span className="text-slate-400">PnL:</span>
                  <span className={`ml-2 font-semibold ${trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                  </span>
                </div>
              )}

              <div>
                <span className="text-slate-400">Leverage:</span>
                <span className="text-white ml-2">{trade.decision.leverage}x</span>
              </div>

              <div>
                <span className="text-slate-400">Confidence:</span>
                <span className="text-white ml-2">{(trade.decision.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>

            {trade.decision.justification && (
              <div className="mt-2 pt-2 border-t border-slate-600">
                <div className="text-xs text-slate-400">Justification:</div>
                <div className="text-sm text-slate-300 mt-1">{trade.decision.justification}</div>
              </div>
            )}

            {trade.close_reason && (
              <div className="mt-2 text-xs">
                <span className="text-slate-400">Close Reason:</span>
                <span className="text-slate-300 ml-2">{trade.close_reason}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
