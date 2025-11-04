import { AccountState, TradeExecution, AutoExecuteResponse } from '../types/trading';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  async getAccountState(): Promise<AccountState> {
    const response = await fetch(`${API_BASE_URL}/api/account`);
    if (!response.ok) throw new Error('Failed to fetch account state');
    return response.json();
  },

  async autoExecuteTrade(): Promise<AutoExecuteResponse> {
    const response = await fetch(`${API_BASE_URL}/api/trade/auto-execute`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to auto-execute trade');
    return response.json();
  },

  async getTradeHistory(limit: number = 50): Promise<TradeExecution[]> {
    const response = await fetch(`${API_BASE_URL}/api/trades?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch trade history');
    return response.json();
  },

  async checkPositions(): Promise<{ closed_positions: TradeExecution[]; account_state: AccountState }> {
    const response = await fetch(`${API_BASE_URL}/api/positions/check`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to check positions');
    return response.json();
  },

  async resetEngine(): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/reset`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to reset engine');
    return response.json();
  },
};
