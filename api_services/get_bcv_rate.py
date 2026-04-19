import requests
from bs4 import BeautifulSoup
import re
import urllib3
import time
from typing import Optional, List, Tuple, Dict, Any

# Deshabilitar advertencias SSL a nivel de módulo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BCVError(Exception):
    """Excepción personalizada para errores relacionados con la obtención de datos del BCV."""
    pass

def scrap_get_bcv_rate(moneda: str = "dolar") -> float:
    """Scrapea la página del BCV para obtener la tasa de cambio.
       Parámetros:
           moneda: "dolar", "euro", "yuan", "lira", "rublo" (por defecto "dolar")
       Retorna:
           Tasa de cambio como float
    """
    url = "https://www.bcv.org.ve/estadisticas/tipo-cambio-de-referencia-smc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        moneda_element = soup.find('div', {'id': moneda})
        
        if moneda_element:
            for element in moneda_element.find_all(['div', 'span', 'strong']):
                text = element.get_text(strip=True)
                if re.match(r'^\d{1,3}[,\.]\d{2,8}$', text):
                    return float(text.replace(',', '.'))
        
        raise BCVError(f"No se encontró la tasa de cambio para '{moneda}' en la página del BCV.")

    except requests.RequestException as e:
        raise BCVError(f"Error de conexión al obtener datos del BCV: {e}")
    except Exception as e:
        if isinstance(e, BCVError):
            raise e
        raise BCVError(f"Error inesperado procesando la tasa del BCV: {e}")

def get_bcv_rate(moneda: str = "usd") -> float:
    """Obtiene la tasa de cambio del BCV para la moneda especificada. 
         Parámetros:
              moneda: Código de moneda (ej. 'usd', 'eur', 'cny')
            Retorna:
              Tasa de cambio como float
    """
    currency_map = {
        "usd": "dolar",
        "dolar": "dolar",
        "eur": "euro",
        "euro": "euro",
        "cny": "yuan",
        "yuan": "yuan",
        "try": "lira",
        "lira": "lira",
        "rub": "rublo",
        "rublo": "rublo"
    }
    
    mon = currency_map.get(moneda.lower())
    if not mon:
        raise ValueError(f"Moneda '{moneda}' no soportada. Use 'usd', 'eur', 'cny', 'try' o 'rub'.")
    
    return scrap_get_bcv_rate(mon)

if __name__ == "__main__":
    try:
        tasa = get_bcv_rate()
        print(f"Tasa BCV obtenida: {tasa}")
    except (BCVError, ValueError) as e:
        print(f"Error: {e}")
