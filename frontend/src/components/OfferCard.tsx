'use client';

import { Offer } from '@/types';
import { ExternalLink, Star, Truck, Award } from 'lucide-react';

interface OfferCardProps {
  offer: Offer;
}

export default function OfferCard({ offer }: OfferCardProps) {
  const totalPrice = offer.price + offer.shipping_cost;
  const discount = offer.original_price
    ? Math.round(((offer.original_price - offer.price) / offer.original_price) * 100)
    : 0;

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-400 border-green-500/30 bg-green-500/10';
    if (score >= 6) return 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10';
    return 'text-red-400 border-red-500/30 bg-red-500/10';
  };

  const getStoreColor = (slug?: string) => {
    switch (slug) {
      case 'amazon': return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
      case 'mercadolivre': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'shopee': return 'bg-red-500/20 text-red-300 border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  return (
    <div className="flex flex-col md:flex-row items-stretch md:items-center gap-4 p-4 bg-dark-800 border border-dark-700 rounded-xl hover:border-dark-600 transition-all">
      {/* Store Badge */}
      <div className="flex items-center gap-3 min-w-[140px]">
        <span className={`px-3 py-1 text-xs font-medium rounded-full border ${getStoreColor(offer.store_slug)}`}>
          {offer.store_name || offer.store_slug}
        </span>
      </div>

      {/* Seller Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-300 truncate">
          {offer.seller_name && <span>Vendido por: {offer.seller_name}</span>}
        </p>
        <div className="flex items-center gap-2 mt-1">
          {offer.seller_rating && (
            <span className="flex items-center text-xs text-yellow-400">
              <Star className="w-3 h-3 mr-1 fill-yellow-400" />
              {offer.seller_rating.toFixed(1)}
            </span>
          )}
          {offer.shipping_time && (
            <span className="flex items-center text-xs text-gray-400">
              <Truck className="w-3 h-3 mr-1" />
              {offer.shipping_time}
            </span>
          )}
        </div>
      </div>

      {/* Price */}
      <div className="text-right min-w-[150px]">
        {offer.original_price && offer.original_price > offer.price && (
          <p className="text-xs text-gray-500 line-through">
            R$ {offer.original_price.toFixed(2).replace('.', ',')}
          </p>
        )}
        <p className="text-xl font-bold text-green-400">
          R$ {offer.price.toFixed(2).replace('.', ',')}
        </p>
        <p className="text-xs text-gray-400">
          {offer.shipping_cost === 0
            ? <span className="text-green-400">Frete Gratis</span>
            : `+ R$ ${offer.shipping_cost.toFixed(2).replace('.', ',')} frete`}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Total: R$ {totalPrice.toFixed(2).replace('.', ',')}
        </p>
      </div>

      {/* Score */}
      <div className={`flex items-center justify-center w-14 h-14 rounded-xl border ${getScoreColor(offer.score)}`}>
        <div className="text-center">
          <p className="text-lg font-bold">{offer.score.toFixed(1)}</p>
        </div>
      </div>

      {/* Action */}
      <a
        href={offer.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
      >
        <ExternalLink className="w-4 h-4" />
        Ver Oferta
      </a>
    </div>
  );
}
