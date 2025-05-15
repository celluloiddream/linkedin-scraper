# linkedin_educational_scraper_improved.py
import os
import json
import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import urllib.parse

class LinkedInEducationalScraper:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.universidad = os.getenv('UNIVERSIDAD', 'Universidad de Antioquia')
        
        # Configuración del navegador
        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # User agents aleatorios
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.options.add_argument(f'user-agent={random.choice(self.user_agents)}')
        
        self.driver = None
        self.perfiles = []
        self.current_page = 1
        self.profile_urls = []
    
    def human_like_delay(self, min_time=1, max_time=3):
        """Simular delays humanos"""
        time.sleep(random.uniform(min_time, max_time))
    
    def start_driver(self):
        """Inicializar el driver de Chrome"""
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def human_like_type(self, element, text):
        """Simular escritura humana"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.25))
    
    def automatic_login(self):
        """Login automático a LinkedIn"""
        try:
            print("[EDUCATIONAL] Intentando login automático...")
            self.driver.get("https://www.linkedin.com/login")
            self.human_like_delay()
            
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            self.human_like_type(email_field, self.email)
            self.human_like_delay(0.5, 1.5)
            self.human_like_type(password_field, self.password)
            self.human_like_delay()
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
            )
            print("[EDUCATIONAL] Login exitoso")
            
        except Exception as e:
            print(f"Error en login: {e}")
            raise
    
    def search_university_graduates(self, universidad):
        """Buscar egresados de una universidad específica"""
        try:
            print(f"[EDUCATIONAL] Buscando egresados de: {universidad}")
            
            # Diferentes queries para buscar egresados
            queries = [
                f'"{universidad}" egresado',
                f'"{universidad}" graduate',
                f'"{universidad}" alumni',
                f'estudiante "{universidad}"',
                f'graduado "{universidad}"'
            ]
            
            # Usar la primera query
            query = queries[0]
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"
            
            print(f"[EDUCATIONAL] URL de búsqueda: {search_url}")
            self.driver.get(search_url)
            
            self.human_like_delay(5, 8)
            
            # Verificar si hay verificación requerida
            page_source = self.driver.page_source
            if "checkpoint/challenge" in page_source:
                print("[EDUCATIONAL] Se requiere verificación - pausa de 30 segundos")
                self.human_like_delay(30, 45)
            
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            raise
    
    def collect_profile_urls(self, max_pages=5):
        """Recolectar URLs de perfiles de múltiples páginas"""
        print(f"[EDUCATIONAL] Recolectando URLs de perfiles de hasta {max_pages} páginas...")
        
        for page in range(1, max_pages + 1):
            print(f"\n[EDUCATIONAL] Página {page}")
            
            # Scroll para cargar todo el contenido
            self.scroll_page()
            
            # Encontrar tarjetas de perfiles
            profile_cards = self.driver.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container")
            print(f"[EDUCATIONAL] Perfiles encontrados en página {page}: {len(profile_cards)}")
            
            for card in profile_cards:
                try:
                    # Extraer URL del perfil
                    profile_link = card.find_element(By.CSS_SELECTOR, "a.app-aware-link[href*='/in/']")
                    profile_url = profile_link.get_attribute('href')
                    
                    # Limpiar URL (quitar parámetros)
                    if '?' in profile_url:
                        profile_url = profile_url.split('?')[0]
                    
                    # Extraer nombre básico para verificar
                    try:
                        name_element = card.find_element(By.CSS_SELECTOR, "span[dir='ltr'] span[aria-hidden='true']")
                        nombre = name_element.text.strip()
                        
                        # Filtrar perfiles válidos
                        if nombre and "Miembro de LinkedIn" not in nombre and nombre != "No disponible":
                            if profile_url not in self.profile_urls:
                                self.profile_urls.append(profile_url)
                                print(f"[EDUCATIONAL] URL recolectada: {nombre}")
                    except:
                        # Si no puede extraer el nombre, agregar la URL de todos modos
                        if profile_url not in self.profile_urls:
                            self.profile_urls.append(profile_url)
                
                except Exception as e:
                    print(f"Error al extraer URL de perfil: {e}")
                    continue
            
            # Navegar a siguiente página si no es la última
            if page < max_pages:
                if not self.navigate_to_next_page():
                    print("[EDUCATIONAL] No se pudo continuar a la siguiente página")
                    break
                    
                self.human_like_delay(3, 5)
        
        print(f"[EDUCATIONAL] Total URLs recolectadas: {len(self.profile_urls)}")
    
    def scroll_page(self):
        """Hacer scroll para cargar todo el contenido"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 3
        
        while scroll_attempts < max_attempts:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.human_like_delay(2, 3)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
            scroll_attempts += 1
    
    def navigate_to_next_page(self):
        """Navegar a la siguiente página de resultados"""
        try:
            next_button = None
            
            # Buscar botón de siguiente página
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Siguiente']")
            except:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Página siguiente']")
                except:
                    try:
                        next_page_num = self.current_page + 1
                        next_button = self.driver.find_element(By.CSS_SELECTOR, f"button[aria-label='Página {next_page_num}']")
                    except:
                        pass
            
            if next_button and next_button.is_enabled():
                print(f"[EDUCATIONAL] Navegando a página {self.current_page + 1}")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                self.human_like_delay(1, 2)
                next_button.click()
                self.human_like_delay(5, 8)
                self.current_page += 1
                return True
            
            return False
            
        except Exception as e:
            print(f"Error al navegar a siguiente página: {e}")
            return False
    
    def extract_complete_profile(self, profile_url):
        """Extraer información completa de un perfil individual"""
        try:
            print(f"[EDUCATIONAL] Extrayendo perfil: {profile_url}")
            
            self.driver.get(profile_url)
            self.human_like_delay(5, 8)
            
            # Obtener el código fuente de la página
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            profile_data = {}
            profile_data['url'] = profile_url
            
            # Extraer nombre
            try:
                name = soup.find('h1', {'class': 'text-heading-xlarge inline t-24 v-align-middle break-words'})
                profile_data['name'] = name.get_text().strip() if name else "No disponible"
            except:
                profile_data['name'] = "No disponible"
            
            # Extraer headline/título
            try:
                headline = soup.find('div', {'class': 'text-body-medium break-words'})
                profile_data['headline'] = headline.get_text().strip() if headline else "No disponible"
            except:
                profile_data['headline'] = "No disponible"
            
            # Extraer ubicación
            try:
                location = soup.find('span', {'class': 'text-body-small inline t-black--light break-words'})
                profile_data['location'] = location.get_text().strip() if location else "No disponible"
            except:
                profile_data['location'] = "No disponible"
            
            # Intentar leer "Acerca de" (hacer clic en "Ver más" si existe)
            try:
                show_more_button = self.driver.find_element(By.CLASS_NAME, "inline-show-more-text__button")
                show_more_button.click()
                self.human_like_delay(1, 2)
                
                # Recargar soup después del clic
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'lxml')
                
                about = soup.find('div', {'class': 'display-flex ph5 pv3'})
                profile_data['about'] = about.get_text().strip() if about else "No disponible"
            except:
                profile_data['about'] = "No disponible"
            
            # Extraer educación
            profile_data['education'] = self.extract_education()
            
            # Extraer experiencia
            profile_data['experience'] = self.extract_experience()
            
            # Agregar metadatos
            profile_data['extraction_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            profile_data['university_searched'] = self.universidad
            
            return profile_data
            
        except Exception as e:
            print(f"Error al extraer perfil {profile_url}: {e}")
            return None
    
    def extract_education(self):
        """Extraer información de educación"""
        try:
            # Buscar sección de educación
            sections = self.driver.find_elements(By.CSS_SELECTOR, "section.artdeco-card")
            education_section = None
            
            for section in sections:
                if section.find_elements(By.CSS_SELECTOR, "div#education"):
                    education_section = section
                    break
            
            if not education_section:
                return []
            
            page_source = education_section.get_attribute('outerHTML')
            soup = BeautifulSoup(page_source, 'lxml')
            
            education_items = soup.find_all('div', {'class': 'artdeco-entity-lockup__content'})
            education_list = []
            
            for item in education_items:
                try:
                    education_data = {}
                    
                    # Extraer nombre de la institución
                    school = item.find('div', {'class': 'display-flex align-items-center mr1 t-bold'})
                    education_data['school'] = school.get_text().strip() if school else "No disponible"
                    
                    # Extraer degree
                    degree = item.find('span', {'class': 't-14 t-normal'})
                    education_data['degree'] = degree.get_text().strip() if degree else "No disponible"
                    
                    # Extraer fechas
                    dates = item.find('span', {'class': 't-14 t-normal t-black--light'})
                    education_data['dates'] = dates.get_text().strip() if dates else "No disponible"
                    
                    education_list.append(education_data)
                    
                except Exception as e:
                    print(f"Error al extraer educación: {e}")
                    continue
            
            return education_list[:3]  # Limitar a 3 educaciones
            
        except Exception as e:
            print(f"Error en extract_education: {e}")
            return []
    
    def extract_experience(self):
        """Extraer información de experiencia laboral"""
        try:
            # Buscar sección de experiencia
            sections = self.driver.find_elements(By.CSS_SELECTOR, "section.artdeco-card")
            experience_section = None
            
            for section in sections:
                if section.find_elements(By.CSS_SELECTOR, "div#experience"):
                    experience_section = section
                    break
            
            if not experience_section:
                return []
            
            page_source = experience_section.get_attribute('outerHTML')
            soup = BeautifulSoup(page_source, 'lxml')
            
            experience_items = soup.find_all('div', {'class': 'artdeco-entity-lockup__content'})
            experience_list = []
            
            for item in experience_items:
                try:
                    experience_data = {}
                    
                    # Extraer puesto
                    position = item.find('div', {'class': 'display-flex align-items-center mr1 t-bold'})
                    experience_data['position'] = position.get_text().strip() if position else "No disponible"
                    
                    # Extraer empresa
                    company = item.find('span', {'class': 't-14 t-normal'})
                    experience_data['company'] = company.get_text().strip() if company else "No disponible"
                    
                    # Extraer fechas
                    dates = item.find('span', {'class': 't-14 t-normal t-black--light'})
                    experience_data['dates'] = dates.get_text().strip() if dates else "No disponible"
                    
                    experience_list.append(experience_data)
                    
                except Exception as e:
                    print(f"Error al extraer experiencia: {e}")
                    continue
            
            return experience_list[:3]  # Limitar a 3 experiencias
            
        except Exception as e:
            print(f"Error en extract_experience: {e}")
            return []
    
    def extract_all_profiles(self, min_profiles=10):
        """Extraer información completa de todos los perfiles recolectados"""
        print(f"[EDUCATIONAL] Extrayendo información de {len(self.profile_urls)} perfiles...")
        
        extracted_count = 0
        
        for i, profile_url in enumerate(self.profile_urls, 1):
            if extracted_count >= min_profiles:
                break
                
            print(f"\n[EDUCATIONAL] Procesando perfil {i}/{len(self.profile_urls)}")
            
            profile_data = self.extract_complete_profile(profile_url)
            
            if profile_data:
                self.perfiles.append(profile_data)
                extracted_count += 1
                print(f"[EDUCATIONAL] Perfil extraído: {profile_data['name']}")
            
            # Delay entre perfiles para evitar detección
            self.human_like_delay(3, 6)
            
            # Pausa cada 5 perfiles
            if i % 5 == 0:
                print("[EDUCATIONAL] Pausa de seguridad...")
                self.human_like_delay(10, 15)
        
        print(f"\n[EDUCATIONAL] Total perfiles extraídos: {len(self.perfiles)}")
    
    def save_results(self, filename="perfiles_egresados.json"):
        """Guardar resultados en archivo JSON"""
        output = {
            "metadata": {
                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "universidad_buscada": self.universidad,
                "total_perfiles": len(self.perfiles),
                "proposito": "Investigación educativa en ciberseguridad",
                "version": "1.0"
            },
            "perfiles": self.perfiles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        
        print(f"[EDUCATIONAL] Resultados guardados en {filename}")
    
    def logout(self):
        """Cerrar sesión de LinkedIn"""
        try:
            print("[EDUCATIONAL] Cerrando sesión...")
            self.driver.get("https://www.linkedin.com/m/logout/")
            self.human_like_delay(3, 5)
            print("[EDUCATIONAL] Sesión cerrada exitosamente")
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            self.logout()
            self.human_like_delay(2, 3)
            self.driver.quit()

def main():
    print("=" * 60)
    print("LINKEDIN EDUCATIONAL SCRAPER MEJORADO")
    print("Extracción de perfiles de egresados universitarios")
    print("Solo para fines educativos en ciberseguridad")
    print("=" * 60)
    
    scraper = LinkedInEducationalScraper()
    
    try:
        # Inicializar driver y login
        scraper.start_driver()
        scraper.automatic_login()
        
        # Buscar universidad
        scraper.search_university_graduates(scraper.universidad)
        
        # Recolectar URLs de perfiles (ajustar max_pages según necesidad)
        scraper.collect_profile_urls(max_pages=3)
        
        # Extraer información completa de perfiles (mínimo 10)
        scraper.extract_all_profiles(min_profiles=10)
        
        # Guardar resultados
        scraper.save_results()
        
        print(f"\n[EDUCATIONAL] ¡Extracción completada exitosamente!")
        print(f"Total de perfiles extraídos: {len(scraper.perfiles)}")
        
    except KeyboardInterrupt:
        print("\n[EDUCATIONAL] Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"[EDUCATIONAL] Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()