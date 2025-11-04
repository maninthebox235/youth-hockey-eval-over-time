import { AccountState } from '../types/trading';

interface Props {
  accountState: AccountState;
}

export function AccountOverview({ accountState }: Props) {
  const winRate = accountState.total_trades > 0
    ? (accountState.winning_trades / accountState.total_trades) * 100
    : 0;

  const totalPnL = accountState.realized_pnl + accountState.unrealized_pnl;
  const pnlPercentage = ((totalPnL / 10000) * 100).toFixed(2);

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
      <h2 className="text-2xl font-bold mb-4 text-white">Account Overview</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-700 rounded p-4">
          <div className="text-slate-400 text-sm">Total Equity</div>
          <div className="text-2xl font-bold text-white">
            ${accountState.total_equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className={`text-sm ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {totalPnL >= 0 ? '+' : ''}{pnlPercentage}%
          </div>
        </div>

        <div className="bg-slate-700 rounded p-4">
          <div className="text-slate-400 text-sm">Available Cash</div>
          <div className="text-2xl font-bold text-white">
            ${accountState.available_cash.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        <div className="bg-slate-700 rounded p-4">
          <div className="text-slate-400 text-sm">Total PnL</div>
          <div className={`text-2xl font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {totalPnL >= 0 ? '+' : ''}${totalPnL.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-xs text-slate-400">
            Realized: ${accountState.realized_pnl.toFixed(2)} | Unrealized: ${accountState.unrealized_pnl.toFixed(2)}
          </div>
        </div>

        <div className="bg-slate-700 rounded p-4">
          <div className="text-slate-400 text-sm">Sharpe Ratio</div>
          <div className={`text-2xl font-bold ${
            accountState.sharpe_ratio > 2 ? 'text-green-400' :
            accountState.sharpe_ratio > 1 ? 'text-yellow-400' :
            accountState.sharpe_ratio > 0 ? 'text-orange-400' :
            'text-red-400'
          }`}>
            {accountState.sharpe_ratio.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mt-4">
        <div className="bg-slate-700 rounded p-3">
          <div className="text-slate-400 text-xs">Total Trades</div>
          <div className="text-xl font-semibold text-white">{accountState.total_trades}</div>
        </div>

        <div className="bg-slate-700 rounded p-3">
          <div className="text-slate-400 text-xs">Win Rate</div>
          <div className="text-xl font-semibold text-white">{winRate.toFixed(1)}%</div>
          <div className="text-xs text-slate-400">
            {accountState.winning_trades}W / {accountState.losing_trades}L
          </div>
        </div>

        <div className="bg-slate-700 rounded p-3">
          <div className="text-slate-400 text-xs">Open Positions</div>
          <div className="text-xl font-semibold text-white">{accountState.positions.length}</div>
        </div>
      </div>
    </div>
  );
}
