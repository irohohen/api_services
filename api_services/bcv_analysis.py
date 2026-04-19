from typing import Dict, Any, List

def analyze_bank_rates(data: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, Dict[str, Any]]:
    """
    Analiza las tasas bancarias para extraer indicadores de mercado.
    
    Retorna:
        Un diccionario con el análisis por fecha:
        {
            "fecha": {
                "promedio_compra": float,
                "promedio_venta": float,
                "mejor_banco_compra": {"nombre": str, "valor": float},
                "mejor_banco_venta": {"nombre": str, "valor": float},
                "spread_mercado": float
            },
            ...
        }
    """
    analysis_results = {}

    for fecha, bancos in data.items():
        compras = []
        ventas = []
        
        best_buy_val = -1.0
        best_buy_bank = ""
        
        best_sell_val = float('inf')
        best_sell_bank = ""

        for banco, valores in bancos.items():
            compra = valores['compra']
            venta = valores['venta']
            
            compras.append(compra)
            ventas.append(venta)
            
            # El mejor banco para COMPRAR divisas es el que tiene la VENTA más baja
            if venta < best_sell_val:
                best_sell_val = venta
                best_sell_bank = banco
                
            # El mejor banco para VENDER divisas es el que tiene la COMPRA más alta
            if compra > best_buy_val:
                best_buy_val = compra
                best_buy_bank = banco

        avg_compra = sum(compras) / len(compras) if compras else 0
        avg_venta = sum(ventas) / len(ventas) if ventas else 0
        
        # El spread es la diferencia entre la mejor compra y la mejor venta del sistema
        spread = best_sell_val - best_buy_val if (best_sell_val != float('inf') and best_buy_val != -1.0) else 0

        analysis_results[fecha] = {
            "promedio_compra": round(avg_compra, 4),
            "promedio_venta": round(avg_venta, 4),
            "mejor_banco_compra": {"nombre": best_buy_bank, "valor": best_buy_val},
            "mejor_banco_venta": {"nombre": best_sell_bank, "valor": best_sell_val},
            "spread_mercado": round(spread, 4)
        }

    return analysis_results
