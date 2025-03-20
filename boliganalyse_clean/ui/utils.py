"""
Hjelpefunksjoner for web-applikasjonen

Denne modulen inneholder hjelpefunksjoner for web-applikasjonen.
"""

import os
import json
import time
import hashlib
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

from ui.config import CACHE_DIR, CACHE_TTL

def cache_result(key: str, data: Any, ttl: int = CACHE_TTL) -> bool:
    """
    Lagrer data i cache med en gitt nøkkel.
    
    Args:
        key: Unik nøkkel for cachen
        data: Data som skal lagres
        ttl: Levetid i sekunder
        
    Returns:
        True hvis lagring var vellykket, ellers False
    """
    try:
        cache_file = os.path.join(CACHE_DIR, f"{key}.json")
        
        cache_data = {
            'data': data,
            'timestamp': time.time(),
            'expires': time.time() + ttl
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    except Exception as e:
        print(f"Feil ved lagring av cache: {str(e)}")
        return False

def get_cached_result(key: str) -> Optional[Any]:
    """
    Henter data fra cache hvis den eksisterer og ikke er utløpt.
    
    Args:
        key: Unik nøkkel for cachen
        
    Returns:
        Cached data hvis funnet og gyldig, ellers None
    """
    try:
        cache_file = os.path.join(CACHE_DIR, f"{key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Sjekk om cachen er utløpt
        if time.time() > cache_data.get('expires', 0):
            return None
        
        return cache_data.get('data')
    
    except Exception as e:
        print(f"Feil ved henting av cache: {str(e)}")
        return None

def generate_cache_key(url: str) -> str:
    """
    Genererer en unik cache-nøkkel basert på URL.
    
    Args:
        url: URL som skal caches
        
    Returns:
        Unik cache-nøkkel
    """
    return hashlib.md5(url.encode()).hexdigest()

def format_price(price: int) -> str:
    """
    Formaterer pris med mellomrom som tusenskilletegn.
    
    Args:
        price: Pris som skal formateres
        
    Returns:
        Formatert prisstreng
    """
    return f"{price:,}".replace(',', ' ')

def format_date(timestamp: float) -> str:
    """
    Formaterer tidsstempel til lesbar dato.
    
    Args:
        timestamp: Unix-tidsstempel
        
    Returns:
        Formatert datostreng
    """
    return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')

def get_image_from_url(url: str) -> Optional[bytes]:
    """
    Henter bilde fra URL.
    
    Args:
        url: URL til bildet
        
    Returns:
        Bildedata hvis vellykket, ellers None
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Feil ved henting av bilde: {str(e)}")
        return None

def clean_html(html_text: str) -> str:
    """
    Fjerner HTML-tagger fra tekst.
    
    Args:
        html_text: Tekst med HTML-tagger
        
    Returns:
        Renset tekst
    """
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text)

def generate_share_link(analysis_id: str) -> str:
    """
    Genererer en delingslenke for en analyse.
    
    Args:
        analysis_id: Unik ID for analysen
        
    Returns:
        Delingslenke
    """
    # I en faktisk implementasjon ville dette generere en unik URL
    # For nå returnerer vi bare en placeholder
    return f"?share={analysis_id}"
