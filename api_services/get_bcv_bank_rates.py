import requests
from bs4 import BeautifulSoup
import urllib3
from typing import Dict, Any

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BCVBankError(Exception):
    """Excepción personalizada para errores en la obtención de tasas bancarias del BCV."""
    pass

def get_bcv_bank_rates() -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Obtiene las tasas informativas del sistema bancario desde el BCV.
    
    Retorna:
        Un diccionario estructurado como:
        {
            "fecha": {
                "nombre_del_banco": {"compra": 0.0, "venta": 0.0},
                ...
            },
            ...
        }
    """
    url = "https://www.bcv.org.ve/tasas-informativas-sistema-bancario"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscamos la tabla de tasas
        table = soup.find('table')
        if not table:
            raise BCVBankError("No se encontró la tabla de tasas bancarias en la página.")

        rows = table.find_all('tr')
        data_grouped = {}

        for row in rows[1:]:  # Omitimos la cabecera
            cols = row.find_all('td')
            if len(cols) < 4:
                continue

            # Mapeo corregido:
            # 0: Fecha, 1: Banco, 2: Compra, 3: Venta
            fecha = cols[0].get_text(strip=True)
            banco = cols[1].get_text(strip=True)
            compra_str = cols[2].get_text(strip=True).replace(',', '.')
            venta_str = cols[3].get_text(strip=True).replace(',', '.')

            try:
                compra = float(compra_str)
                venta = float(venta_str)
            except ValueError:
                continue # Saltamos filas con datos no numéricos

            if fecha not in data_grouped:
                data_grouped[fecha] = {}
            
            data_grouped[fecha][banco] = {
                "compra": compra,
                "venta": venta
            }

        return data_grouped

    except requests.RequestException as e:
        raise BCVBankError(f"Error de conexión al obtener tasas bancarias: {e}")
    except Exception as e:
        if isinstance(e, BCVBankError):
            raise e
        raise BCVBankError(f"Error inesperado procesando tasas bancarias: {e}")

if __name__ == "__main__":
    try:
        tasas = get_bcv_bank_rates()
        import pprint
        pprint.pprint(tasas)
    except BCVBankError as e:
        print(f"Error: {e}")
