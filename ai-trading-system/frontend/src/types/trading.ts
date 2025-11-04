export type TradingSignal = 'buy_to_enter' | 'sell_to_enter' | 'hold' | 'close';
export type Coin = 'BTC' | 'ETH' | 'SOL' | 'BNB' | 'DOGE' | 'XRP';

export interface TradingDecision {
  signal: TradingSignal;
  coin: Coin;
  quantity: number;
  leverage: number;
  profit_target: number;
  stop_loss: number;
  invalidation_condition: string;
  confidence: number;
  risk_usd: number;
  justification: string;
}

export interface Position {
  coin: Coin;
  entry_price: number;
  quantity: number;
  leverage: number;
  side: 'long' | 'short';
  unrealized_pnl: number;
  profit_target: number;
  stop_loss: number;
  invalidation_condition: string;
  opened_at: string;
}

export interface AccountState {
  available_cash: number;
  total_equity: number;
  positions: Position[];
  unrealized_pnl: number;
  realized_pnl: number;
  sharpe_ratio: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
}

export interface TradeExecution {
  id: string;
  timestamp: string;
  decision: TradingDecision;
  execution_price: number;
  status: string;
  pnl: number | null;
  close_reason: string | null;
}

export interface AutoExecuteResponse {
  decision: TradingDecision;
  execution: TradeExecution;
  auto_closes: TradeExecution[];
  account_state: AccountState;
}
