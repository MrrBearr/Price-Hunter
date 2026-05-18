'use client';

import Link from 'next/link';
import { Product } from '@/types';
import { ShoppingBag, TrendingDown } from 'lucide-react';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const discount = product.max_price && product.min_price
    ? Math.round(((product.max_price - product.min_price) / product.max_price) * 100)
    : 0;

  return (
    <Link href={`/product/${product.id}`}>
      <div className="bg-dark-800 border border-dark-700 rounded-xl overflow-hidden hover:border-primary-500/50 hover:shadow-lg hover:shadow-primary-500/10 transition-all group cursor-pointer">
        {/* Image */}
        <div className="relative h-48 bg-dark-700 flex items-center justify-center overflow-hidden">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform"
            />
          ) : (
            <ShoppingBag className="w-16 h-16 text-dark-500" />
          )}
          {discount > 10 && (
            <span className="absolute top-2 right-2 px-2 py-1 bg-green-500/90 text-white text-xs font-bold rounded-md">
              -{discount}%
            </span>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-200 line-clamp-2 mb-3 min-h-[40px]">
            {product.name}
          </h3>

          {/* Price */}
          <div className="flex items-end justify-between">
            <div>
              {product.min_price ? (
                <>
                  <p className="text-xs text-gray-400">A partir de</p>
                  <p className="text-xl font-bold text-green-400">
                    R$ {product.min_price.toFixed(2).replace('.', ',')}
                  </p>
                </>
              ) : (
                <p className="text-sm text-gray-400">Preco indisponivel</p>
              )}
            </div>
            <div className="text-right">
              <span className="text-xs text-gray-400">
                {product.offers_count} {product.offers_count === 1 ? 'oferta' : 'ofertas'}
              </span>
            </div>
          </div>

          {/* Category & Brand */}
          {(product.category || product.brand) && (
            <div className="flex items-center gap-2 mt-3">
              {product.brand && (
                <span className="px-2 py-0.5 bg-dark-700 text-gray-400 text-xs rounded">
                  {product.brand}
                </span>
              )}
              {product.category && (
                <span className="px-2 py-0.5 bg-dark-700 text-gray-400 text-xs rounded">
                  {product.category}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
