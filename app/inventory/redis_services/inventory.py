import json

from core import settings
from inventory.models import Product

r = settings.REDIS_CLIENT

def _inventory_key():
    return f"inventory_list"

def get_all_items():
    lists = r.exists(_inventory_key()) == 1
    if lists:
        ids = r.zrevrange(f"{_inventory_key()}:orderbyid", 0, -1)
        lists = r.hmget(_inventory_key(), ids)
        return [json.loads(l) for l in lists]
    else:
        products = Product.objects.all()
        for i in products:
            product_data = {
                'id': int(i.id),
                'name': i.name,
                'price': i.price,
                "slug": i.slug,
                "category_id": getattr(i.category, "id", None),
            }
            r.hset(_inventory_key(), i.id, json.dumps(product_data))
            r.zadd(f"{_inventory_key()}:orderbyid", {i.id:i.price})
        lists = r.hvals(_inventory_key())
        return [json.loads(l) for l in lists]

def cache_product(product) -> None:
    product_data = {
        'id': int(product.id),
        'name': product.name,
        'price': product.price,
        "slug": product.slug,
    }
    r.hset(_inventory_key(), product.id, json.dumps(product_data))











