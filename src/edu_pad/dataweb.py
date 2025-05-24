import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
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
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')  # Ruta relativa al script
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
            'tags': '|'.join(tags),  # Separador más robusto que la coma
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
    
    def load_data(self, format: str = 'csv') -> pd.DataFrame:
        """Carga datos existentes desde archivo"""
        try:
            if format == 'csv' and os.path.exists(self.CSV_PATH):
                return pd.read_csv(self.CSV_PATH)
            elif format == 'excel' and os.path.exists(self.EXCEL_PATH):
                return pd.read_excel(self.EXCEL_PATH)
            return pd.DataFrame()  # Retorna DataFrame vacío si no hay archivos
        except Exception as e:
            print(f"Error cargando datos: {str(e)}")
            return pd.DataFrame()
    
    def get_quotes(self, pages: int = 1, force_rescrape: bool = False) -> pd.DataFrame:
        """
        Obtiene citas, con cache local automático.
        """
        if not force_rescrape:
            df_existing = self.load_data()
            if not df_existing.empty:
                print("Datos existentes cargados desde archivo.")
                return df_existing
        
        df = self.scrape_quotes(pages)
        
        if not df.empty:
            self.save_data(df)
            print(f"\n✅ Scraping completado. {len(df)} citas obtenidas.")
        else:
            print("\n⚠️ No se obtuvieron datos. Verifica la conexión o la estructura de la página.")
        
        return df

def main():
    """Función principal para ejecución desde CLI"""
    print("=== Iniciando scraper ===")
    scraper = QuotesScraper()
    quotes_df = scraper.get_quotes(pages=2)
    
    if not quotes_df.empty:
        print("\n📊 Vista previa de los datos:")
        print(quotes_df.head(3))
        print("\n💾 Datos guardados en:")
        print(f"- CSV: {os.path.abspath(scraper.CSV_PATH)}")
        print(f"- Excel: {os.path.abspath(scraper.EXCEL_PATH)}")
    else:
        print("\nNo se obtuvieron datos para mostrar.")

if __name__ == "__main__":
    main()