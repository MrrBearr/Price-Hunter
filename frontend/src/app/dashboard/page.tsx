'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { alertsAPI, favoritesAPI, couponsAPI } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import { Alert, Favorite, Coupon } from '@/types';
import { Bell, Heart, Tag, Trash2, Loader2, TrendingDown, CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('alerts');
  const { isAuthenticated, user, loadUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    loadUser();
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchData = async () => {
    try {
      const [alertsRes, favsRes, couponsRes] = await Promise.all([
        alertsAPI.getAll(),
        favoritesAPI.getAll(),
        couponsAPI.getAll({ active_only: true }),
      ]);
      setAlerts(alertsRes.data);
      setFavorites(favsRes.data);
      setCoupons(couponsRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteAlert = async (alertId: string) => {
    try {
      await alertsAPI.delete(alertId);
      setAlerts(alerts.filter((a) => a.id !== alertId));
    } catch (error) {
      console.error('Failed to delete alert:', error);
    }
  };

  const testCoupon = async (couponId: string) => {
    try {
      await couponsAPI.test(couponId);
      alert('Teste de cupom enfileirado!');
    } catch (error) {
      console.error('Failed to test coupon:', error);
    }
  };

  if (!isAuthenticated && !loading) {
    return (
      <div className="text-center py-20">
        <p className="text-xl text-gray-400 mb-4">Faca login para acessar o dashboard</p>
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
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-400">Bem-vindo, {user?.full_name || user?.username}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="p-6 bg-dark-800 border border-dark-700 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Alertas Ativos</p>
              <p className="text-2xl font-bold">{alerts.filter((a) => a.is_active).length}</p>
            </div>
            <Bell className="w-8 h-8 text-yellow-400" />
          </div>
        </div>
        <div className="p-6 bg-dark-800 border border-dark-700 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Favoritos</p>
              <p className="text-2xl font-bold">{favorites.length}</p>
            </div>
            <Heart className="w-8 h-8 text-red-400" />
          </div>
        </div>
        <div className="p-6 bg-dark-800 border border-dark-700 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Cupons Disponiveis</p>
              <p className="text-2xl font-bold">{coupons.length}</p>
            </div>
            <Tag className="w-8 h-8 text-green-400" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-dark-800 border border-dark-700 rounded-lg p-1 mb-6">
        {[
          { id: 'alerts', label: 'Alertas', icon: Bell },
          { id: 'coupons', label: 'Cupons', icon: Tag },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Icon className="w-4 h-4" /> {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'alerts' && (
        <div className="space-y-4">
          {alerts.length === 0 ? (
            <p className="text-center py-8 text-gray-400">Nenhum alerta de preco criado</p>
          ) : (
            alerts.map((alert) => (
              <div key={alert.id} className="flex items-center gap-4 p-4 bg-dark-800 border border-dark-700 rounded-xl">
                <div className={`p-2 rounded-lg ${alert.triggered ? 'bg-green-500/20' : 'bg-yellow-500/20'}`}>
                  {alert.triggered ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <Bell className="w-5 h-5 text-yellow-400" />
                  )}
                </div>
                <div className="flex-1">
                  <Link href={`/product/${alert.product_id}`} className="font-medium hover:text-primary-400">
                    {alert.product_name || 'Produto'}
                  </Link>
                  <div className="flex items-center gap-4 text-sm text-gray-400 mt-1">
                    <span>Meta: R$ {alert.target_price.toFixed(2).replace('.', ',')}</span>
                    {alert.current_price && (
                      <span>Atual: R$ {alert.current_price.toFixed(2).replace('.', ',')}</span>
                    )}
                    {alert.triggered && <span className="text-green-400">Atingido!</span>}
                  </div>
                </div>
                <button onClick={() => deleteAlert(alert.id)} className="p-2 text-gray-400 hover:text-red-400">
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'coupons' && (
        <div className="space-y-4">
          {coupons.length === 0 ? (
            <p className="text-center py-8 text-gray-400">Nenhum cupom disponivel</p>
          ) : (
            coupons.map((coupon) => (
              <div key={coupon.id} className="flex items-center gap-4 p-4 bg-dark-800 border border-dark-700 rounded-xl">
                <div className="p-2 bg-green-500/20 rounded-lg">
                  <Tag className="w-5 h-5 text-green-400" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-green-400 bg-green-500/10 px-2 py-0.5 rounded">
                      {coupon.code}
                    </span>
                    <span className="text-sm text-gray-400">{coupon.store_name}</span>
                  </div>
                  <p className="text-sm text-gray-400 mt-1">
                    {coupon.discount_type === 'percentage' && `${coupon.discount_value}% de desconto`}
                    {coupon.discount_type === 'fixed' && `R$ ${coupon.discount_value.toFixed(2)} de desconto`}
                    {coupon.discount_type === 'shipping' && 'Frete gratis'}
                    {coupon.description && ` - ${coupon.description}`}
                  </p>
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                    <span>Taxa sucesso: {coupon.success_rate.toFixed(0)}%</span>
                    {coupon.minimum_purchase > 0 && (
                      <span>Min: R$ {coupon.minimum_purchase.toFixed(2)}</span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => testCoupon(coupon.id)}
                  className="px-3 py-2 bg-dark-700 border border-dark-600 rounded-lg text-sm hover:border-primary-500 transition-colors"
                >
                  Testar
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
