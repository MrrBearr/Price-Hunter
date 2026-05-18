'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { favoritesAPI } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import { Favorite } from '@/types';
import { Heart, Trash2, Loader2, ShoppingBag } from 'lucide-react';
import Link from 'next/link';

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated, loadUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    loadUser();
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchFavorites = async () => {
    try {
      const response = await favoritesAPI.getAll();
      setFavorites(response.data);
    } catch (error) {
      console.error('Failed to fetch favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (productId: string) => {
    try {
      await favoritesAPI.remove(productId);
      setFavorites(favorites.filter((f) => f.product_id !== productId));
    } catch (error) {
      console.error('Failed to remove favorite:', error);
    }
  };

  if (!isAuthenticated && !loading) {
    return (
      <div className="text-center py-20">
        <Heart className="w-16 h-16 text-gray-500 mx-auto mb-4" />
        <p className="text-xl text-gray-400 mb-4">Faca login para ver seus favoritos</p>
        <Link href="/login" className="px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors">
          Entrar
        </Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Heart className="w-6 h-6 text-red-400" /> Meus Favoritos
      </h1>

      {favorites.length === 0 ? (
        <div className="text-center py-16 bg-dark-800 rounded-xl border border-dark-700">
          <Heart className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400 mb-4">Voce ainda nao tem favoritos</p>
          <Link href="/" className="text-primary-400 hover:text-primary-300">
            Buscar produtos
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {favorites.map((fav) => (
            <div key={fav.id} className="flex items-center gap-4 p-4 bg-dark-800 border border-dark-700 rounded-xl">
              <div className="w-16 h-16 bg-dark-700 rounded-lg flex items-center justify-center">
                {fav.product_image ? (
                  <img src={fav.product_image} alt="" className="w-full h-full object-contain p-1 rounded-lg" />
                ) : (
                  <ShoppingBag className="w-8 h-8 text-dark-500" />
                )}
              </div>
              <div className="flex-1">
                <Link href={`/product/${fav.product_id}`} className="font-medium hover:text-primary-400 transition-colors">
                  {fav.product_name || 'Produto'}
                </Link>
                {fav.min_price && (
                  <p className="text-sm text-green-400">
                    A partir de R$ {fav.min_price.toFixed(2).replace('.', ',')}
                  </p>
                )}
              </div>
              <button
                onClick={() => removeFavorite(fav.product_id)}
                className="p-2 text-gray-400 hover:text-red-400 transition-colors"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
