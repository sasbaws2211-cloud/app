import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-stone-100">
      {/* Header */}
      <header className="container mx-auto px-6 py-6 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-emerald-900 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-xl">S</span>
          </div>
          <span className="font-chivo text-2xl font-bold text-emerald-950">SusuFlow</span>
        </div>
        <div className="flex space-x-4">
          <Link to="/login">
            <Button variant="ghost" className="text-slate-600 hover:text-emerald-900" data-testid="login-link">Login</Button>
          </Link>
          <Link to="/register">
            <Button className="bg-emerald-900 hover:bg-emerald-800 text-white rounded-full px-6" data-testid="register-link">Get Started</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <h1 className="font-chivo text-5xl md:text-6xl font-bold text-emerald-950 leading-tight">
              Digital Group Savings Made Simple
            </h1>
            <p className="text-xl text-slate-600 leading-relaxed">
              Manage your susu, credit union, or cooperative contributions with complete transparency and mobile money integration.
            </p>
            <div className="flex space-x-4">
              <Link to="/register">
                <Button className="bg-emerald-900 hover:bg-emerald-800 text-white rounded-full px-8 py-6 text-lg shadow-xl hover:shadow-2xl transition-all duration-300" data-testid="hero-get-started">
                  Start Saving Together
                </Button>
              </Link>
            </div>
          </div>
          <div className="relative">
            <img 
              src="https://images.unsplash.com/photo-1548782033-3ac3a62ece8d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwxfHxXZXN0JTIwQWZyaWNhbiUyMGNvbW11bml0eSUyMG1lZXRpbmclMjBoYXBweSUyMGdyb3VwfGVufDB8fHx8MTc2ODcwMzg5Mnww&ixlib=rb-4.1.0&q=85" 
              alt="Community" 
              className="rounded-2xl shadow-2xl"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="font-chivo text-4xl font-bold text-emerald-950 mb-4">Built for West African Communities</h2>
          <p className="text-lg text-slate-600">Everything you need for transparent group financial management</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-stone-200">
            <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-emerald-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="font-chivo text-2xl font-bold text-emerald-950 mb-3">Personal & Group Wallets</h3>
            <p className="text-slate-600 leading-relaxed">Manage your personal savings and contribute to multiple groups seamlessly</p>
          </div>
          
          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-stone-200">
            <div className="w-12 h-12 bg-sky-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="font-chivo text-2xl font-bold text-emerald-950 mb-3">Mobile Money Integration</h3>
            <p className="text-slate-600 leading-relaxed">Deposit and withdraw using MTN, Vodafone, or AirtelTigo mobile money</p>
          </div>
          
          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all duration-300 border border-stone-200">
            <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-emerald-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="font-chivo text-2xl font-bold text-emerald-950 mb-3">Complete Transparency</h3>
            <p className="text-slate-600 leading-relaxed">Immutable ledger with full transaction history visible to all members</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="bg-emerald-900 rounded-2xl p-12 text-center text-white">
          <h2 className="font-chivo text-4xl font-bold mb-4">Ready to Start?</h2>
          <p className="text-xl mb-8 text-emerald-100">Join thousands managing their group contributions digitally</p>
          <Link to="/register">
            <Button className="bg-white text-emerald-900 hover:bg-emerald-50 rounded-full px-8 py-6 text-lg font-bold shadow-xl" data-testid="cta-get-started">
              Create Your Account
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-8 border-t border-stone-200 mt-20">
        <div className="text-center text-slate-600">
          <p>&copy; 2025 SusuFlow. Built for West African communities.</p>
        </div>
      </footer>
    </div>
  );
}