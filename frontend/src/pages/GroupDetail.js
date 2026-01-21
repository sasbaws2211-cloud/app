<<<<<<< HEAD
import React, { useEffect, useState } from 'react';
=======
import React, { useEffect, useState, useCallback } from 'react';
>>>>>>> 17c6933 (initial update)
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
<<<<<<< HEAD
  const [loading, setLoading] = useState(true);
  const [contributionAmount, setContributionAmount] = useState('');
  const [contributeOpen, setContributeOpen] = useState(false);

  useEffect(() => {
    fetchGroupData();
  }, [groupId]);

  const fetchGroupData = async () => {
=======
  const [policiesOpen, setPoliciesOpen] = useState(false);
  const [policiesText, setPoliciesText] = useState('');
  const [loading, setLoading] = useState(true);
  const [contributionAmount, setContributionAmount] = useState('');
  const [contributeOpen, setContributeOpen] = useState(false);
  const [disburseOpen, setDisburseOpen] = useState(false);
  const [disburseAmount, setDisburseAmount] = useState('');
  const [disburseRecipient, setDisburseRecipient] = useState('');
  const [disburseDescription, setDisburseDescription] = useState('');

  const fetchGroupData = useCallback(async () => {
>>>>>>> 17c6933 (initial update)
    try {
      const [groupRes, transactionsRes] = await Promise.all([
        api.get(`/groups/${groupId}`),
        api.get(`/groups/${groupId}/transactions`)
      ]);
<<<<<<< HEAD
      
      setGroup(groupRes.data);
      setTransactions(transactionsRes.data);
    } catch (error) {
      toast.error('Failed to load group data');
    } finally {
      setLoading(false);
    }
  };
=======
      // Validate group response shape (expect an object with uid/name)
      const g = groupRes.data;
      if (!g || typeof g !== 'object' || !g.uid || !g.name) {
        // Backend may have returned a validation error object (e.g. { detail: [...] })
        console.error('Unexpected group response', groupRes.data);
        toast.error('Failed to load group data (invalid response)');
        setLoading(false);
        return;
      }

      // Transactions should be an array — otherwise ignore and show empty
      const txs = Array.isArray(transactionsRes.data) ? transactionsRes.data : [];

  // populate policies text if present
  setGroup(g);
  setPoliciesText(g.policies || '');
      setTransactions(txs);
    } catch (error) {
      console.error('Error fetching group data', error);
      toast.error(error.response?.data?.detail || 'Failed to load group data');
    } finally {
      setLoading(false);
    }
  }, [groupId]); 

  console.log('GroupDetail render, groupId:', groupId);

  useEffect(() => {
    fetchGroupData();
  }, [fetchGroupData]);
>>>>>>> 17c6933 (initial update)

  const handleContribute = async (e) => {
    e.preventDefault();

    try {
      await api.post(`/groups/${groupId}/contribute`, {
<<<<<<< HEAD
        group_id: parseInt(groupId),
=======
        // send group_uid as a string (UUID) to match backend expectations
        group_uid: String(groupId),
>>>>>>> 17c6933 (initial update)
        amount: parseFloat(contributionAmount)
      });
      toast.success('Contribution successful!');
      setContributionAmount('');
      setContributeOpen(false);
      fetchGroupData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Contribution failed');
    }
  };

<<<<<<< HEAD
=======
  const isCurrentUserAdmin = () => {
    if (!group || !group.members || !user) return false;
    return group.members.some((m) => m.user_uid === user.uid && m.is_admin === true);
  };

  const handleRemoveMember = async (member) => {
    if (!isCurrentUserAdmin()) {
      toast.error('Only admins can remove members');
      return;
    }
    try {
      await api.delete(`/groups/${groupId}/members/${member.user_uid}`);
      toast.success('Member removed');
      fetchGroupData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to remove member');
    }
  };

  const handlePoliciesSave = async (e) => {
    e.preventDefault();
    if (!isCurrentUserAdmin()) {
      toast.error('Only admins can update policies');
      return;
    }
    try {
      await api.patch(`/groups/${groupId}/policies`, { policies: policiesText });
      toast.success('Policies updated');
      setPoliciesOpen(false);
      fetchGroupData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update policies');
    }
  };

  const handleDisburse = async (e) => {
    e.preventDefault();
    if (!isCurrentUserAdmin()) {
      toast.error('Only admins can disburse funds');
      return;
    }

    if (!disburseRecipient) {
      toast.error('Select a recipient');
      return;
    }
    // Confirmation step
    const recipientObj = (group.members || []).find((m) => String(m.user_uid) === String(disburseRecipient));
    const recipientName = recipientObj ? recipientObj.name : disburseRecipient;
    const confirmed = window.confirm(`Confirm disbursement of GH₵ ${parseFloat(disburseAmount).toFixed(2)} to ${recipientName}?`);
    if (!confirmed) return;

    try {
      await api.post(`/groups/${groupId}/disburse`, {
        group_uid: String(groupId),
        to_user_uid: disburseRecipient,
        amount: parseFloat(disburseAmount),
        description: disburseDescription || 'Disbursement',
      });
      toast.success('Disbursement successful');
      setDisburseOpen(false);
      setDisburseAmount('');
      setDisburseRecipient('');
      setDisburseDescription('');
      // Refresh both group and transactions so the ledger shows the new disbursement
      fetchGroupData();
    } catch (error) {
      console.error('Disburse error', error);
      toast.error(error.response?.data?.detail || 'Disbursement failed');
    }
  };

>>>>>>> 17c6933 (initial update)
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
            
            <Dialog open={contributeOpen} onOpenChange={setContributeOpen}>
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
<<<<<<< HEAD
=======
            <div className="mt-4 space-y-2">
              {(group.members || []).map((m) => (
                <div key={m.uid} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="font-semibold">{m.name}</div>
                    {m.is_admin && <div className="text-xs px-2 py-1 bg-emerald-100 text-emerald-800 rounded-full">Admin</div>}
                  </div>
                  {isCurrentUserAdmin() && m.user_uid !== user.uid && (
                    <button onClick={() => handleRemoveMember(m)} className="text-sm text-red-600">Remove</button>
                  )}
                </div>
              ))}
            </div>
            {isCurrentUserAdmin() && (
              <div className="mt-4">
                <Dialog open={disburseOpen} onOpenChange={setDisburseOpen}>
                  <DialogTrigger asChild>
                    <Button className="bg-emerald-900 text-white">Disburse Funds</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Disburse Funds</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleDisburse} className="space-y-4">
                      <div>
                        <Label htmlFor="recipient">Recipient</Label>
                        <select id="recipient" value={disburseRecipient} onChange={(e) => setDisburseRecipient(e.target.value)} className="w-full p-2 border rounded">
                          <option value="">-- Select recipient --</option>
                          {(group.members || []).map((m) => (
                            <option key={m.user_uid} value={m.user_uid}>{m.name} {m.is_admin ? '(Admin)' : ''}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <Label htmlFor="amount">Amount (GH₵)</Label>
                        <Input id="amount" type="number" step="0.01" value={disburseAmount} onChange={(e) => setDisburseAmount(e.target.value)} required />
                      </div>
                      <div>
                        <Label htmlFor="desc">Description</Label>
                        <Input id="desc" type="text" value={disburseDescription} onChange={(e) => setDisburseDescription(e.target.value)} />
                      </div>
                      <div className="flex space-x-2">
                        <Button type="submit" className="bg-emerald-900 text-white">Send</Button>
                        <Button type="button" onClick={() => setDisburseOpen(false)} className="bg-stone-200">Cancel</Button>
                      </div>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            )}
>>>>>>> 17c6933 (initial update)
          </Card>

          <Card className="bg-white p-8 rounded-2xl border border-stone-200 shadow-sm">
            <p className="text-slate-600 text-sm mb-2">CONTRIBUTION</p>
            <h2 className="font-chivo text-3xl font-bold text-emerald-950">GH₵ {group.contribution_amount.toFixed(2)}</h2>
            <p className="text-slate-500 text-sm mt-1">{group.contribution_frequency}</p>
          </Card>
        </div>

<<<<<<< HEAD
=======
        {/* Policies / Rules */}
        <Card className="bg-white p-6 rounded-2xl border border-stone-200 shadow-sm mb-8">
          <div className="flex justify-between items-center mb-4">
            <p className="text-slate-600 text-sm">GROUP POLICIES</p>
            {isCurrentUserAdmin() && (
              <button onClick={() => setPoliciesOpen(true)} className="text-sm text-emerald-900">Edit Policies</button>
            )}
          </div>
          <div className="text-sm text-slate-700 whitespace-pre-wrap">{group.policies || 'No policies set.'}</div>

          <Dialog open={policiesOpen} onOpenChange={setPoliciesOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Edit Group Policies</DialogTitle>
              </DialogHeader>
              <form onSubmit={handlePoliciesSave} className="space-y-4">
                <textarea value={policiesText} onChange={(e) => setPoliciesText(e.target.value)} className="w-full h-40 p-3 border rounded" />
                <div className="flex space-x-2">
                  <Button type="submit" className="bg-emerald-900 text-white">Save</Button>
                  <Button type="button" onClick={() => setPoliciesOpen(false)} className="bg-stone-200">Cancel</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </Card>

>>>>>>> 17c6933 (initial update)
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