import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';

export default function GroupDetail() {
  const { groupId } = useParams();
  const { user } = useAuth();
  const [group, setGroup] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [contributionAmount, setContributionAmount] = useState('');
  const [contributeOpen, setContributeOpen] = useState(false);

  useEffect(() => {
    fetchGroupData();
  }, [groupId]);

  const fetchGroupData = async () => {
    try {
      const [groupRes, transactionsRes] = await Promise.all([
        api.get(`/groups/${groupId}`),
        api.get(`/groups/${groupId}/transactions`)
      ]);
      
      setGroup(groupRes.data);
      setTransactions(transactionsRes.data);
    } catch (error) {
      toast.error('Failed to load group data');
    } finally {
      setLoading(false);
    }
  };

  const handleContribute = async (e) => {
    e.preventDefault();

    try {
      await api.post(`/groups/${groupId}/contribute`, {
        group_id: parseInt(groupId),
        amount: parseFloat(contributionAmount)
      });
      toast.success('Contribution successful!');
      setContributionAmount('');
      fetchGroupData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Contribution failed');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!group) {
    return (
      <div className="min-h-screen bg-stone-50">
        <Navbar />
        <div className="container mx-auto px-6 py-8">
          <p className="text-center text-slate-500">Group not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50" data-testid="group-detail-page">
      <Navbar />
      
      <div className="container mx-auto px-6 py-8">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="font-chivo text-4xl font-bold text-emerald-950 mb-2">{group.name}</h1>
            {group.description && <p className="text-slate-600">{group.description}</p>}
            <div className="flex items-center space-x-4 mt-4">
              <span className="text-sm text-slate-500">Invite Code: <span className="font-mono font-bold text-emerald-900">{group.invite_code}</span></span>
            </div>
          </div>
          
          <Link to={`/groups/${groupId}/chat`}>
            <Button className="bg-sky-600 hover:bg-sky-700 text-white rounded-full" data-testid="group-chat-button">
              Group Chat
            </Button>
          </Link>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-emerald-900 text-white p-8 rounded-2xl border-none shadow-xl" data-testid="group-balance-card">
            <p className="text-emerald-200 text-sm mb-2">GROUP BALANCE</p>
            <h2 className="font-chivo text-5xl font-bold mb-4">GH₵ {group.wallet_balance?.toFixed(2) || '0.00'}</h2>
            
            <Dialog>
              <DialogTrigger asChild>
                <Button className="bg-white text-emerald-900 hover:bg-emerald-50 rounded-full" data-testid="contribute-button">
                  Contribute
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Contribute to Group</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleContribute} className="space-y-4" data-testid="contribute-form">
                  <div className="space-y-2">
                    <Label htmlFor="contribution">Amount (GH₵)</Label>
                    <Input
                      id="contribution"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={contributionAmount}
                      onChange={(e) => setContributionAmount(e.target.value)}
                      required
                      data-testid="contribution-amount-input"
                    />
                    {group.contribution_amount > 0 && (
                      <p className="text-sm text-slate-500">Recommended: GH₵ {group.contribution_amount.toFixed(2)}</p>
                    )}
                  </div>
                  <Button type="submit" className="w-full bg-emerald-900 hover:bg-emerald-800 rounded-full" data-testid="contribute-submit">
                    Contribute
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </Card>

          <Card className="bg-white p-8 rounded-2xl border border-stone-200 shadow-sm">
            <p className="text-slate-600 text-sm mb-2">MEMBERS</p>
            <h2 className="font-chivo text-5xl font-bold text-emerald-950">{group.member_count || 0}</h2>
          </Card>

          <Card className="bg-white p-8 rounded-2xl border border-stone-200 shadow-sm">
            <p className="text-slate-600 text-sm mb-2">CONTRIBUTION</p>
            <h2 className="font-chivo text-3xl font-bold text-emerald-950">GH₵ {group.contribution_amount.toFixed(2)}</h2>
            <p className="text-slate-500 text-sm mt-1">{group.contribution_frequency}</p>
          </Card>
        </div>

        {/* Transaction Ledger */}
        <Card className="bg-white rounded-2xl border border-stone-200 shadow-sm p-8">
          <h2 className="font-chivo text-2xl font-bold text-emerald-950 mb-6">Transaction Ledger</h2>
          
          {transactions.length === 0 ? (
            <p className="text-slate-500 text-center py-12">No transactions yet</p>
          ) : (
            <div className="space-y-4" data-testid="transaction-ledger">
              {transactions.map((tx) => (
                <div 
                  key={tx.id} 
                  className="flex justify-between items-center border-b border-stone-100 pb-4 last:border-0"
                  data-testid={`ledger-transaction-${tx.id}`}
                >
                  <div>
                    <p className="font-semibold text-emerald-950 capitalize">{tx.transaction_type}</p>
                    <p className="text-sm text-slate-600">{new Date(tx.created_at).toLocaleString()}</p>
                    {tx.description && <p className="text-sm text-slate-500">{tx.description}</p>}
                  </div>
                  <div className="text-right">
                    <p className="font-chivo font-bold text-emerald-900">GH₵ {tx.amount.toFixed(2)}</p>
                    <span className={`text-xs px-3 py-1 rounded-full ${
                      tx.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
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