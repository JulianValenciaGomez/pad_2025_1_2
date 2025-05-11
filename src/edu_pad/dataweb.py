import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from typing import Optional
import os
from pathlib import Path

class QuotesScraper:
    """
    Scraper profesional que guarda datos persistentemente en archivos locales.
    
    Uso:
    scraper = QuotesScraper()
    df = scraper.get_quotes(pages=2)  # Obtiene datos y los guarda automáticamente
    """
    
    BASE_URL = "https://quotes.toscrape.com"
    DATA_DIR = "data"
    CSV_PATH = os.path.join(DATA_DIR, "quotes_data.csv")
    EXCEL_PATH = os.path.join(DATA_DIR, "quotes_data.xlsx")
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self._setup_data_directory()
    
    def _setup_data_directory(self):
        """Crea el directorio data si no existe"""
        Path(self.DATA_DIR).mkdir(exist_ok=True)
    
    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Obtiene y parsea HTML con manejo robusto de errores"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener {url}: {str(e)}")
            return None
    
    def _extract_quote_data(self, quote_div) -> dict:
        """Extrae datos estructurados de un div de cita"""
        text = quote_div.find('span', class_='text').get_text(strip=True).replace('"', '')
        author = quote_div.find('small', class_='author').get_text(strip=True)
        author_link = urljoin(self.BASE_URL, quote_div.find('a')['href'])
        
        tags = [tag.get_text(strip=True) for tag in quote_div.find_all('a', class_='tag')]
        
        return {
            'quote': text,
            'author': author,
            'author_link': author_link,
            'tags': ', '.join(tags),
            'tags_count': len(tags),
            'first_tag': tags[0] if tags else None
        }
    
    def scrape_quotes(self, pages: int = 1) -> pd.DataFrame:
        """Realiza el scraping y devuelve un DataFrame"""
        all_quotes = []
        current_url = self.BASE_URL
        
        for page in range(1, pages + 1):
            print(f"Scrapeando página {page}...")
            soup = self._get_soup(current_url)
            
            if not soup:
                continue
                
            for div in soup.find_all('div', class_='quote'):
                try:
                    all_quotes.append(self._extract_quote_data(div))
                except Exception as e:
                    print(f"Error procesando cita: {str(e)}")
                    continue
            
            next_btn = soup.find('li', class_='next')
            if not next_btn:
                break
            current_url = urljoin(self.BASE_URL, next_btn.find('a')['href'])
        
        return pd.DataFrame(all_quotes)
    
    def save_data(self, df: pd.DataFrame, format: str = 'both'):
        """Guarda los datos en los formatos especificados"""
        if format in ('csv', 'both'):
            df.to_csv(self.CSV_PATH, index=False, encoding='utf-8-sig')
            print(f"\nDatos guardados en {self.CSV_PATH}")
        
        if format in ('excel', 'both'):
            df.to_excel(self.EXCEL_PATH, index=False)
            print(f"Datos guardados en {self.EXCEL_PATH}")
    
    def load_data(self, format: str = 'csv') -> Optional[pd.DataFrame]:
        """Carga datos existentes desde archivo"""
        try:
            if format == 'csv' and os.path.exists(self.CSV_PATH):
                return pd.read_csv(self.CSV_PATH)
            elif format == 'excel' and os.path.exists(self.EXCEL_PATH):
                return pd.read_excel(self.EXCEL_PATH)
            return None
        except Exception as e:
            print(f"Error cargando datos: {str(e)}")
            return None
    
    def get_quotes(self, pages: int = 1, force_rescrape: bool = False) -> pd.DataFrame:
        """
        Obtiene citas, con cache local automático.
        
        Args:
            pages: Número de páginas a scrapear
            force_rescrape: Si True, ignora datos existentes y rescrapea
            
        Returns:
            DataFrame con todas las citas
        """
        # Intentar cargar datos existentes si no forzamos rescrapeo
        if not force_rescrape and (df_existing := self.load_data()):
            print("Datos existentes cargados desde archivo.")
            return df_existing
        
        # Si no hay datos existentes o forzamos rescrapeo
        df = self.scrape_quotes(pages)
        
        if not df.empty:
            self.save_data(df)
            print(f"\n✅ Scraping completado. {len(df)} citas obtenidas.")
        else:
            print("\n⚠️ No se obtuvieron datos. Verifica la conexión o la estructura de la página.")
        
        return df


# Ejemplo de uso
if __name__ == "__main__":
    print("Iniciando scraper...")
    scraper = QuotesScraper()
    
    # Obtener datos (usará cache si existe, a menos que force_rescrape=True)
    quotes_df = scraper.get_quotes(pages=2)
    
    # Mostrar resultados
    if not quotes_df.empty:
        print("\n📊 Vista previa de los datos:")
        print(quotes_df.head())
        
        # Mostrar ubicación de los archivos guardados
        print("\n💾 Datos persistentes guardados en:")
        print(f"- CSV: {os.path.abspath(scraper.CSV_PATH)}")
        print(f"- Excel: {os.path.abspath(scraper.EXCEL_PATH)}")
    else:
        print("\nNo se obtuvieron datos para mostrar.")