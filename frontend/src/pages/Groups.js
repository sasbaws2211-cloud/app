import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';

export default function Groups() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createLoading, setCreateLoading] = useState(false);
  const [joinCode, setJoinCode] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [joinOpen, setJoinOpen] = useState(false);
  
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    contribution_amount: 0,
    contribution_frequency: 'monthly'
  });

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await api.get('/groups');
      setGroups(response.data);
    } catch (error) {
      toast.error('Failed to load groups');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    setCreateLoading(true);

    try {
      await api.post('/groups', newGroup);
      toast.success('Group created successfully!');
      setNewGroup({ name: '', description: '', contribution_amount: 0, contribution_frequency: 'monthly' });
      setCreateOpen(false);
      fetchGroups();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create group');
    } finally {
      setCreateLoading(false);
    }
  };

  const handleJoinGroup = async (e) => {
    e.preventDefault();

    try {
      await api.post(`/groups/join/${joinCode}`);
      toast.success('Successfully joined group!');
      setJoinCode('');
      setJoinOpen(false);
      fetchGroups();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to join group');
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
    <div className="min-h-screen bg-stone-50" data-testid="groups-page">
      <Navbar />
      
      <div className="container mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="font-chivo text-4xl font-bold text-emerald-950">My Groups</h1>
          
          <div className="flex space-x-4">
            <Dialog open={joinOpen} onOpenChange={setJoinOpen}>
              <DialogTrigger asChild>
                <Button className="bg-emerald-700 hover:bg-emerald-600 text-white rounded-full" data-testid="join-group-button">
                  Join Group
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Join a Group</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleJoinGroup} className="space-y-4" data-testid="join-group-form">
                  <div className="space-y-2">
                    <Label htmlFor="invite-code">Invite Code</Label>
                    <Input
                      id="invite-code"
                      placeholder="Enter invite code"
                      value={joinCode}
                      onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                      required
                      data-testid="invite-code-input"
                    />
                  </div>
                  <Button type="submit" className="w-full bg-emerald-900 hover:bg-emerald-800 rounded-full" data-testid="join-group-submit">
                    Join Group
                  </Button>
                </form>
              </DialogContent>
            </Dialog>

            <Dialog open={createOpen} onOpenChange={setCreateOpen}>
              <DialogTrigger asChild>
                <Button className="bg-emerald-900 hover:bg-emerald-800 text-white rounded-full" data-testid="create-group-button">
                  Create Group
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Group</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreateGroup} className="space-y-4" data-testid="create-group-form">
                  <div className="space-y-2">
                    <Label htmlFor="group-name">Group Name</Label>
                    <Input
                      id="group-name"
                      placeholder="e.g., Family Savings"
                      value={newGroup.name}
                      onChange={(e) => setNewGroup({ ...newGroup, name: e.target.value })}
                      required
                      data-testid="group-name-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="group-description">Description</Label>
                    <Input
                      id="group-description"
                      placeholder="What's this group for?"
                      value={newGroup.description}
                      onChange={(e) => setNewGroup({ ...newGroup, description: e.target.value })}
                      data-testid="group-description-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="contribution-amount">Monthly Contribution (GH₵)</Label>
                    <Input
                      id="contribution-amount"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={newGroup.contribution_amount}
                      onChange={(e) => setNewGroup({ ...newGroup, contribution_amount: parseFloat(e.target.value) })}
                      data-testid="contribution-amount-input"
                    />
                  </div>
                  <Button 
                    type="submit" 
                    className="w-full bg-emerald-900 hover:bg-emerald-800 rounded-full"
                    disabled={createLoading}
                    data-testid="create-group-submit"
                  >
                    {createLoading ? 'Creating...' : 'Create Group'}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {groups.length === 0 ? (
          <Card className="bg-white rounded-2xl border border-stone-200 shadow-sm p-12 text-center">
            <p className="text-slate-500 text-lg mb-6">You're not in any groups yet</p>
            <p className="text-slate-400 mb-8">Create a new group or join an existing one to get started</p>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="groups-list">
            {groups.map((group) => (
              <Link 
<<<<<<< HEAD
                key={group.id} 
                to={`/groups/${group.id}`}
                data-testid={`group-card-${group.id}`}
=======
                key={group.uid} 
                to={`/groups/${group.uid}`}
                data-testid={`group-card-${group.uid}`}
>>>>>>> 17c6933 (initial update)
              >
                <Card className="bg-white rounded-2xl border border-stone-200 shadow-sm hover:shadow-lg transition-all duration-300 p-6 h-full">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-chivo text-xl font-bold text-emerald-950 mb-1">{group.name}</h3>
                      <p className="text-sm text-slate-500">{group.member_count} members</p>
                    </div>
                    <span className="text-xs bg-emerald-100 text-emerald-900 px-3 py-1 rounded-full">
                      {group.invite_code}
                    </span>
                  </div>
                  
                  {group.description && (
                    <p className="text-slate-600 text-sm mb-4 line-clamp-2">{group.description}</p>
                  )}
                  
                  <div className="border-t border-stone-100 pt-4 mt-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="text-xs text-slate-500">Group Balance</p>
                        <p className="font-chivo text-2xl font-bold text-emerald-900">GH₵ {group.wallet_balance?.toFixed(2) || '0.00'}</p>
                      </div>
                      {group.contribution_amount > 0 && (
                        <div className="text-right">
                          <p className="text-xs text-slate-500">Monthly</p>
                          <p className="font-semibold text-emerald-950">GH₵ {group.contribution_amount.toFixed(2)}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}