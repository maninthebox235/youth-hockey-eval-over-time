import { Position } from '../types/trading';

interface Props {
  positions: Position[];
}

export function PositionsList({ positions }: Props) {
  if (positions.length === 0) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
        <h2 className="text-xl font-bold mb-4 text-white">Open Positions</h2>
        <div className="text-slate-400 text-center py-8">No open positions</div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
      <h2 className="text-xl font-bold mb-4 text-white">
        Open Positions ({positions.length})
      </h2>

      <div className="space-y-4">
        {positions.map((position, index) => {
          const pnlPercentage = ((position.unrealized_pnl / (position.entry_price * position.quantity)) * 100).toFixed(2);

          return (
            <div key={index} className="bg-slate-700 rounded-lg p-4 border-l-4"
                 style={{ borderLeftColor: position.side === 'long' ? '#10b981' : '#ef4444' }}>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xl font-bold text-white">{position.coin}</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      position.side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {position.side.toUpperCase()} {position.leverage}x
                    </span>
                  </div>
                  <div className="text-sm text-slate-400">
                    Entry: ${position.entry_price.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </div>
                </div>

                <div className="text-right">
                  <div className={`text-xl font-bold ${position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                  </div>
                  <div className={`text-sm ${position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {position.unrealized_pnl >= 0 ? '+' : ''}{pnlPercentage}%
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-sm mt-3">
                <div>
                  <span className="text-slate-400">Quantity:</span>
                  <span className="text-white ml-2">{position.quantity.toFixed(4)}</span>
                </div>
                <div>
                  <span className="text-slate-400">Opened:</span>
                  <span className="text-white ml-2">
                    {new Date(position.opened_at).toLocaleTimeString()}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Target:</span>
                  <span className="text-green-400 ml-2">${position.profit_target.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-slate-400">Stop:</span>
                  <span className="text-red-400 ml-2">${position.stop_loss.toFixed(2)}</span>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-slate-600">
                <div className="text-xs text-slate-400">Invalidation Condition:</div>
                <div className="text-sm text-slate-300 mt-1">{position.invalidation_condition}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
