import re

def parse_currency_value(text: str) -> float:
    """
    Parsea una cadena de texto con formato numérico (incluyendo formato venezolano/europeo 
    con separadores de miles y comas decimales) a un valor float de manera robusta.

    Parámetros:
        text: Cadena con el texto numérico (ej: "36.123,45", "1.234,56", "36,50", "36.50")
    Retorna:
        Valor numérico como float
    """
    cleaned = text.strip()
    cleaned = re.sub(r'[^\d,\.]', '', cleaned)
    
    if not cleaned:
        raise ValueError(f"No se pudo parsear el valor numérico de: '{text}'")
        
    if ',' in cleaned and '.' in cleaned:
        last_comma = cleaned.rfind(',')
        last_dot = cleaned.rfind('.')
        if last_comma > last_dot:
            # Formato europeo/venezolano: 36.123,45 -> miles='.', decimal=','
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # Formato anglosajón: 36,123.45 -> miles=',', decimal='.'
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Solo comas (ej: 36,50 o 1,234)
        # Si tiene comas como separador de miles (ej: 1,234.56 ya manejado arriba, o 1,234)
        if len(cleaned.split(',')[-1]) == 3 and len(cleaned.split(',')[0]) <= 3:
            cleaned = cleaned.replace(',', '')
        else:
            cleaned = cleaned.replace(',', '.')
    elif '.' in cleaned:
        # Solo puntos (ej: 36.50 o 1.234)
        parts = cleaned.split('.')
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3 and len(parts[0]) <= 3):
            cleaned = cleaned.replace('.', '')
            
    return float(cleaned)
