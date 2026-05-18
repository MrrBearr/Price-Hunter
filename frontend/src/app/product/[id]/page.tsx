'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { productsAPI, offersAPI, favoritesAPI, alertsAPI } from '@/lib/api';
import { Product, Offer, PriceHistory } from '@/types';
import { useAuthStore } from '@/store/authStore';
import PriceChart from '@/components/PriceChart';
import OfferCard from '@/components/OfferCard';
import { Heart, Bell, Star, Loader2, ExternalLink, ShoppingBag } from 'lucide-react';

export default function ProductPage() {
  const { id } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [history, setHistory] = useState<PriceHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('score');
  const [alertPrice, setAlertPrice] = useState('');
  const [showAlertForm, setShowAlertForm] = useState(false);
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (id) {
      fetchProduct();
      fetchOffers();
      fetchHistory();
    }
  }, [id]);

  useEffect(() => {
    if (id) fetchOffers();
  }, [sortBy]);

  const fetchProduct = async () => {
    try {
      const response = await productsAPI.getById(id as string);
      setProduct(response.data);
    } catch (error) {
      console.error('Failed to fetch product:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOffers = async () => {
    try {
      const response = await offersAPI.getByProduct(id as string, sortBy);
      setOffers(response.data);
    } catch (error) {
      console.error('Failed to fetch offers:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await productsAPI.getHistory(id as string, 30);
      setHistory(response.data);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const addToFavorites = async () => {
    if (!isAuthenticated) return;
    try {
      await favoritesAPI.add(id as string);
      alert('Adicionado aos favoritos!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao adicionar favorito');
    }
  };

  const createAlert = async () => {
    if (!isAuthenticated || !alertPrice) return;
    try {
      await alertsAPI.create({ product_id: id as string, target_price: parseFloat(alertPrice) });
      alert('Alerta criado com sucesso!');
      setShowAlertForm(false);
      setAlertPrice('');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao criar alerta');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
      </div>
    );
  }

  if (!product) {
    return <div className="text-center py-20 text-gray-400">Produto nao encontrado</div>;
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Product Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        {/* Image */}
        <div className="bg-dark-800 rounded-xl p-8 flex items-center justify-center border border-dark-700">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} className="max-h-64 object-contain" />
          ) : (
            <ShoppingBag className="w-24 h-24 text-dark-500" />
          )}
        </div>

        {/* Info */}
        <div className="md:col-span-2">
          <h1 className="text-2xl font-bold mb-4">{product.name}</h1>

          {(product.brand || product.category) && (
            <div className="flex gap-2 mb-4">
              {product.brand && <span className="px-3 py-1 bg-dark-700 rounded-full text-sm text-gray-300">{product.brand}</span>}
              {product.category && <span className="px-3 py-1 bg-dark-700 rounded-full text-sm text-gray-300">{product.category}</span>}
            </div>
          )}

          {/* Price Range */}
          <div className="bg-dark-800 rounded-xl p-6 border border-dark-700 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Menor preco encontrado</p>
                <p className="text-3xl font-bold text-green-400">
                  R$ {product.min_price ? product.min_price.toFixed(2).replace('.', ',') : '--'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">{product.offers_count} ofertas</p>
                {product.max_price && product.min_price && product.max_price > product.min_price && (
                  <p className="text-sm text-gray-300">
                    ate R$ {product.max_price.toFixed(2).replace('.', ',')}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Actions */}
          {isAuthenticated && (
            <div className="flex gap-3">
              <button
                onClick={addToFavorites}
                className="flex items-center gap-2 px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg hover:border-red-500 hover:text-red-400 transition-colors"
              >
                <Heart className="w-4 h-4" /> Favoritar
              </button>
              <button
                onClick={() => setShowAlertForm(!showAlertForm)}
                className="flex items-center gap-2 px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg hover:border-yellow-500 hover:text-yellow-400 transition-colors"
              >
                <Bell className="w-4 h-4" /> Criar Alerta
              </button>
            </div>
          )}

          {/* Alert Form */}
          {showAlertForm && (
            <div className="mt-4 p-4 bg-dark-800 border border-dark-700 rounded-lg">
              <p className="text-sm text-gray-300 mb-2">Receba um alerta quando o preco atingir:</p>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={alertPrice}
                  onChange={(e) => setAlertPrice(e.target.value)}
                  placeholder="R$ 0,00"
                  className="flex-1 px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-sm outline-none focus:border-primary-500"
                />
                <button onClick={createAlert} className="px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-sm transition-colors">
                  Criar
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Price History Chart */}
      {history.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4">Historico de Precos (30 dias)</h2>
          <div className="bg-dark-800 rounded-xl p-6 border border-dark-700">
            <PriceChart data={history} />
          </div>
        </div>
      )}

      {/* Offers */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Ofertas Disponíveis</h2>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-sm outline-none focus:border-primary-500"
          >
            <option value="score">Melhor Score</option>
            <option value="price">Menor Preco</option>
            <option value="shipping">Menor Frete</option>
          </select>
        </div>

        <div className="space-y-4">
          {offers.map((offer) => (
            <OfferCard key={offer.id} offer={offer} />
          ))}
          {offers.length === 0 && (
            <p className="text-center py-8 text-gray-400">Nenhuma oferta disponivel</p>
          )}
        </div>
      </div>
    </div>
  );
}
