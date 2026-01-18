import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';

export default function Wallet() {
  const { user } = useAuth();
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [depositOpen, setDepositOpen] = useState(false);
  const [withdrawOpen, setWithdrawOpen] = useState(false);

  const [depositData, setDepositData] = useState({
    amount: '',
    phone_number: '',
    provider: 'MTN'
  });

  const [withdrawData, setWithdrawData] = useState({
    amount: '',
    phone_number: '',
    provider: 'MTN'
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [walletRes, transactionsRes] = await Promise.all([
        api.get('/wallet'),
        api.get('/transactions')
      ]);
      
      setWallet(walletRes.data);
      setTransactions(transactionsRes.data);
    } catch (error) {
      toast.error('Failed to load wallet data');
    } finally {
      setLoading(false);
    }
  };

  const handleDeposit = async (e) => {
    e.preventDefault();
    setActionLoading(true);

    try {
      await api.post('/wallet/deposit', depositData);
      toast.success('Deposit initiated! Check your phone for prompt.');
      setDepositData({ amount: '', phone_number: '', provider: 'MTN' });
      setDepositOpen(false);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Deposit failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleWithdraw = async (e) => {
    e.preventDefault();
    setActionLoading(true);

    try {
      await api.post('/wallet/withdraw', withdrawData);
      toast.success('Withdrawal initiated!');
      setWithdrawData({ amount: '', phone_number: '', provider: 'MTN' });
      setWithdrawOpen(false);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Withdrawal failed');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50" data-testid="wallet-page">
      <Navbar />
      
      <div className="container mx-auto px-6 py-8">
        <h1 className="font-chivo text-4xl font-bold text-emerald-950 mb-8">Personal Wallet</h1>

        {/* Wallet Balance */}
        <Card className="bg-emerald-900 text-white p-12 rounded-2xl border-none shadow-xl mb-8" data-testid="wallet-balance">
          <p className="text-emerald-200 text-sm mb-2">CURRENT BALANCE</p>
          <h2 className="font-chivo text-6xl font-bold mb-6">GH₵ {wallet?.balance.toFixed(2)}</h2>
          
          <div className="flex space-x-4">
            <Dialog open={depositOpen} onOpenChange={setDepositOpen}>
              <DialogTrigger asChild>
                <Button className="bg-white text-emerald-900 hover:bg-emerald-50 rounded-full px-8" data-testid="deposit-button">
                  Deposit Money
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Deposit Money</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleDeposit} className="space-y-4" data-testid="deposit-form">
                  <div className="space-y-2">
                    <Label htmlFor="deposit-amount">Amount (GH₵)</Label>
                    <Input
                      id="deposit-amount"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={depositData.amount}
                      onChange={(e) => setDepositData({ ...depositData, amount: e.target.value })}
                      required
                      data-testid="deposit-amount-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="deposit-phone">Phone Number</Label>
                    <Input
                      id="deposit-phone"
                      type="tel"
                      placeholder="+233XXXXXXXXX"
                      value={depositData.phone_number}
                      onChange={(e) => setDepositData({ ...depositData, phone_number: e.target.value })}
                      required
                      data-testid="deposit-phone-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="deposit-provider">Mobile Money Provider</Label>
                    <Select 
                      value={depositData.provider}
                      onValueChange={(value) => setDepositData({ ...depositData, provider: value })}
                    >
                      <SelectTrigger data-testid="deposit-provider-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MTN">MTN Mobile Money</SelectItem>
                        <SelectItem value="Vodafone">Vodafone Cash</SelectItem>
                        <SelectItem value="AirtelTigo">AirtelTigo Money</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button 
                    type="submit" 
                    className="w-full bg-emerald-900 hover:bg-emerald-800 rounded-full"
                    disabled={actionLoading}
                    data-testid="deposit-submit"
                  >
                    {actionLoading ? 'Processing...' : 'Deposit'}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>

            <Dialog>
              <DialogTrigger asChild>
                <Button className="bg-emerald-700 hover:bg-emerald-600 text-white rounded-full px-8" data-testid="withdraw-button">
                  Withdraw Money
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Withdraw Money</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleWithdraw} className="space-y-4" data-testid="withdraw-form">
                  <div className="space-y-2">
                    <Label htmlFor="withdraw-amount">Amount (GH₵)</Label>
                    <Input
                      id="withdraw-amount"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={withdrawData.amount}
                      onChange={(e) => setWithdrawData({ ...withdrawData, amount: e.target.value })}
                      required
                      data-testid="withdraw-amount-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="withdraw-phone">Phone Number</Label>
                    <Input
                      id="withdraw-phone"
                      type="tel"
                      placeholder="+233XXXXXXXXX"
                      value={withdrawData.phone_number}
                      onChange={(e) => setWithdrawData({ ...withdrawData, phone_number: e.target.value })}
                      required
                      data-testid="withdraw-phone-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="withdraw-provider">Mobile Money Provider</Label>
                    <Select 
                      value={withdrawData.provider}
                      onValueChange={(value) => setWithdrawData({ ...withdrawData, provider: value })}
                    >
                      <SelectTrigger data-testid="withdraw-provider-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MTN">MTN Mobile Money</SelectItem>
                        <SelectItem value="Vodafone">Vodafone Cash</SelectItem>
                        <SelectItem value="AirtelTigo">AirtelTigo Money</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button 
                    type="submit" 
                    className="w-full bg-emerald-900 hover:bg-emerald-800 rounded-full"
                    disabled={actionLoading}
                    data-testid="withdraw-submit"
                  >
                    {actionLoading ? 'Processing...' : 'Withdraw'}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </Card>

        {/* Transaction History */}
        <Card className="bg-white rounded-2xl border border-stone-200 shadow-sm p-8">
          <h2 className="font-chivo text-2xl font-bold text-emerald-950 mb-6">Transaction History</h2>
          
          {transactions.length === 0 ? (
            <p className="text-slate-500 text-center py-12">No transactions yet</p>
          ) : (
            <div className="space-y-4" data-testid="transaction-list">
              {transactions.map((tx) => (
                <div 
                  key={tx.id} 
                  className="flex justify-between items-center border-b border-stone-100 pb-4 last:border-0"
                  data-testid={`transaction-item-${tx.id}`}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      tx.transaction_type === 'deposit' ? 'bg-green-100' :
                      tx.transaction_type === 'withdrawal' ? 'bg-red-100' :
                      'bg-blue-100'
                    }`}>
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        {tx.transaction_type === 'deposit' && (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        )}
                        {tx.transaction_type === 'withdrawal' && (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                        )}
                        {tx.transaction_type === 'transfer' && (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        )}
                      </svg>
                    </div>
                    <div>
                      <p className="font-semibold text-emerald-950 capitalize">{tx.transaction_type}</p>
                      <p className="text-sm text-slate-600">{new Date(tx.created_at).toLocaleString()}</p>
                      {tx.description && <p className="text-sm text-slate-500">{tx.description}</p>}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-chivo font-bold text-emerald-900">GH₵ {tx.amount.toFixed(2)}</p>
                    <span className={`text-xs px-3 py-1 rounded-full ${
                      tx.status === 'completed' ? 'bg-green-100 text-green-800' :
                      tx.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {tx.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
