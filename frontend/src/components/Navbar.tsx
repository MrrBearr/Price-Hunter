'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Search, User, Heart, Bell, Menu, X, LogOut } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export default function Navbar() {
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const router = useRouter();
  const { isAuthenticated, user, logout, loadUser } = useAuthStore();

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  return (
    <nav className="sticky top-0 z-50 bg-dark-900/95 backdrop-blur border-b border-dark-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              PriceHunter
            </span>
          </Link>

          {/* Search Bar - Desktop */}
          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-lg mx-8">
            <div className="flex items-center w-full bg-dark-800 border border-dark-600 rounded-lg overflow-hidden focus-within:border-primary-500">
              <Search className="w-4 h-4 text-gray-400 ml-3" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar produtos..."
                className="flex-1 px-3 py-2 bg-transparent text-white placeholder-gray-400 outline-none text-sm"
              />
            </div>
          </form>

          {/* Actions - Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link href="/favorites" className="p-2 text-gray-300 hover:text-primary-400 transition-colors">
                  <Heart className="w-5 h-5" />
                </Link>
                <Link href="/dashboard" className="p-2 text-gray-300 hover:text-primary-400 transition-colors">
                  <Bell className="w-5 h-5" />
                </Link>
                <Link href="/dashboard" className="flex items-center space-x-2 px-3 py-2 bg-dark-800 rounded-lg text-sm">
                  <User className="w-4 h-4" />
                  <span>{user?.username}</span>
                </Link>
                <button
                  onClick={logout}
                  className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-4 py-2 text-sm text-gray-300 hover:text-white transition-colors"
                >
                  Entrar
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded-lg transition-colors"
                >
                  Cadastrar
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-gray-300"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-dark-700">
            <form onSubmit={handleSearch} className="mb-4">
              <div className="flex items-center bg-dark-800 border border-dark-600 rounded-lg overflow-hidden">
                <Search className="w-4 h-4 text-gray-400 ml-3" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Buscar produtos..."
                  className="flex-1 px-3 py-2 bg-transparent text-white placeholder-gray-400 outline-none text-sm"
                />
              </div>
            </form>
            <div className="space-y-2">
              {isAuthenticated ? (
                <>
                  <Link href="/dashboard" className="block px-3 py-2 text-gray-300 hover:text-white">Dashboard</Link>
                  <Link href="/favorites" className="block px-3 py-2 text-gray-300 hover:text-white">Favoritos</Link>
                  <button onClick={logout} className="block px-3 py-2 text-red-400">Sair</button>
                </>
              ) : (
                <>
                  <Link href="/login" className="block px-3 py-2 text-gray-300 hover:text-white">Entrar</Link>
                  <Link href="/register" className="block px-3 py-2 text-primary-400">Cadastrar</Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
