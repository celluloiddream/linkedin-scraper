import os
import json
import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import urllib.parse

class LinkedInEducationalScraper:
    def __init__(self):
        """
        Initializes the scraper, loading environment variables, setting up Chrome options,
        and handling potential missing credentials.
        """
        try:
            load_dotenv()
            print("[EDUCATIONAL] Archivo .env cargado correctamente")
        except Exception as e:
            print(f"[EDUCATIONAL] No se pudo cargar el archivo .env: {e}")
            print("[EDUCATIONAL] Se usarán valores predeterminados")

        self.email = os.getenv('LINKEDIN_EMAIL', '')
        self.password = os.getenv('LINKEDIN_PASSWORD', '')
        self.universidad = os.getenv('UNIVERSIDAD', 'SENA')

        if not self.email or not self.password:
            print("[EDUCATIONAL] ADVERTENCIA: Credenciales de LinkedIn no configuradas en .env")
            print("[EDUCATIONAL] Deberá ingresarlas manualmente cuando se abra el navegador")

        self.options = Options()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--allow-insecure-content")
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.options.add_argument(f'user-agent={random.choice(self.user_agents)}')
        self.driver = None
        self.perfiles = []
        self.current_page = 1
        self.profile_urls = set()
    
    def start_driver(self):
        """Starts the Chrome WebDriver."""
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("[EDUCATIONAL] Navegador iniciado correctamente")
        except Exception as e:
            print(f"[EDUCATIONAL] Error al iniciar el navegador con WebDriverManager: {e}")
            try:
                print("[EDUCATIONAL] Intentando método alternativo para iniciar Chrome...")
                self.options.add_argument("--no-sandbox")
                self.options.add_argument("--disable-dev-shm-usage")
                chrome_path = None
                possible_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    "/usr/bin/google-chrome",
                    "/usr/bin/google-chrome-stable",
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/opt/google/chrome/chrome"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                if chrome_path:
                    self.options.binary_location = chrome_path
                self.driver = webdriver.Chrome(options=self.options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("[EDUCATIONAL] Navegador iniciado con método alternativo")
            except Exception as e2:
                print(f"[EDUCATIONAL] Error en método alternativo: {e2}")
                raise Exception("No se pudo iniciar el navegador después de múltiples intentos")

    def human_like_delay(self, min_time=1, max_time=3):
        """Introduces a random delay."""
        time.sleep(random.uniform(min_time, max_time))

    def human_like_type(self, element, text):
        """Simulates human-like typing speed."""
        for char in text:
            try:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.25))
            except Exception as e:
                print(f"[EDUCATIONAL] Error typing character {char}: {e}")
                break

    def automatic_login(self):
        """Attempts to log in to LinkedIn automatically."""
        try:
            print("[EDUCATIONAL] Intentando login automático...")
            self.driver.get("https://www.linkedin.com/login")
            self.human_like_delay()
            self.driver.save_screenshot("login_page.png")

            if not self.email or not self.password:
                print("[EDUCATIONAL] Credenciales no disponibles. Esperando login manual...")
                wait_time = 120
                print(f"[EDUCATIONAL] Por favor, inicie sesión manualmente. Esperando {wait_time} segundos...")
                try:
                    WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
                    )
                    print("[EDUCATIONAL] Login manual detectado")
                    return
                except:
                    print("[EDUCATIONAL] Tiempo de espera agotado para login manual. Continuando...")

            try:
                email_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                password_field = self.driver.find_element(By.ID, "password")
                self.human_like_type(email_field, self.email)
                self.human_like_delay(0.5, 1.5)
                self.human_like_type(password_field, self.password)
                self.human_like_delay()
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()

                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
                )
                print("[EDUCATIONAL] Login exitoso")
                self.driver.save_screenshot("after_login.png")
            except Exception as e:
                print(f"[EDUCATIONAL] Error en campos de login: {e}")
                print("[EDUCATIONAL] Esperando login manual...")
                try:
                    WebDriverWait(self.driver, 120).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
                    )
                    print("[EDUCATIONAL] Login manual completado")
                    self.driver.save_screenshot("after_manual_login.png")
                except:
                    print("[EDUCATIONAL] No se pudo detectar login manual.  Continuando...")
        except Exception as e:
            print(f"Error en login: {e}")
            print("[EDUCATIONAL] Intentando continuar con la sesión actual...")

    def direct_search(self, universidad):
        """Performs a search on LinkedIn for graduates of a given university."""
        try:
            print(f"[EDUCATIONAL] Navegando a resultados de búsqueda para: {universidad}")
            query = f'"{universidad}" egresado'
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"
            self.driver.get(search_url)
            self.human_like_delay(5, 8)
            output_dir = "screenshots"
            os.makedirs(output_dir, exist_ok=True)
            screenshot_path = os.path.join(output_dir, "search_results_initial.png")
            self.driver.save_screenshot(screenshot_path)
            page_source = self.driver.page_source
            if "checkpoint/challenge" in page_source:
                print("[EDUCATIONAL] Se requiere verificación - pausa de 30 segundos")
                self.human_like_delay(30, 45)
                self.driver.save_screenshot("checkpoint_challenge.png")

            result_selectors = [
                "li.reusable-search__result-container",
                "li.entity-result",
                "div.entity-result",
                "ul.reusable-search__entity-result-list",
                "div.search-results__container",
                "div.occludable-update"
            ]

            has_results = False
            for selector in result_selectors:
                try:
                    results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if results and len(results) > 0:
                        has_results = True
                        break
                except:
                    continue

            if not has_results:
                query_alt = f"{universidad} egresado"
                encoded_query_alt = urllib.parse.quote(query_alt)
                search_url_alt = f"https://www.linkedin.com/search/results/people/?keywords={encoded_query_alt}"
                self.driver.get(search_url_alt)
                self.human_like_delay(5, 8)
                self.driver.save_screenshot("search_results_alternative.png")
                for selector in result_selectors:
                    try:
                        results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if results and len(results) > 0:
                            has_results = True
                            break
                    except:
                        continue

            if not has_results:
                self.driver.get("https://www.linkedin.com/search/results/people/")
                self.human_like_delay(5, 8)
                self.driver.save_screenshot("search_results_generic.png")
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            self.driver.save_screenshot("search_error.png")

    def extract_profile_data(self, profile_url):
        """Extracts detailed profile data from a LinkedIn profile URL."""
        try:
            main_window = self.driver.current_window_handle
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(profile_url)
            self.human_like_delay(5, 8)
            profile_id = profile_url.split('/in/')[-1].split('?')[0]
            screenshot_path = f"profile_{profile_id}_screenshot.png"
            self.driver.save_screenshot(screenshot_path)
            perfil_data = {}
            name_selectors = [
                "h1.pv-top-card-profile-picture__container",
                "h1.text-heading-xlarge",
                "h1.break-words",
                "h1[data-generated-fonts-viewed]",
                "h1.artdeco-entity-lockup__title",
                "h1.leading-regular",
                "h1"
            ]
            for selector in name_selectors:
                try:
                    nombre = self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    if nombre:
                        perfil_data['nombre'] = nombre
                        break
                except:
                    continue
            if 'nombre' not in perfil_data:
                perfil_data['nombre'] = "No disponible"
            title_selectors = [
                "div.text-body-medium",
                ".pv-text-details__title",
                ".pv-text-details__left-panel .text-body-medium",
                ".ph5 .text-body-medium",
                ".pv-top-card--list .text-body-medium",
                "h2.mt1",
                ".text-body-text"
            ]
            for selector in title_selectors:
                try:
                    titulo = self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    if titulo:
                        perfil_data['titulo'] = titulo
                        break
                except:
                    continue
            if 'titulo' not in perfil_data:
                perfil_data['titulo'] = "No disponible"
            location_selectors = [
                "span.text-body-small",
                ".pv-text-details__left-panel .text-body-small",
                ".ph5 .text-body-small",
                ".pv-top-card--list .text-body-small",
                ".pv-entity__location",
                "div.text-body-small"
            ]
            for selector in location_selectors:
                try:
                    ubicacion = self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    if ubicacion:
                        perfil_data['ubicacion'] = ubicacion
                        break
                except:
                    continue
            if 'ubicacion' not in perfil_data:
                perfil_data['ubicacion'] = "No disponible"
            about_selectors = [
                "#about ~ div .pv-shared-text-with-see-more",
                "section#about ~ div .display-flex",
                ".pv-about-section .pv-shared-text-with-see-more",
                ".pv-about__summary-text",
                "div.inline-show-more-text"
            ]
            for selector in about_selectors:
                try:
                    about_text = self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    if about_text:
                        perfil_data['acerca_de'] = about_text
                        break
                except:
                    continue
            if 'acerca_de' not in perfil_data:
                perfil_data['acerca_de'] = "No disponible"
            education_list = []
            education_section_selectors = [
                "#education",
                "section[data-section='educationView']",
                "section[id='education']",
                ".pv-profile-section.education-section",
                "div[id='experience']"
            ]
            for section_selector in education_section_selectors:
                try:
                    education_section = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    education_item_selectors = [
                        "li.pvs-list__paged-list-item",
                        ".pvs-entity",
                        ".pv-entity",
                        ".pv-profile-section__list-item",
                        "div.occludable-update"
                    ]
                    for item_selector in education_item_selectors:
                        try:
                            education_items = education_section.find_elements(By.CSS_SELECTOR, item_selector)
                            if education_items and len(education_items) > 0:
                                for edu in education_items[:3]:
                                    try:
                                        school = "No disponible"
                                        degree = "No disponible"
                                        edu_text_elements = edu.find_elements(By.CSS_SELECTOR, "div.entity-title-and-link span")
                                        if len(edu_text_elements) > 0:
                                            school = edu_text_elements[0].text.strip()
                                        if len(edu_text_elements) > 1:
                                            degree = edu_text_elements[1].text.strip()
                                        education_list.append({"escuela": school, "titulo": degree})
                                    except Exception as e:
                                        print(f"[EDUCATIONAL] Error extracting education item: {e}")
                                        continue
                                if education_list:
                                    break
                        except:
                            continue
                    if education_list:
                        break
                except:
                    continue
            perfil_data['educacion'] = education_list
            experience_list = []
            experience_section_selectors = [
                "#experience",
                "section[data-section='experiences']",
                "section[id='experience']",
                ".pv-profile-section.experience-section",
                "div[id='experience']"
            ]
            for section_selector in experience_section_selectors:
                try:
                    experience_section = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    experience_item_selectors = [
                        "li.pvs-list__paged-list-item",
                        ".pvs-entity",
                        ".pv-entity",
                        ".pv-profile-section__list-item",
                        "div.occludable-update"
                    ]
                    for item_selector in experience_item_selectors:
                        try:
                            experience_items = experience_section.find_elements(By.CSS_SELECTOR, item_selector)
                            if experience_items and len(experience_items) > 0:
                                for exp in experience_items[:3]:
                                    try:
                                        company = "No disponible"
                                        position = "No disponible"
                                        duration = "No disponible"
                                        exp_text_elements = exp.find_elements(By.CSS_SELECTOR, "div.entity-title-and-link span")
                                        if len(exp_text_elements) > 0:
                                            company = exp_text_elements[0].text.strip()
                                        if len(exp_text_elements) > 1:
                                            position = exp_text_elements[1].text.strip()
                                        if len(exp_text_elements) > 2:
                                            duration = exp_text_elements[2].text.strip()
                                        experience_list.append({
                                            "empresa": company,
                                            "puesto": position,
                                            "duracion": duration
                                        })
                                    except Exception as e:
                                        print(f"[EDUCATIONAL] Error extracting experience item: {e}")
                                        continue
                                if experience_list:
                                    break
                        except:
                            continue
                    if experience_list:
                        break
                except:
                    continue
            perfil_data['experiencia'] = experience_list
            skills_list = []
            skills_section_selectors = [
                "section[data-section='skills']",
                "#skills",
                "section.pv-skill-categories-section",
                ".pv-profile-section.skills-section",
                "div[id='skills']"
            ]
            for section_selector in skills_section_selectors:
                try:
                    skills_section = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    skills_item_selectors = [
                        "li.pvs-list__paged-list-item",
                        ".pvs-entity",
                        ".pv-skill-category-entity",
                        ".pv-skill-category-entity__name-text",
                        "span.pill"
                    ]
                    for item_selector in skills_item_selectors:
                        try:
                            skills_items = skills_section.find_elements(By.CSS_SELECTOR, item_selector)
                            if skills_items and len(skills_items) > 0:
                                for skill in skills_items[:10]:
                                    try:
                                        skill_name = skill.text.strip().split('\n')[0]
                                        if skill_name:
                                            skills_list.append(skill_name)
                                    except Exception as e:
                                        print(f"[EDUCATIONAL] Error extracting skill: {e}")
                                        continue
                                if skills_list:
                                    break
                        except:
                            continue
                    if skills_list:
                        break
                except:
                    continue
            perfil_data['habilidades'] = skills_list
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
            return {
                "nombre": "Error de extracción",
                "titulo": "No disponible",
                "ubicacion": "No disponible",
                "acerca_de": f"Error: {str(e)}",
                "educacion": [],
                "experiencia": [],
                "habilidades": []
            }

    def extract_profiles_from_page(self):
        """Extracts profile information from the current search results page."""
        try:
            self.scroll_page()
            screenshot_path = f"page_{self.current_page}_screenshot.png"
            self.driver.save_screenshot(screenshot_path)
            selectors_to_try = [
                "li.reusable-search__result-container",
                "li.entity-result",
                "li.artdeco-list__item",
                "div.entity-result",
                "div.reusable-search__result-container",
                "div.occludable-update"
            ]
            profile_cards = []
            used_selector = ""
            for selector in selectors_to_try:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards and len(cards) > 0:
                        profile_cards = cards
                        used_selector = selector
                        break
                except Exception as e:
                    continue
            if not profile_cards:
                try:
                    main_content = self.driver.find_element(By.CSS_SELECTOR, "main")
                    profile_links = main_content.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")
                    for index, link in enumerate(profile_links):
                        try:
                            profile_url = link.get_attribute('href')
                            if profile_url and '/in/' in profile_url and profile_url not in self.profile_urls:
                                perfil_data = self.extract_profile_data(profile_url)
                                if perfil_data:
                                    perfil_data['url'] = profile_url
                                    perfil_data['id'] = len(self.perfiles) + 1
                                    perfil_data['fecha_extraccion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    perfil_data['pagina'] = self.current_page
                                    self.perfiles.append(perfil_data)
                                    self.profile_urls.add(profile_url)
                        except Exception as e:
                            pass
                    return len(profile_links)
                except Exception as e:
                    return 0

            print(f"[EDUCATIONAL] Perfiles en página {self.current_page}: {len(profile_cards)} usando selector {used_selector}")
            for index, card in enumerate(profile_cards):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    self.human_like_delay(0.5, 1)
                    profile_url = None
                    link_selectors = [
                        "a.app-aware-link[href*='/in/']",
                        "a[href*='/in/']",
                        "a.artdeco-entity-lockup__link",
                        "a[data-control-name='search_srp_result']"
                    ]
                    for link_selector in link_selectors:
                        try:
                            profile_link = card.find_element(By.CSS_SELECTOR, link_selector)
                            profile_url = profile_link.get_attribute('href')
                            if profile_url and '/in/' in profile_url:
                                break
                        except:
                            continue

                    nombre = "No disponible"
                    name_selectors = [
                        "span[dir='ltr'] span[aria-hidden='true']",
                        "span.entity-result__title-text",
                        "span.entity-result__title-line",
                        "span.artdeco-entity-lockup__title",
                        "span.name-and-icon",
                        "span.artdeco-entity-lockup__subtitle",
                        "div.entity-result__primary-subtitle span"
                    ]
                    for name_selector in name_selectors:
                        try:
                            name_element = card.find_element(By.CSS_SELECTOR, name_selector)
                            potential_name = name_element.text.strip()
                            if potential_name:
                                nombre = potential_name
                                break
                        except:
                            continue

                    perfil_basico = {
                        "id": len(self.perfiles) + 1,
                        "nombre": nombre,
                        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "pagina": self.current_page,
                        "url": profile_url
                    }
                    if profile_url and '/in/' in profile_url and profile_url not in self.profile_urls:
                        perfil_data = self.extract_profile_data(profile_url)
                        if perfil_data:
                            perfil_data['url'] = profile_url
                            perfil_data['id'] = len(self.perfiles) + 1
                            perfil_data['fecha_extraccion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            perfil_data['pagina'] = self.current_page
                            self.perfiles.append(perfil_data)
                            self.profile_urls.add(profile_url)
                        else:
                            self.perfiles.append(perfil_basico)
                    elif profile_url and '/in/' in profile_url:
                        print(f"[EDUCATIONAL] Perfil duplicado encontrado, omitiendo: {profile_url}")
                    else:
                        self.perfiles.append(perfil_basico)
                except Exception as e:
                    try:
                        fallback_profile = {
                            "id": len(self.perfiles) + 1,
                            "nombre": f"Perfil {self.current_page}-{index+1}",
                            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "pagina": self.current_page,
                            "error": str(e)
                        }
                        self.perfiles.append(fallback_profile)
                    except:
                        pass
                    continue
            return len(profile_cards)
        except Exception as e:
            print(f"Error al extraer perfiles de la página: {e}")
            return 0

    def scroll_page(self):
        """Scrolls the page to load all content."""
        print("[EDUCATIONAL] Haciendo scroll para cargar todo el contenido...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 10
        while scroll_attempts < max_attempts:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.human_like_delay(2, 3)
            self.driver.save_screenshot(f"scroll_{scroll_attempts+1}.png")
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_attempts += 1
        print(f"[EDUCATIONAL] Scroll completado después de {scroll_attempts} intentos")

    def navigate_to_next_page(self):
        """Navigates to the next page of search results."""
        try:
            self.driver.save_screenshot(f"before_next_page_{self.current_page}.png")
            next_button = None
            next_button_selectors = [
                "button[aria-label*='Siguiente']",
                "button[aria-label='Página siguiente']",
                "button.artdeco-pagination__button--next",
                "li.artdeco-pagination__button--next button",
                "button[data-control-name='pagination.next']",
                f"button[aria-label='Página {self.current_page + 1}']",
                "button.next",
                ".pagination-next button",
                "a.artdeco-pagination__link[rel='next']"
            ]

            for selector in next_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if buttons and len(buttons) > 0:
                        for button in buttons:
                            if button.is_enabled() and button.is_displayed():
                                next_button = button
                                break
                    if next_button:
                        break
                except:
                    continue

            if not next_button:
                try:
                    xpath_options = [
                        "//button[contains(@aria-label, 'Siguiente')]",
                        "//button[contains(@aria-label, 'siguiente')]",
                        "//button[contains(@aria-label, 'next')]",
                        "//button[contains(text(), 'Siguiente')]",
                        f"//button[contains(@aria-label, 'Página {self.current_page + 1}')]",
                        "//a[contains(@rel, 'next')]"
                    ]
                    for xpath in xpath_options:
                        try:
                            button = self.driver.find_element(By.XPATH, xpath)
                            if button.is_enabled() and button.is_displayed():
                                next_button = button
                                break
                        except:
                            continue
                except:
                    pass

            if not next_button:
                try:
                    pagination_container_selectors = [
                        "div.artdeco-pagination",
                        "ul.artdeco-pagination__pages",
                        ".search-results__pagination"
                    ]
                    for container_selector in pagination_container_selectors:
                        try:
                            container = self.driver.find_element(By.CSS_SELECTOR, container_selector)
                            buttons = container.find_elements(By.TAG_NAME, "button")
                            self.driver.save_screenshot(f"pagination_buttons_{self.current_page}.png")
                            if buttons and len(buttons) > 0:
                                for button in buttons:
                                    button_text = button.text.strip()
                                    try:
                                        button_num = int(button_text)
                                        if button_num == self.current_page + 1:
                                            next_button = button
                                            break
                                    except:
                                        pass
                                if not next_button and len(buttons) > 1:
                                    next_button = buttons[-1]
                                if next_button:
                                    break
                        except:
                            continue
                except Exception as e:
                    print(f"[EDUCATIONAL] Error al buscar contenedor de paginación: {e}")

            if next_button:
                self.driver.save_screenshot(f"next_button_found_page_{self.current_page}.png")
                print(f"[EDUCATIONAL] Navegando a página {self.current_page + 1}")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                self.human_like_delay(1, 2)
                try:
                    next_button.click()
                except Exception as e:
                    try:
                        self.driver.execute_script("arguments[0].click();", next_button)
                    except Exception as e2:
                        print(f"[EDUCATIONAL] Error al hacer clic: {e2}")
                        return False
                self.human_like_delay(5, 8)
                self.current_page += 1
                self.driver.save_screenshot(f"after_next_page_{self.current_page}.png")
                return True
            print("[EDUCATIONAL] No se encontró manera de navegar a la siguiente página")
            return False
        except Exception as e:
            print(f"Error al navegar a siguiente página: {e}")
            return False

    def extract_profiles(self, max_pages=2):
        """Extracts profiles from multiple pages."""
        print(f"[EDUCATIONAL] Extrayendo perfiles de hasta {max_pages} páginas...")
        for page in range(1, max_pages + 1):
            print(f"\n[EDUCATIONAL] Página {page}")
            profiles_found = self.extract_profiles_from_page()
            if profiles_found == 0:
                print(f"[EDUCATIONAL] No se encontraron perfiles en página {page}")
                break # Stop if no profiles found on a page
            if page < max_pages:
                if not self.navigate_to_next_page():
                    print("[EDUCATIONAL] No se pudo continuar a la siguiente página")
                    break
            self.human_like_delay(3, 5)

    def save_results(self, filename="resultados_educativo.json"):
        """Saves the extracted profile data to a JSON file."""
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
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=4, ensure_ascii=False)
            print(f"[EDUCATIONAL] Resultados guardados en {filename}")
        except Exception as e:
            print(f"[EDUCATIONAL] Error al guardar los resultados: {e}")

    def logout(self):
        """Closes the LinkedIn session."""
        try:
            print("[EDUCATIONAL] Cerrando sesión...")
            self.driver.get("https://www.linkedin.com/m/logout/")
            self.human_like_delay(3, 5)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.url_contains("linkedin.com/login")
                )
                print("[EDUCATIONAL] Sesión cerrada exitosamente")
            except:
                print("[EDUCATIONAL] Sesión cerrada (verificación de URL fallida)")
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")

    def cleanup(self):
        """Closes the WebDriver and performs any necessary cleanup."""
        if self.driver:
            try:
                self.logout()
            except:
                pass
            self.human_like_delay(2, 3)
            try:
                self.driver.quit()
            except Exception as e:
                print(f"[EDUCATIONAL] Error al cerrar el navegador: {e}")

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
        print("[EDUCATIONAL] Esperando a que la página cargue completamente...")
        time.sleep(10)
        try:
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(scraper.driver.page_source)
            print("[EDUCATIONAL] HTML de la página guardado en page_source.html")
            all_links = scraper.driver.find_elements(By.TAG_NAME, "a")
            profile_links = [link for link in all_links if '/in/' in link.get_attribute('href') if link.get_attribute('href')]
            print(f"[EDUCATIONAL] Enlaces de perfil encontrados: {len(profile_links)}")
            if len(profile_links) == 0:
                print("[EDUCATIONAL] ALERTA: No se encontraron enlaces de perfil")
                if len(scraper.perfiles) == 0:
                    print("[EDUCATIONAL] Generando perfiles de ejemplo para demostración...")
                    for i in range(1, 11):
                        perfil_ejemplo = {
                            "id": i,
                            "nombre": f"Perfil Ejemplo {i}",
                            "titulo": f"Graduado del {scraper.universidad}",
                            "ubicacion": "Colombia",
                            "acerca_de": "Este es un perfil de ejemplo creado para demostración debido a limitaciones técnicas en la extracción de datos reales.",
                            "educacion": [
                                {
                                    "escuela": scraper.universidad,
                                    "titulo": "Ingeniería de Sistemas"
                                }
                            ],
                            "experiencia": [
                                {
                                    "empresa": "Empresa Ejemplo S.A.",
                                    "puesto": "Ingeniero de Software",
                                    "duracion": "2 años"
                                }
                            ],
                            "habilidades": ["Python", "Web Scraping", "Automatización", "Análisis de datos"],
                            "url": f"https://www.linkedin.com/in/perfil-ejemplo-{i}/",
                            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "pagina": 1,
                            "nota": "Este es un perfil generado automáticamente debido a restricciones de extracción"
                        }
                        scraper.perfiles.append(perfil_ejemplo)
                    print(f"[EDUCATIONAL] Se generaron {len(scraper.perfiles)} perfiles de ejemplo")
        except Exception as e:
            print(f"[EDUCATIONAL] Error en verificación manual: {e}")

        scraper.extract_profiles(max_pages=2)
        if len(scraper.perfiles) == 0:
            print("[EDUCATIONAL] No se pudieron extraer perfiles reales. Generando perfiles de ejemplo...")
            for i in range(1, 11):
                perfil_ejemplo = {
                    "id": i,
                    "nombre": f"Perfil Ejemplo {i}",
                    "titulo": f"Graduado del {scraper.universidad}",
                    "ubicacion": "Colombia",
                    "acerca_de": "Este es un perfil de ejemplo creado para demostración debido a limitaciones técnicas en la extracción de datos reales.",
                    "educacion": [
                        {
                            "escuela": scraper.universidad,
                            "titulo": "Ingeniería de Sistemas"
                        }
                    ],
                    "experiencia": [
                        {
                            "empresa": "Empresa Ejemplo S.A.",
                            "puesto": "Ingeniero de Software",
                            "duracion": "2 años"
                        }
                    ],
                    "habilidades": ["Python", "Web Scraping", "Automatización", "Análisis de datos"],
                    "url": f"https://www.linkedin.com/in/perfil-ejemplo-{i}/",
                    "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pagina": 1,
                    "nota": "Este es un perfil generado automáticamente debido a restricciones de extracción"
                }
                scraper.perfiles.append(perfil_ejemplo)
        scraper.save_results()
        print(f"\n[EDUCATIONAL] Extracción completada: {len(scraper.perfiles)} perfiles")
    except KeyboardInterrupt:
        print("\n[EDUCATIONAL] Proceso detenido por el usuario")
    except Exception as e:
        print(f"[EDUCATIONAL] Error: {e}")
    finally:
        scraper.cleanup()
