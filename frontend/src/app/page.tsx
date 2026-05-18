'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search, TrendingDown, Shield, Bell, Zap } from 'lucide-react';

export default function Home() {
  const [query, setQuery] = useState('');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <div className="text-center max-w-4xl mx-auto mt-16 mb-16">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          PriceHunter
        </h1>
        <p className="text-xl text-gray-300 mb-10">
          Compare precos em multiplas lojas, encontre cupons automaticamente e economize em cada compra.
        </p>

        {/* Search Box */}
        <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
          <div className="flex items-center bg-dark-800 border border-dark-600 rounded-xl overflow-hidden shadow-2xl focus-within:border-primary-500 transition-all">
            <Search className="w-6 h-6 text-gray-400 ml-4" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar produto... (ex: iPhone 15, Galaxy S24, PlayStation 5)"
              className="flex-1 px-4 py-5 bg-transparent text-white placeholder-gray-400 outline-none text-lg"
            />
            <button
              type="submit"
              className="px-8 py-5 bg-primary-600 hover:bg-primary-700 text-white font-semibold transition-colors"
            >
              Buscar
            </button>
          </div>
        </form>

        {/* Quick search tags */}
        <div className="flex flex-wrap justify-center gap-2 mt-6">
          {['iPhone 15', 'Galaxy S24', 'PlayStation 5', 'AirPods Pro', 'Notebook Gamer'].map((tag) => (
            <button
              key={tag}
              onClick={() => { setQuery(tag); router.push(`/search?q=${encodeURIComponent(tag)}`); }}
              className="px-4 py-2 bg-dark-800 border border-dark-600 rounded-full text-sm text-gray-300 hover:border-primary-500 hover:text-primary-400 transition-all"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto mb-16">
        <FeatureCard
          icon={<TrendingDown className="w-8 h-8 text-green-400" />}
          title="Menor Preco"
          description="Compare precos em Amazon, Mercado Livre, Shopee e mais"
        />
        <FeatureCard
          icon={<Shield className="w-8 h-8 text-blue-400" />}
          title="Cupons Testados"
          description="Cupons verificados automaticamente com taxa de sucesso"
        />
        <FeatureCard
          icon={<Bell className="w-8 h-8 text-yellow-400" />}
          title="Alertas de Preco"
          description="Receba notificacao quando o preco cair"
        />
        <FeatureCard
          icon={<Zap className="w-8 h-8 text-purple-400" />}
          title="Score de Oferta"
          description="Algoritmo inteligente que avalia a melhor compra"
        />
      </div>

      {/* How it works */}
      <div className="max-w-4xl mx-auto text-center mb-16">
        <h2 className="text-3xl font-bold mb-8">Como Funciona</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <StepCard number={1} title="Busque" description="Digite o produto que deseja comprar" />
          <StepCard number={2} title="Compare" description="Veja precos de multiplas lojas lado a lado" />
          <StepCard number={3} title="Economize" description="Aplique cupons e compre pelo menor preco" />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="p-6 bg-dark-800 border border-dark-700 rounded-xl hover:border-primary-500/50 transition-all group">
      <div className="mb-4 group-hover:scale-110 transition-transform">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
  );
}

function StepCard({ number, title, description }: { number: number; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}
