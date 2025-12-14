from django.conf import settings
import json

redis_client = settings.REDIS_CLIENT

CART_TTL = 60 * 30

def _cart_key(session_id):
    return f"cart:{session_id}"

def _details_key(session_id):
    return f"{_cart_key(session_id)}:details"

def _qty_key(session_id):
    return f"{_cart_key(session_id)}:qty"

def _refresh_cart_ttl_pipe(pipe, session_id):

    pipe.expire(_qty_key(session_id), CART_TTL)
    pipe.expire(_details_key(session_id), CART_TTL)
    pipe.expire(f"{_cart_key(session_id)}:promo_code", CART_TTL)

def add_to_cart(session_id, product_id, quantity, name, price):
    qty = _qty_key(session_id)
    details_key = _details_key(session_id)
    pipe = redis_client.pipeline()
    pipe.hincrby(qty, product_id, quantity)
    if not redis_client.hexists(details_key, product_id):
        product_data = {
            'product_id': product_id,
            'name': name,
            'price': price,
        }
        pipe.hset(details_key, product_id, json.dumps(product_data))

    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()

def get_cart(session_id):
    qtys = redis_client.hgetall(_qty_key(session_id))
    details = redis_client.hgetall(_details_key(session_id))
    cart_items = []
    for pid, qty in qtys.items():
        detail_json = details.get(pid)
        if not detail_json:
            continue
        data = json.loads(detail_json)
        data["quantity"] = int(qty)
        cart_items.append(data)
    return cart_items

def remove_from_cart(session_id, product_id):
    pipe = redis_client.pipeline()
    pipe.hdel(_cart_key(session_id), product_id)
    pipe.hdel(_qty_key(session_id), product_id)

    _refresh_cart_ttl_pipe(pipe, session_id)
    if not redis_client.exists(_qty_key(session_id)):
        promo_code = f"cart:{session_id}:promo_code"
        pipe.delete(promo_code)
    pipe.execute()

def clear_cart(session_id):
    pipe = redis_client.pipeline()
    pipe.delete(_qty_key(session_id))
    pipe.delete(_details_key(session_id))
    pipe.delete(f"_cart:{session_id}:promo_code")
    pipe.execute()

def increament_quantity(session_id, product_id, step=1):
    pipe = redis_client.pipeline()
    pipe.hincrby(_qty_key(session_id), product_id, step)
    _refresh_cart_ttl_pipe(pipe, session_id)
    return True

def decrement_quantity(session_id, product_id, step=1):
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)

    MAX_ATTEMPTS = 5

    for attempt in range(MAX_ATTEMPTS):
        try:
            with redis_client.pipeline() as pipe:
                pipe.watch(qty_key)
                current_qty = pipe.hget(qty_key, product_id)
                if current_qty is None:
                    pipe.unwatch()
                    return False
                current_qty = int(current_qty)
                new_qty = current_qty - step
                pipe.multi()
                if new_qty <1:
                    pipe.hdel(qty_key, product_id)
                    pipe.hdel(details_key, product_id)
                else:
                    pipe.hset(qty_key, product_id, new_qty)
                _refresh_cart_ttl_pipe(session_id)
                pipe.execute()
                return True
        except redis_client.WatchError:
            continue

def set_quantity(session_id, product_id, quantity):
    qty_key = _qty_key(session_id)
    existing = redis_client.hget(qty_key, product_id)
    if not existing:
        return False
    pipe = redis_client.pipeline()
    pipe.hset(qty_key, product_id, quantity)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()
    return True

def set_promo_code(session_id, promo_code):
    key = f"cart:{session_id}:promo_code"
    pipe = redis_client.pipeline()
    pipe.set(key, promo_code)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()

def get_promo_code(session_id):
    key = f"cart:{session_id}:promo_code"
    return redis_client.get(key)

def update_cart_item(session_id, product_id, name, price, quantity):
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)

    product_data= {
        "product_id": product_id,
        "name": name,
        "price": price,
    }
    pipe = redis_client.pipeline()
    pipe.hset(details_key, product_id, json.dumps(product_data))
    pipe.hset(qty_key, product_id, quantity)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()