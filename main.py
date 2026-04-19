from api_services.get_bcv_rate import get_bcv_rate
from api_services.get_binance_p2p_prices import get_binance_p2p_prices
from api_services.get_bcv_bank_rates import get_bcv_bank_rates, BCVBankError
from api_services.bcv_analysis import analyze_bank_rates
from api_services.binance_p2p_liquidity import get_binance_p2p_order_book

if __name__ == "__main__":
    # Ejemplo de uso 1: USDC y EUR
    try:
        first_price, simple_avg, weighted_avg = get_binance_p2p_prices("BUY", "usdc")
        print(f"USDC - Primer precio: {first_price}, Promedio simple: {simple_avg}, Promedio ponderado: {weighted_avg}")
        
        bcv_price = get_bcv_rate("eur")
        print(f"Tasa de cambio del BCV (EUR): {bcv_price}")
    except Exception as e:
        print(f"Error en el primer ejemplo: {e}")

    # Ejemplo de uso 2: Valores por defecto
    try:
        first_price2, simple_avg2, weighted_avg2 = get_binance_p2p_prices("BUY")
        print(f"USDT - Primer precio: {first_price2}, Promedio simple: {simple_avg2}, Promedio ponderado: {weighted_avg2}")
        
        bcv_price2 = get_bcv_rate("euro")
        print(f"Tasa de cambio del BCV (EUR): {bcv_price2}")
    except Exception as e:
        print(f"Error en el segundo ejemplo: {e}")

    # Ejemplo de uso 3: Tasas Bancarias BCV y Análisis
    try:
        print("\nObteniendo y analizando tasas bancarias del BCV...")
        bank_rates = get_bcv_bank_rates()
        
        # Realizamos el análisis de mercado
        market_analysis = analyze_bank_rates(bank_rates)
        
        import pprint
        pprint.pprint(market_analysis)
        
    except BCVBankError as e:
        print(f"Error al obtener tasas bancarias: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

    # Ejemplo de uso 4: Liquidez y Libro de Órdenes Binance P2P
    try:
        print("\nAnalizando liquidez de Binance P2P (BUY USDT)...")
        liquidity_data = get_binance_p2p_order_book("BUY")
        print(f"Liquidez Total en Página 1: {liquidity_data['total_liquidity']} USDT")
        print(f"Precio Promedio de la Página: {liquidity_data['avg_price']}")
        print("Top 3 ofertas por volumen:")
        # Ordenamos las órdenes por surplusAmount de mayor a menor
        sorted_orders = sorted(liquidity_data['orders'], key=lambda x: x['surplusAmount'], reverse=True)
        for order in sorted_orders[:3]:
            print(f"- {order['user']}: {order['surplusAmount']} USDT a {order['price']}")
    except Exception as e:
        print(f"Error al obtener liquidez de Binance: {e}")
