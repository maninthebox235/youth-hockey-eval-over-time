import { TradingDecision } from '../types/trading';

interface Props {
  decision: TradingDecision | null;
}

export function LatestDecision({ decision }: Props) {
  if (!decision) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
        <h2 className="text-xl font-bold mb-4 text-white">Latest LLM Decision</h2>
        <div className="text-slate-400 text-center py-8">
          Click "Execute Trade" to get a decision from the LLM
        </div>
      </div>
    );
  }

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy_to_enter': return 'bg-green-500 text-white';
      case 'sell_to_enter': return 'bg-red-500 text-white';
      case 'close': return 'bg-blue-500 text-white';
      case 'hold': return 'bg-slate-500 text-white';
      default: return 'bg-slate-500 text-white';
    }
  };

  const rewardRiskRatio = decision.profit_target / decision.stop_loss;

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
      <h2 className="text-xl font-bold mb-4 text-white">Latest LLM Decision</h2>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold text-white">{decision.coin}</span>
            <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${getSignalColor(decision.signal)}`}>
              {decision.signal.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          <div className="text-right">
            <div className="text-xs text-slate-400">Confidence</div>
            <div className="text-xl font-bold text-white">
              {(decision.confidence * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-slate-700 rounded p-3">
            <div className="text-xs text-slate-400">Quantity</div>
            <div className="text-lg font-semibold text-white">{decision.quantity.toFixed(4)}</div>
          </div>

          <div className="bg-slate-700 rounded p-3">
            <div className="text-xs text-slate-400">Leverage</div>
            <div className="text-lg font-semibold text-white">{decision.leverage}x</div>
          </div>

          <div className="bg-slate-700 rounded p-3">
            <div className="text-xs text-slate-400">Risk (USD)</div>
            <div className="text-lg font-semibold text-white">${decision.risk_usd.toFixed(0)}</div>
          </div>

          <div className="bg-slate-700 rounded p-3">
            <div className="text-xs text-slate-400">R:R Ratio</div>
            <div className={`text-lg font-semibold ${rewardRiskRatio >= 2 ? 'text-green-400' : 'text-yellow-400'}`}>
              {rewardRiskRatio.toFixed(2)}:1
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-700 rounded p-3">
            <div className="text-xs text-slate-400">Profit Target</div>
            <div className="text-lg font-semibold text-green-400">${decision.profit_target.toFixed(2)}</div>
          </div>

          <div className="bg-slate-700 rounded p-3">
            <div className="text-xs text-slate-400">Stop Loss</div>
            <div className="text-lg font-semibold text-red-400">${decision.stop_loss.toFixed(2)}</div>
          </div>
        </div>

        <div className="bg-slate-700 rounded p-4">
          <div className="text-xs text-slate-400 mb-2">Justification</div>
          <div className="text-sm text-slate-200">{decision.justification}</div>
        </div>

        <div className="bg-slate-700 rounded p-4">
          <div className="text-xs text-slate-400 mb-2">Invalidation Condition</div>
          <div className="text-sm text-slate-200">{decision.invalidation_condition}</div>
        </div>
      </div>
    </div>
  );
}
