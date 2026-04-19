import requests
from typing import List, Dict, Any, Optional

def get_binance_p2p_order_book(
    trade_type: str, 
    asset: str = "usdt", 
    payTypes: Optional[List[str]] = None, 
    page: int = 1
) -> Dict[str, Any]:
    """
    Obtiene el libro de órdenes detallado del P2P de Binance.
    
    Retorna:
        Un diccionario con:
        - 'orders': Lista de ofertas con precio, monto disponible y usuario.
        - 'total_liquidity': Suma total de surplusAmount de todas las ofertas en la página.
        - 'avg_price': Precio promedio simple de la página.
    """
    if payTypes is None:
        payTypes = []

    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "Content-Type": "application/json",
        "clienttype": "web",
    }
    payload = {
        "asset": asset.upper(),
        "fiat": "VES",
        "tradeType": trade_type,
        "page": page,
        "rows": 20,
        "payTypes": payTypes,
        "publisherType": None
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    data = r.json().get("data")

    if not data:
        return {"orders": [], "total_liquidity": 0.0, "avg_price": 0.0}

    orders = []
    total_liquidity = 0.0
    sum_prices = 0.0

    for ad in data:
        adv = ad.get("adv", {})
        price = float(adv.get("price", 0))
        surplus = float(adv.get("surplusAmount", 0))
        user = adv.get("userName", "Unknown")
        
        orders.append({
            "user": user,
            "price": price,
            "surplusAmount": surplus
        })
        
        total_liquidity += surplus
        sum_prices += price

    return {
        "orders": orders,
        "total_liquidity": total_liquidity,
        "avg_price": sum_prices / len(orders) if orders else 0.0
    }

if __name__ == "__main__":
    # Ejemplo: Ver cuántos USDT hay disponibles para COMPRAR (BUY) en la primera página
    try:
        book = get_binance_p2p_order_book("BUY")
        print(f"Liquidez Total Disponible: {book['total_liquidity']} USDT")
        print(f"Precio Promedio: {book['avg_price']}")
        print("\nDetalle de las primeras 5 ofertas:")
        for order in book['orders'][:5]:
            print(f"Usuario: {order['user']} | Precio: {order['price']} | Disponible: {order['surplusAmount']}")
    except Exception as e:
        print(f"Error: {e}")
