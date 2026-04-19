# Módulo `api_services`

Módulo privado de servicios de API y scraping para datos del mercado cambiario (BCV y Binance P2P), pensado para compartirse entre proyectos internos como fuente única de tasas y precios.

## Instalación

Al no publicarse en PyPI, inclúyelo como paquete local o submódulo Git y añade el directorio padre al `PYTHONPATH`, o instálalo en modo editable según el flujo de tu equipo.

### Dependencias

Desde la raíz del paquete:

```bash
pip install -r requirements.txt
```

Las piezas activas del paquete usan principalmente `requests`, `beautifulsoup4` y `urllib3` (este último suele instalarse como dependencia de `requests`).

## Cómo importar

El paquete reexporta solo dos símbolos en `__init__.py`:

- `get_bcv_rate`
- `get_binance_p2p_prices`

El resto de funciones se importan desde sus submódulos, por ejemplo:

```python
from api_services import get_bcv_rate, get_binance_p2p_prices
from api_services.get_bcv_bank_rates import get_bcv_bank_rates, BCVBankError
from api_services.bcv_analysis import analyze_bank_rates
from api_services.binance_p2p_liquidity import get_binance_p2p_order_book
```

## Servicios

### 1. Tasas oficiales BCV (`get_bcv_rate.py`)

Obtiene la tasa de referencia publicada en la web del BCV para varias monedas.

| Función | Descripción |
|--------|-------------|
| `get_bcv_rate(moneda: str = "usd") -> float` | Punto de entrada: normaliza códigos (`usd`, `eur`, …) y delega en el scraper interno. |
| `scrap_get_bcv_rate(moneda: str = "dolar") -> float` | Uso interno: espera ids de bloque HTML del BCV (`dolar`, `euro`, `yuan`, `lira`, `rublo`). |

**Monedas aceptadas por `get_bcv_rate`:** `usd`, `eur`, `cny`, `try`, `rub` (también alias en español como `dolar`, `euro`, etc., según el mapa del módulo).

**Excepciones:**

- `ValueError` si el código de moneda no está soportado.
- `BCVError` si falla la red, la respuesta HTTP o no se encuentra el valor en el HTML esperado.

### 2. Precios Binance P2P (`get_binance_p2p_prices.py`)

Consulta el endpoint público de anuncios P2P de Binance (fiat `VES`).

`get_binance_p2p_prices(trade_type, asset="usdt", payTypes=None, page=1)` devuelve una tupla `(Optional[float], Optional[float], Optional[float])`:

1. Precio de la primera oferta de la página.
2. Media aritmética de hasta **20** ofertas (`rows` fijo en el payload).
3. Media ponderada por `surplusAmount` de esas ofertas.

**Parámetros:** `trade_type` debe ser `"BUY"` o `"SELL"`; `asset` en minúsculas (p. ej. `usdt`, `usdc`); `payTypes` filtra métodos de pago; `page` selecciona la página de resultados.

**Comportamiento:** si la API no devuelve lista de anuncios, la función retorna `(None, None, None)`. Las respuestas HTTP erróneas propagan la excepción de `requests` (`raise_for_status`).

### 3. Tasas bancarias BCV (`get_bcv_bank_rates.py`)

`get_bcv_bank_rates() -> Dict[str, Dict[str, Dict[str, float]]]` hace scraping de la tabla de tasas informativas del sistema bancario.

Estructura típica:

```python
{
    "fecha": {
        "Nombre del banco": {"compra": float, "venta": float},
        ...
    },
    ...
}
```

**Excepciones:** `BCVBankError` ante fallos de conexión, HTML inesperado u otros errores encapsulados por el módulo.

### 4. Análisis de tasas bancarias (`bcv_analysis.py`)

`analyze_bank_rates(data)` recibe el diccionario devuelto por `get_bcv_bank_rates` y produce, **por cada fecha**, un diccionario con:

| Clave | Significado |
|-------|-------------|
| `promedio_compra` / `promedio_venta` | Promedio simple entre todos los bancos de esa fecha. |
| `mejor_banco_compra` | `{"nombre": str, "valor": float}` — banco con la **mayor** tasa de compra (mejor para quien vende divisas al banco). |
| `mejor_banco_venta` | `{"nombre": str, "valor": float}` — banco con la **menor** tasa de venta (mejor para quien compra divisas al banco). |
| `spread_mercado` | Diferencia entre la mejor venta y la mejor compra del sistema (`mejor_venta - mejor_compra` en términos de esos valores extremos). |

Los promedios y el spread se redondean a cuatro decimales en el resultado.

### 5. Libro de órdenes P2P (`binance_p2p_liquidity.py`)

`get_binance_p2p_order_book(trade_type, asset="usdt", payTypes=None, page=1)` usa el mismo endpoint que el servicio de precios pero devuelve un diccionario:

- `orders`: lista de `{"user", "price", "surplusAmount"}` por oferta en la página (hasta 20 filas).
- `total_liquidity`: suma de `surplusAmount` en esa página.
- `avg_price`: media simple de los precios de esas ofertas.

Si no hay datos, retorna `{"orders": [], "total_liquidity": 0.0, "avg_price": 0.0}`. Errores HTTP se manejan igual que en `get_binance_p2p_prices`.

## Ejemplo de uso

```python
from api_services import get_bcv_rate, get_binance_p2p_prices
from api_services.get_bcv_bank_rates import get_bcv_bank_rates, BCVBankError
from api_services.bcv_analysis import analyze_bank_rates
from api_services.binance_p2p_liquidity import get_binance_p2p_order_book

# BCV y Binance (precios agregados)
first, simple, weighted = get_binance_p2p_prices("BUY", "usdt")
eur = get_bcv_rate("eur")

# Tasas bancarias y análisis
try:
    bank_rates = get_bcv_bank_rates()
    analysis = analyze_bank_rates(bank_rates)
except BCVBankError as e:
    print(e)

# Liquidez en la primera página
liquidity = get_binance_p2p_order_book("BUY", "usdt")
print(f"USDT disponibles (página 1): {liquidity['total_liquidity']}")
```

En el repositorio, `main.py` amplía estos ejemplos con distintos activos y manejo de errores.

## Notas importantes

1. **SSL:** Las peticiones al sitio del BCV usan `verify=False` y se silencian advertencias de certificado (`InsecureRequestWarning`), por limitaciones habituales del servidor.
2. **Scraping:** `get_bcv_rate` y `get_bcv_bank_rates` dependen del HTML actual del BCV; un cambio de plantilla puede romper el parseo hasta actualizar selectores.
3. **Binance:** Puede aplicarse *rate limiting*; conviene caché o backoff si el consumo es alto.
