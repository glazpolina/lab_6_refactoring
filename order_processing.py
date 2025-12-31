DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
MIN_PRICE = 0
MIN_QTY = 0

COUPON_RULES = {
    "SAVE10": {"discount_rate": 0.10, "min_amount": 0, "fixed_discount": 0},
    "SAVE20": {"discount_rate": 0.20, "min_amount": 200, "fallback_rate": 0.05, "fixed_discount": 0},
    "VIP": {"discount_rate": 0, "min_amount": 100, "fixed_discount": 50, "fallback_discount": 10},
}

def parse_request(request: dict):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency",DEFAULT_CURRENCY)
    return user_id, items, coupon, currency

def validate_request(user_id, items, currency):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
  
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")
    
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= MIN_PRICE:
            raise ValueError("price must be positive")
        if item["qty"] <= MIN_QTY:
            raise ValueError("qty must be positive")

def calculate_subtotal(items):
    return sum(item["price"] * item["qty"] for item in items)

def calculate_discount(subtotal, coupon):
    if not coupon or coupon == "":
        return 0
    
    if coupon not in COUPON_RULES:
        raise ValueError("unknown coupon")
    
    rule = COUPON_RULES[coupon]
    
    if coupon == "SAVE10":
        return int(subtotal * rule["discount_rate"])
    
    elif coupon == "SAVE20":
        rate = rule["discount_rate"] if subtotal >= rule["min_amount"] else rule["fallback_rate"]
        return int(subtotal * rate)
    
    elif coupon == "VIP":
        discount = rule["fixed_discount"] if subtotal >= rule["min_amount"] else rule["fallback_discount"]
        return discount
    
    return 0

def calculate_tax(amount):
    return int(amount * TAX_RATE)

def generate_order_id(user_id, items):
    return f"{user_id}-{len(items)}-X"

def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)
    validate_request(user_id, items, currency)
    
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, coupon)
    total_after_discount = max(subtotal - discount, 0) 
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax
    
    order_id = generate_order_id(user_id, items)

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
