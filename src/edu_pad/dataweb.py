import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import os
from pathlib import Path
from datetime import datetime

class QuotesScraper:
    """
    Scraper profesional con persistencia de datos y manejo histórico
    
    Uso:
    scraper = QuotesScraper()
    df = scraper.get_quotes(pages=2)  # Devuelve DataFrame con las citas
    """
    
    BASE_URL = "https://quotes.toscrape.com"
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    HISTORICAL_DIR = os.path.join(DATA_DIR, 'histórico')
    CSV_ACTUAL = os.path.join(DATA_DIR, "quotes_actual.csv")
    EXCEL_ACTUAL = os.path.join(DATA_DIR, "quotes_actual.xlsx")
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self._setup_directories()
    
    def _setup_directories(self):
        """Crea las estructuras de directorios necesarias"""
        Path(self.DATA_DIR).mkdir(exist_ok=True)
        Path(self.HISTORICAL_DIR).mkdir(exist_ok=True)
    
    def _get_soup(self, url: str):
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
            'tags': '|'.join(tags),  # Separador más robusto
            'tags_count': len(tags),
            'first_tag': tags[0] if tags else None,
            'fecha_extraccion': datetime.now().strftime('%Y-%m-%d')  # Nueva columna
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
    
    def save_historical_data(self, df: pd.DataFrame):
        """Guarda datos con marca temporal para historial"""
        if not df.empty:
            fecha = datetime.now().strftime('%Y-%m-%d')
            df.to_csv(os.path.join(self.HISTORICAL_DIR, f'quotes_{fecha}.csv'), index=False)
            df.to_excel(os.path.join(self.HISTORICAL_DIR, f'quotes_{fecha}.xlsx'), index=False)
    
    def save_current_data(self, df: pd.DataFrame):
        """Guarda versión actual de los datos"""
        if not df.empty:
            df.to_csv(self.CSV_ACTUAL, index=False)
            df.to_excel(self.EXCEL_ACTUAL, index=False)
    
    def get_quotes(self, pages: int = 1) -> pd.DataFrame:
        """
        Obtiene citas, guarda en múltiples formatos y devuelve DataFrame
        """
        df = self.scrape_quotes(pages)
        
        if not df.empty:
            self.save_historical_data(df)
            self.save_current_data(df)
            print(f"\n✅ Scraping completado. {len(df)} citas obtenidas.")
            print(f"📁 Datos guardados en:\n- {self.CSV_ACTUAL}\n- {self.HISTORICAL_DIR}/")
        else:
            print("\n⚠️ No se obtuvieron datos. Verifica la conexión.")
        
        return df

def main():
    """Función principal para ejecución CLI"""
    print("=== Scraper de Citaciones ===")
    scraper = QuotesScraper()
    quotes_df = scraper.get_quotes(pages=2)
    
    if not quotes_df.empty:
        print("\n📊 Vista previa de datos:")
        print(quotes_df[['quote', 'author', 'tags_count']].head(3))
        print(f"\n⏰ Última extracción: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()