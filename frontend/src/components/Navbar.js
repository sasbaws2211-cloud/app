import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white border-b border-stone-200 sticky top-0 z-50" data-testid="navbar">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <Link to="/dashboard" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-emerald-900 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <span className="font-chivo text-2xl font-bold text-emerald-950">SusuFlow</span>
          </Link>

          <div className="flex items-center space-x-6">
            <Link 
              to="/dashboard" 
              className={`text-sm font-medium transition-colors hover:text-emerald-900 ${
                isActive('/dashboard') ? 'text-emerald-900' : 'text-slate-600'
              }`}
              data-testid="nav-dashboard"
            >
              Dashboard
            </Link>
            <Link 
              to="/wallet" 
              className={`text-sm font-medium transition-colors hover:text-emerald-900 ${
                isActive('/wallet') ? 'text-emerald-900' : 'text-slate-600'
              }`}
              data-testid="nav-wallet"
            >
              Wallet
            </Link>
            <Link 
              to="/groups" 
              className={`text-sm font-medium transition-colors hover:text-emerald-900 ${
                isActive('/groups') ? 'text-emerald-900' : 'text-slate-600'
              }`}
              data-testid="nav-groups"
            >
              Groups
            </Link>

            <div className="flex items-center space-x-4 ml-4 pl-4 border-l border-stone-200">
              <span className="text-sm text-slate-600">{user?.name}</span>
              <Button 
                onClick={logout} 
                variant="outline" 
                className="rounded-full"
                data-testid="logout-button"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}