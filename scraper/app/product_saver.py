import logging
import re
from typing import List
from uuid import uuid4
from app.base_scraper import ScrapedProduct
from app.database import Database

logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    """Create URL slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:300]


class ProductSaver:
    """Saves scraped products to the database."""

    @staticmethod
    async def save_products(query: str, products: List[ScrapedProduct]) -> int:
        """Save scraped products to database. Returns count of saved items."""
        saved_count = 0

        for scraped in products:
            try:
                # Get or create product
                product_id = await ProductSaver._get_or_create_product(scraped, query)
                if not product_id:
                    continue

                # Get store
                store_id = await ProductSaver._get_store_id(scraped.store_slug)
                if not store_id:
                    continue

                # Create or update offer
                await ProductSaver._save_offer(product_id, store_id, scraped)
                saved_count += 1

            except Exception as e:
                logger.error(f"Failed to save product '{scraped.name}': {e}")
                continue

        logger.info(f"Saved {saved_count}/{len(products)} products for query '{query}'")
        return saved_count

    @staticmethod
    async def _get_or_create_product(scraped: ScrapedProduct, query: str):
        """Find existing product or create new one."""
        slug = slugify(scraped.name)

        # Try to find existing product by slug
        existing = await Database.fetchrow(
            "SELECT id FROM products WHERE slug = $1",
            slug,
        )

        if existing:
            return existing['id']

        # Create new product
        product_id = uuid4()
        await Database.execute(
            """
            INSERT INTO products (id, name, slug, category, image_url)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT DO NOTHING
            """,
            product_id,
            scraped.name[:500],
            slug,
            query,
            scraped.image_url,
        )

        return product_id

    @staticmethod
    async def _get_store_id(store_slug: str):
        """Get store ID by slug."""
        result = await Database.fetchrow(
            "SELECT id FROM stores WHERE slug = $1",
            store_slug,
        )
        return result['id'] if result else None

    @staticmethod
    async def _save_offer(product_id, store_id, scraped: ScrapedProduct):
        """Create or update an offer."""
        # Check existing offer
        existing = await Database.fetchrow(
            """
            SELECT id FROM offers
            WHERE product_id = $1 AND store_id = $2 AND url = $3
            """,
            product_id,
            store_id,
            scraped.url[:1000],
        )

        if existing:
            # Update existing offer
            offer_id = existing['id']
            await Database.execute(
                """
                UPDATE offers SET
                    price = $1, original_price = $2, shipping_cost = $3,
                    shipping_time = $4, seller_name = $5, seller_rating = $6,
                    is_available = true, last_checked = NOW(), updated_at = NOW()
                WHERE id = $7
                """,
                scraped.price,
                scraped.original_price,
                scraped.shipping_cost,
                scraped.shipping_time,
                scraped.seller_name,
                scraped.seller_rating,
                offer_id,
            )
        else:
            # Create new offer
            offer_id = uuid4()
            await Database.execute(
                """
                INSERT INTO offers (id, product_id, store_id, price, original_price,
                    shipping_cost, shipping_time, url, seller_name, seller_rating, is_available)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, true)
                """,
                offer_id,
                product_id,
                store_id,
                scraped.price,
                scraped.original_price,
                scraped.shipping_cost,
                scraped.shipping_time,
                scraped.url[:1000],
                scraped.seller_name,
                scraped.seller_rating,
            )

        # Save price history
        await Database.execute(
            """
            INSERT INTO price_history (id, offer_id, product_id, store_id, price, shipping_cost)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            uuid4(),
            offer_id,
            product_id,
            store_id,
            scraped.price,
            scraped.shipping_cost,
        )

        # Calculate and update score
        await ProductSaver._update_score(offer_id, product_id, store_id, scraped)

    @staticmethod
    async def _update_score(offer_id, product_id, store_id, scraped: ScrapedProduct):
        """Calculate and update offer score."""
        # Get price range for product
        result = await Database.fetchrow(
            """
            SELECT MIN(price) as min_price, MAX(price) as max_price
            FROM offers WHERE product_id = $1 AND is_available = true
            """,
            product_id,
        )

        min_price = float(result['min_price']) if result and result['min_price'] else scraped.price
        max_price = float(result['max_price']) if result and result['max_price'] else scraped.price

        # Get store reputation
        store_result = await Database.fetchrow(
            "SELECT reputation_score FROM stores WHERE id = $1",
            store_id,
        )
        store_rep = float(store_result['reputation_score']) if store_result else 0.5

        # Calculate score
        from app.score_calculator import calculate_score
        score = calculate_score(
            price=scraped.price,
            min_price=min_price,
            max_price=max_price,
            shipping_cost=scraped.shipping_cost,
            seller_rating=scraped.seller_rating,
            store_reputation=store_rep,
            original_price=scraped.original_price,
        )

        await Database.execute(
            "UPDATE offers SET score = $1 WHERE id = $2",
            score,
            offer_id,
        )
