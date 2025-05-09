# linkedin_auto_scraper.py
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
import urllib.parse

class LinkedInEducationalScraper:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.universidad = os.getenv('UNIVERSIDAD', 'Universidad de Antioquia')
        
        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.options.add_argument(f'user-agent={random.choice(self.user_agents)}')
        
        self.driver = None
        self.perfiles = []
        self.current_page = 1
    
    def human_like_delay(self, min_time=1, max_time=3):
        time.sleep(random.uniform(min_time, max_time))
    
    def start_driver(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def human_like_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.25))
    
    def automatic_login(self):
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
    
    def direct_search(self, universidad):
        try:
            print(f"[EDUCATIONAL] Navegando a resultados de búsqueda para: {universidad}")
            
            query = f'"{universidad}" egresado'
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"
            
            print(f"[EDUCATIONAL] URL: {search_url}")
            self.driver.get(search_url)
            
            self.human_like_delay(5, 8)
            
            page_source = self.driver.page_source
            if "checkpoint/challenge" in page_source:
                print("[EDUCATIONAL] Se requiere verificación - pausa de 30 segundos")
                self.human_like_delay(30, 45)
            
        except Exception as e:
            print(f"Error en búsqueda: {e}")
    
    def extract_profile_data(self, profile_url):
        """Extrae datos detallados del perfil individual"""
        try:
            print(f"[EDUCATIONAL] Entrando al perfil: {profile_url}")
            
            # Abrir perfil en nueva ventana
            main_window = self.driver.current_window_handle
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(profile_url)
            self.human_like_delay(5, 8)
            
            # Extraer información del perfil
            perfil_data = {}
            
            # Nombre
            try:
                perfil_data['nombre'] = self.driver.find_element(By.CSS_SELECTOR, "h1.pv-top-card-profile-picture__container").text.strip()
            except:
                perfil_data['nombre'] = "No disponible"
            
            # Título profesional
            try:
                perfil_data['titulo'] = self.driver.find_element(By.CSS_SELECTOR, "div.text-body-medium").text.strip()
            except:
                perfil_data['titulo'] = "No disponible"
            
            # Ubicación
            try:
                perfil_data['ubicacion'] = self.driver.find_element(By.CSS_SELECTOR, "span.text-body-small").text.strip()
            except:
                perfil_data['ubicacion'] = "No disponible"
            
            # Información "Acerca de"
            try:
                about_section = self.driver.find_element(By.ID, "about")
                about_text = about_section.find_element(By.CSS_SELECTOR, "div.pv-shared-text-with-see-more").text.strip()
                perfil_data['acerca_de'] = about_text
            except:
                perfil_data['acerca_de'] = "No disponible"
            
            # Educación
            try:
                education_section = self.driver.find_element(By.ID, "education")
                education_items = education_section.find_elements(By.CSS_SELECTOR, "li.pvs-list__paged-list-item")
                education_list = []
                
                for edu in education_items[:3]:  # Tomar solo 3 educaciones
                    try:
                        school = edu.find_element(By.CSS_SELECTOR, "span.mr1").text.strip()
                        degree = edu.find_element(By.CSS_SELECTOR, "span.t-14").text.strip()
                        education_list.append({"escuela": school, "titulo": degree})
                    except:
                        continue
                
                perfil_data['educacion'] = education_list
            except:
                perfil_data['educacion'] = []
            
            # Experiencia
            try:
                experience_section = self.driver.find_element(By.ID, "experience")
                experience_items = experience_section.find_elements(By.CSS_SELECTOR, "li.pvs-list__paged-list-item")
                experience_list = []
                
                for exp in experience_items[:3]:  # Tomar solo 3 experiencias
                    try:
                        company = exp.find_element(By.CSS_SELECTOR, "span.mr1").text.strip()
                        position = exp.find_element(By.CSS_SELECTOR, "span.t-bold").text.strip()
                        duration = exp.find_element(By.CSS_SELECTOR, "span.t-14").text.strip()
                        experience_list.append({
                            "empresa": company,
                            "puesto": position,
                            "duracion": duration
                        })
                    except:
                        continue
                
                perfil_data['experiencia'] = experience_list
            except:
                perfil_data['experiencia'] = []
            
            # Skills
            try:
                skills_section = self.driver.find_element(By.CSS_SELECTOR, "section[data-section='skills']")
                skills_items = skills_section.find_elements(By.CSS_SELECTOR, "li.pvs-list__paged-list-item")
                skills_list = []
                
                for skill in skills_items[:10]:  # Tomar solo 10 skills
                    try:
                        skill_name = skill.find_element(By.CSS_SELECTOR, "span.mr1").text.strip()
                        skills_list.append(skill_name)
                    except:
                        continue
                
                perfil_data['habilidades'] = skills_list
            except:
                perfil_data['habilidades'] = []
            
            # Cerrar ventana y volver a la lista
            self.driver.close()
            self.driver.switch_to.window(main_window)
            self.human_like_delay(2, 3)
            
            return perfil_data
            
        except Exception as e:
            print(f"Error al extraer datos del perfil: {e}")
            try:
                self.driver.close()
                self.driver.switch_to.window(main_window)
            except:
                pass
            return None
    
    def extract_profiles_from_page(self):
        """Extrae perfiles de la página actual"""
        try:
            self.scroll_page()
            
            profile_cards = self.driver.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container")
            print(f"[EDUCATIONAL] Perfiles en página {self.current_page}: {len(profile_cards)}")
            
            for index, card in enumerate(profile_cards):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    self.human_like_delay(0.5, 1)
                    
                    # Extraer enlace del perfil
                    try:
                        profile_link = card.find_element(By.CSS_SELECTOR, "a.app-aware-link[href*='/in/']")
                        profile_url = profile_link.get_attribute('href')
                    except:
                        try:
                            profile_link = card.find_element(By.CSS_SELECTOR, "a[href*='/in/']")
                            profile_url = profile_link.get_attribute('href')
                        except:
                            profile_url = None
                    
                    # Extraer nombre básico
                    try:
                        name_element = card.find_element(By.CSS_SELECTOR, "span[dir='ltr'] span[aria-hidden='true']")
                        nombre = name_element.text.strip()
                    except:
                        nombre = "No disponible"
                    
                    # Filtrar perfiles que dicen "Miembro de LinkedIn"
                    if nombre and "Miembro de LinkedIn" not in nombre and nombre != "No disponible":
                        print(f"[EDUCATIONAL] Procesando perfil: {nombre}")
                        
                        # Extraer datos completos si tenemos URL
                        if profile_url:
                            perfil_data = self.extract_profile_data(profile_url)
                            if perfil_data:
                                perfil_data['url'] = profile_url
                                perfil_data['id'] = len(self.perfiles) + 1
                                perfil_data['fecha_extraccion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                perfil_data['pagina'] = self.current_page
                                
                                self.perfiles.append(perfil_data)
                                print(f"[EDUCATIONAL] Perfil completado: {perfil_data['nombre']}")
                        else:
                            # Fallback a datos básicos si no hay URL
                            perfil_basico = {
                                "id": len(self.perfiles) + 1,
                                "nombre": nombre,
                                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "pagina": self.current_page
                            }
                            self.perfiles.append(perfil_basico)
                            print(f"[EDUCATIONAL] Perfil básico guardado: {nombre}")
                    else:
                        print(f"[EDUCATIONAL] Perfil descartado: {nombre}")
                    
                except Exception as e:
                    print(f"Error al extraer perfil en {index}: {e}")
                    continue
            
            return len(profile_cards)
            
        except Exception as e:
            print(f"Error al extraer perfiles de la página: {e}")
            return 0
    
    def scroll_page(self):
        """Scroll para cargar todo el contenido de la página"""
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
        """Navega a la siguiente página de resultados"""
        try:
            next_button = None
            
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Siguiente']")
            except:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Página siguiente']")
                except:
                    pass
            
            if not next_button:
                try:
                    next_page_num = self.current_page + 1
                    next_button = self.driver.find_element(By.CSS_SELECTOR, f"button[aria-label='Página {next_page_num}']")
                except:
                    pass
            
            if next_button:
                print(f"[EDUCATIONAL] Navegando a página {self.current_page + 1}")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                self.human_like_delay(1, 2)
                next_button.click()
                self.human_like_delay(5, 8)
                self.current_page += 1
                return True
            
            print("[EDUCATIONAL] No se encontró manera de navegar a la siguiente página")
            return False
            
        except Exception as e:
            print(f"Error al navegar a siguiente página: {e}")
            return False
    
    def extract_profiles(self, max_pages=10):
        """Extrae perfiles de múltiples páginas"""
        print(f"[EDUCATIONAL] Extrayendo perfiles de hasta {max_pages} páginas...")
        
        for page in range(1, max_pages + 1):
            print(f"\n[EDUCATIONAL] Página {page}")
            
            profiles_found = self.extract_profiles_from_page()
            
            if profiles_found == 0:
                print(f"[EDUCATIONAL] No se encontraron perfiles en página {page}")
            
            if page < max_pages:
                if not self.navigate_to_next_page():
                    print("[EDUCATIONAL] No se pudo continuar a la siguiente página")
                    break
            
            self.human_like_delay(3, 5)
    
    def save_results(self, filename="resultados_educativo.json"):
        output = {
            "metadata": {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_perfiles": len(self.perfiles),
                "paginas_visitadas": self.current_page,
                "universidad_buscada": self.universidad,
                "proposito": "Investigación educativa en ciberseguridad"
            },
            "perfiles": self.perfiles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        print(f"[EDUCATIONAL] Resultados guardados en {filename}")
    
    def logout(self):
        """Cierra la sesión de LinkedIn"""
        try:
            print("[EDUCATIONAL] Cerrando sesión...")
            self.driver.get("https://www.linkedin.com/m/logout/")
            self.human_like_delay(3, 5)
            
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.url_contains("linkedin.com/login")
                )
                print("[EDUCATIONAL] Sesión cerrada exitosamente")
            except:
                print("[EDUCATIONAL] Sesión cerrada (verificación de URL fallida)")
            
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")
    
    def cleanup(self):
        if self.driver:
            self.logout()
            self.human_like_delay(2, 3)
            self.driver.quit()

if __name__ == "__main__":
    print("=" * 50)
    print("LINKEDIN EDUCATIONAL SCRAPER - Solo para fines educativos")
    print("Entender técnicas de web scraping en contexto de ciberseguridad")
    print("NOTA: Este script usará tu red actual de LinkedIn para obtener mejores resultados")
    print("=" * 50)
    
    scraper = LinkedInEducationalScraper()
    
    try:
        scraper.start_driver()
        scraper.automatic_login()
        
        print(f"[EDUCATIONAL] Buscando egresados de: {scraper.universidad}")
        
        scraper.direct_search(scraper.universidad)
        scraper.extract_profiles(max_pages=10)
        scraper.save_results()
        
        print(f"\n[EDUCATIONAL] Extracción completada: {len(scraper.perfiles)} perfiles")
        
    except KeyboardInterrupt:
        print("\n[EDUCATIONAL] Proceso detenido por el usuario")
    except Exception as e:
        print(f"[EDUCATIONAL] Error: {e}")
    finally:
        scraper.cleanup()