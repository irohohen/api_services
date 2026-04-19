import requests
from bs4 import BeautifulSoup
import re
import urllib3
import time
from typing import Tuple, Dict, List, Any, Optional

def get_binance_p2p_prices(
    trade_type: str, 
    asset: str = "usdt", 
    payTypes: Optional[List[str]] = None, 
    page: int = 1
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """ Obtiene los precios del P2P de Binance para un tipo de operación (BUY o SELL).
        Parámetros:
            trade_type: "BUY" o "SELL"
            asset: Criptomoneda a consultar (por defecto "usdt")
            payTypes: Lista de métodos de pago a filtrar (por defecto todos)
            page: Página de resultados a consultar (por defecto 1)
        Retorna:
            first_price: Primer precio listado
            simple_avg: Promedio simple de los precios listados
            weighted_avg: Promedio ponderado por volumen de los precios listados
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
        return None, None, None

    prices = [float(ad["adv"]["price"]) for ad in data]
    volumes = [float(ad["adv"]["surplusAmount"]) for ad in data]

    first_price = prices[0]
    simple_avg = sum(prices) / len(prices)
    
    total_volume = sum(volumes)
    weighted_avg = sum(p * v for p, v in zip(prices, volumes)) / total_volume if total_volume > 0 else None

    return first_price, simple_avg, weighted_avg

if __name__ == "__main__":
    compra_pp, compra_avg, compra_pond = get_binance_p2p_prices("BUY")
    venta_pp, venta_avg, venta_pond = get_binance_p2p_prices("SELL")
    print(f"Compra - Primer Precio: {compra_pp}, Promedio Simple: {compra_avg}, Promedio Ponderado: {compra_pond}")
    print(f"Venta - Primer Precio: {venta_pp}, Promedio Simple: {venta_avg}, Promedio Ponderado: {venta_pond}")
