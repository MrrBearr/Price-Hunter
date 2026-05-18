'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { Mail, Lock, User, Loader2 } from 'lucide-react';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const { register, isLoading } = useAuthStore();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await register(email, username, password, fullName || undefined);
      setSuccess(true);
      setTimeout(() => router.push('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar conta');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16">
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-8">
        <h1 className="text-2xl font-bold mb-2 text-center">Criar Conta</h1>
        <p className="text-gray-400 text-center mb-8">Junte-se ao PriceHunter</p>

        {success && (
          <div className="mb-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm">
            Conta criada com sucesso! Redirecionando...
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-300 mb-1">Nome completo</label>
            <div className="flex items-center bg-dark-700 border border-dark-600 rounded-lg overflow-hidden focus-within:border-primary-500">
              <User className="w-5 h-5 text-gray-400 ml-3" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Seu nome"
                className="flex-1 px-3 py-3 bg-transparent text-white placeholder-gray-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">Username</label>
            <div className="flex items-center bg-dark-700 border border-dark-600 rounded-lg overflow-hidden focus-within:border-primary-500">
              <User className="w-5 h-5 text-gray-400 ml-3" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="username"
                required
                className="flex-1 px-3 py-3 bg-transparent text-white placeholder-gray-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">Email</label>
            <div className="flex items-center bg-dark-700 border border-dark-600 rounded-lg overflow-hidden focus-within:border-primary-500">
              <Mail className="w-5 h-5 text-gray-400 ml-3" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                required
                className="flex-1 px-3 py-3 bg-transparent text-white placeholder-gray-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-300 mb-1">Senha</label>
            <div className="flex items-center bg-dark-700 border border-dark-600 rounded-lg overflow-hidden focus-within:border-primary-500">
              <Lock className="w-5 h-5 text-gray-400 ml-3" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimo 6 caracteres"
                required
                minLength={6}
                className="flex-1 px-3 py-3 bg-transparent text-white placeholder-gray-500 outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-800 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center justify-center"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Criar Conta'}
          </button>
        </form>

        <p className="text-center mt-6 text-gray-400 text-sm">
          Ja tem conta?{' '}
          <Link href="/login" className="text-primary-400 hover:text-primary-300">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
}
