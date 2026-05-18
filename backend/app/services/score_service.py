from decimal import Decimal
from typing import Optional


class ScoreService:
    """
    Calculates offer score based on multiple factors:
    - Price weight: 40%
    - Shipping cost weight: 20%
    - Seller rating weight: 15%
    - Store reputation weight: 15%
    - Discount weight: 10%
    """

    PRICE_WEIGHT = 0.40
    SHIPPING_WEIGHT = 0.20
    SELLER_RATING_WEIGHT = 0.15
    STORE_REPUTATION_WEIGHT = 0.15
    DISCOUNT_WEIGHT = 0.10

    @staticmethod
    def calculate_score(
        price: float,
        min_price: float,
        max_price: float,
        shipping_cost: float = 0.0,
        max_shipping: float = 50.0,
        seller_rating: Optional[float] = None,
        store_reputation: float = 0.5,
        original_price: Optional[float] = None,
        coupon_discount: float = 0.0,
    ) -> float:
        """Calculate a score from 0 to 10 for an offer."""

        # Price score (lower is better)
        if max_price > min_price:
            price_score = 1 - ((price - min_price) / (max_price - min_price))
        else:
            price_score = 1.0

        # Shipping score (lower is better)
        if max_shipping > 0:
            shipping_score = max(0, 1 - (shipping_cost / max_shipping))
        else:
            shipping_score = 1.0

        # Seller rating score
        if seller_rating is not None:
            rating_score = seller_rating / 5.0
        else:
            rating_score = 0.5

        # Store reputation
        reputation_score = float(store_reputation)

        # Discount score
        if original_price and original_price > 0:
            discount_pct = (original_price - price) / original_price
            discount_score = min(discount_pct + (coupon_discount / original_price), 1.0)
        else:
            discount_score = coupon_discount / max(price, 1) if coupon_discount > 0 else 0.0

        # Final weighted score
        final_score = (
            price_score * ScoreService.PRICE_WEIGHT
            + shipping_score * ScoreService.SHIPPING_WEIGHT
            + rating_score * ScoreService.SELLER_RATING_WEIGHT
            + reputation_score * ScoreService.STORE_REPUTATION_WEIGHT
            + discount_score * ScoreService.DISCOUNT_WEIGHT
        ) * 10

        return round(max(0, min(10, final_score)), 2)
