'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { searchAPI } from '@/lib/api';
import { Product } from '@/types';
import ProductCard from '@/components/ProductCard';
import { Filter, SortAsc, Loader2 } from 'lucide-react';

export default function SearchPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('relevance');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [triggered, setTriggered] = useState(false);

  useEffect(() => {
    if (query) {
      fetchResults();
    }
  }, [query, sortBy]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const params: any = { q: query, sort_by: sortBy };
      if (minPrice) params.min_price = parseFloat(minPrice);
      if (maxPrice) params.max_price = parseFloat(maxPrice);

      const response = await searchAPI.search(params);
      setProducts(response.data);

      // If no results, trigger scraping
      if (response.data.length === 0 && !triggered) {
        setTriggered(true);
        await searchAPI.trigger(query);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Search Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">
          Resultados para &ldquo;{query}&rdquo;
        </h1>
        <p className="text-gray-400">
          {loading ? 'Buscando...' : `${products.length} produtos encontrados`}
        </p>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center gap-4 mb-6 p-4 bg-dark-800 rounded-xl border border-dark-700">
        <Filter className="w-5 h-5 text-gray-400" />

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-sm outline-none focus:border-primary-500"
        >
          <option value="relevance">Relevancia</option>
          <option value="price_asc">Menor Preco</option>
          <option value="price_desc">Maior Preco</option>
          <option value="name">Nome</option>
        </select>

        <input
          type="number"
          placeholder="Preco min"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
          className="w-28 px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-sm outline-none focus:border-primary-500"
        />
        <input
          type="number"
          placeholder="Preco max"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          className="w-28 px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-sm outline-none focus:border-primary-500"
        />

        <button
          onClick={fetchResults}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-sm transition-colors"
        >
          Filtrar
        </button>
      </div>

      {/* Results */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
          <p className="text-gray-400">Buscando melhores precos...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-xl text-gray-400 mb-4">Nenhum resultado encontrado</p>
          {triggered && (
            <p className="text-sm text-gray-500">
              Estamos buscando nas lojas. Tente novamente em alguns instantes.
            </p>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
