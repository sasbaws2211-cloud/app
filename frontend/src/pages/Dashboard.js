import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { toast } from 'sonner';

export default function Dashboard() {
  const { user } = useAuth();
  const [wallet, setWallet] = useState(null);
  const [groups, setGroups] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [walletRes, groupsRes, transactionsRes] = await Promise.all([
        api.get('/wallet'),
        api.get('/groups'),
        api.get('/transactions')
      ]);
      
      setWallet(walletRes.data);
      setGroups(groupsRes.data);
      setTransactions(transactionsRes.data.slice(0, 5));
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
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
    <div className="min-h-screen bg-stone-50" data-testid="dashboard-page">
      <Navbar />
      
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="font-chivo text-4xl font-bold text-emerald-950">Welcome back, {user?.name}!</h1>
          <p className="text-slate-600 mt-2">Here's your financial overview</p>
        </div>

        {/* Wallet Balance Card */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-emerald-900 text-white p-8 rounded-2xl border-none shadow-xl" data-testid="wallet-balance-card">
            <p className="text-emerald-200 text-sm mb-2">PERSONAL WALLET</p>
            <h2 className="font-chivo text-5xl font-bold mb-4">GH¢ {wallet?.balance.toFixed(2)}</h2>
            <Link to="/wallet">
              <Button className="bg-white text-emerald-900 hover:bg-emerald-50 rounded-full" data-testid="manage-wallet-button">
                Manage Wallet
              </Button>
            </Link>
          </Card>

          <Card className="bg-white p-8 rounded-2xl border border-stone-200 shadow-sm" data-testid="groups-card">
            <p className="text-slate-600 text-sm mb-2">YOUR GROUPS</p>
            <h2 className="font-chivo text-5xl font-bold text-emerald-950 mb-4">{groups.length}</h2>
            <Link to="/groups">
              <Button variant="outline" className="rounded-full" data-testid="view-groups-button">
                View Groups
              </Button>
            </Link>
          </Card>

          <Card className="bg-white p-8 rounded-2xl border border-stone-200 shadow-sm" data-testid="total-contributions-card">
            <p className="text-slate-600 text-sm mb-2">TOTAL GROUP SAVINGS</p>
            <h2 className="font-chivo text-5xl font-bold text-emerald-950 mb-4">
              GH¢ {groups.reduce((sum, g) => sum + (g.wallet_balance || 0), 0).toFixed(2)}
            </h2>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Recent Transactions */}
          <div>
            <h2 className="font-chivo text-2xl font-bold text-emerald-950 mb-4">Recent Transactions</h2>
            <Card className="bg-white rounded-2xl border border-stone-200 shadow-sm p-6" data-testid="recent-transactions">
              {transactions.length === 0 ? (
                <p className="text-slate-500 text-center py-8">No transactions yet</p>
              ) : (
                <div className="space-y-4">
                  {transactions.map((tx) => (
                    <div key={tx.id} className="flex justify-between items-center border-b border-stone-100 pb-4 last:border-0" data-testid={`transaction-${tx.id}`}>
                      <div>
                        <p className="font-semibold text-emerald-950">{tx.transaction_type}</p>
                        <p className="text-sm text-slate-600">{new Date(tx.created_at).toLocaleDateString()}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-chivo font-bold text-emerald-900">GH¢ {tx.amount.toFixed(2)}</p>
                        <span className={`text-xs px-2 py-1 rounded-full ${
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

          {/* Your Groups */}
          <div>
            <h2 className="font-chivo text-2xl font-bold text-emerald-950 mb-4">Your Groups</h2>
            <Card className="bg-white rounded-2xl border border-stone-200 shadow-sm p-6" data-testid="your-groups">
              {groups.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-slate-500 mb-4">You're not in any groups yet</p>
                  <Link to="/groups">
                    <Button className="bg-emerald-900 hover:bg-emerald-800 text-white rounded-full" data-testid="create-first-group">
                      Create Your First Group
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {groups.slice(0, 3).map((group) => (
                    <Link 
                      key={group.id} 
                      to={`/groups/${group.id}`}
                      className="block border-b border-stone-100 pb-4 last:border-0 hover:bg-stone-50 rounded-lg p-3 transition-colors"
                      data-testid={`group-${group.id}`}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-semibold text-emerald-950">{group.name}</p>
                          <p className="text-sm text-slate-600">{group.member_count} members</p>
                        </div>
                        <div className="text-right">
                          <p className="font-chivo font-bold text-emerald-900">GH¢ {group.wallet_balance?.toFixed(2)}</p>
                          <p className="text-xs text-slate-500">Balance</p>
                        </div>
                      </div>
                    </Link>
                  ))}
                  {groups.length > 3 && (
                    <Link to="/groups">
                      <Button variant="outline" className="w-full rounded-full" data-testid="view-all-groups">
                        View All Groups
                      </Button>
                    </Link>
                  )}
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}