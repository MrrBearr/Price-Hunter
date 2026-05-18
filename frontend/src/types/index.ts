export interface Product {
  id: string;
  name: string;
  slug?: string;
  description?: string;
  category?: string;
  brand?: string;
  image_url?: string;
  min_price?: number;
  max_price?: number;
  offers_count: number;
  created_at: string;
}

export interface Offer {
  id: string;
  product_id: string;
  store_id: string;
  price: number;
  original_price?: number;
  shipping_cost: number;
  shipping_time?: string;
  url: string;
  seller_name?: string;
  seller_rating?: number;
  is_available: boolean;
  score: number;
  store_name?: string;
  store_slug?: string;
  last_checked: string;
  created_at: string;
}

export interface Coupon {
  id: string;
  store_id: string;
  code: string;
  description?: string;
  discount_type: 'percentage' | 'fixed' | 'shipping';
  discount_value: number;
  minimum_purchase: number;
  success_rate: number;
  is_active: boolean;
  expires_at?: string;
  store_name?: string;
  created_at: string;
}

export interface Alert {
  id: string;
  user_id: string;
  product_id: string;
  target_price: number;
  is_active: boolean;
  triggered: boolean;
  triggered_at?: string;
  product_name?: string;
  current_price?: number;
  created_at: string;
}

export interface Favorite {
  id: string;
  user_id: string;
  product_id: string;
  product_name?: string;
  product_image?: string;
  min_price?: number;
  created_at: string;
}

export interface PriceHistory {
  id: string;
  offer_id: string;
  product_id: string;
  store_id: string;
  price: number;
  shipping_cost: number;
  store_name?: string;
  recorded_at: string;
}
