# LinkedIn Educational Scraper

## Descripción
Este proyecto es una herramienta educativa para el estudio de técnicas de web scraping en el contexto de ciberseguridad. Permite extraer información de perfiles de egresados de universidades específicas en LinkedIn, con fines de investigación y aprendizaje en entornos controlados.

## Advertencia
**IMPORTANTE**: Esta herramienta debe ser utilizada EXCLUSIVAMENTE con fines educativos en entornos controlados. El uso de scraping en LinkedIn puede violar sus términos de servicio. El autor no se hace responsable por el mal uso de esta herramienta o por las consecuencias de violar los términos de servicio de LinkedIn.

## Características
- Login automático a LinkedIn con simulación de comportamiento humano
- Búsqueda de perfiles por universidad específica
- Extracción detallada de perfiles incluyendo:
  - Nombre completo
  - Título profesional
  - Ubicación
  - Educación
  - Experiencia laboral
  - Habilidades
- Navegación en múltiples páginas de resultados
- Cierre de sesión seguro
- Guardado de resultados en formato JSON

## Requisitos
- Python 3.13.3
- Navegador Chrome
- Conexión a Internet
- Cuenta de LinkedIn (se recomienda una cuenta de prueba)

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/linkedin-educational-scraper.git
cd linkedin-educational-scraper
```

### 2. Crear un entorno virtual
```bash
python -m venv venv

# Activar el entorno virtual en Windows
venv\Scripts\activate

# Activar el entorno virtual en macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install selenium==4.15.2
pip install webdriver-manager==4.0.1
pip install python-dotenv==1.0.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
```

### 4. Configurar credenciales
Crea un archivo `.env` en el directorio raíz con el siguiente contenido:
```
LINKEDIN_EMAIL=tu_email_de_linkedin
LINKEDIN_PASSWORD=tu_password_de_linkedin
UNIVERSIDAD=Universidad de Antioquia
```

## Uso
```bash
python linkedin_auto_scraper.py
```

El script:
1. Iniciará sesión en LinkedIn
2. Buscará perfiles de egresados de la universidad especificada
3. Navegará por hasta 10 páginas de resultados
4. Extraerá información detallada de cada perfil
5. Guardará los resultados en `resultados_educativo.json`
6. Cerrará sesión y finalizará

## Personalización
- Para cambiar la universidad a buscar, modifica la variable `UNIVERSIDAD` en el archivo `.env`
- Para ajustar el número de páginas a recorrer, modifica el parámetro `max_pages` en la llamada a `extract_profiles()`
- Para cambiar el nombre del archivo de resultados, modifica el parámetro `filename` en la llamada a `save_results()`

## Limitaciones conocidas
- LinkedIn puede detectar actividad automatizada y solicitar verificaciones CAPTCHA
- Los selectores CSS pueden cambiar si LinkedIn actualiza su interfaz
- LinkedIn limita el número de perfiles que se pueden ver en un período de tiempo

## Consideraciones éticas
- No almacene ni distribuya datos personales extraídos
- Respete la privacidad de los usuarios
- Utilice siempre la herramienta con fines educativos
- No sobrecargue los servidores de LinkedIn
- Implemente retrasos aleatorios entre solicitudes

## Estructura del proyecto
```
linkedin-educational-scraper/
├── linkedin_auto_scraper.py  # Script principal
├── .env                      # Archivo de credenciales (no incluido en el repositorio)
├── resultados_educativo.json # Archivo de resultados (generado por el script)
├── README.md                 # Este archivo
└── .gitignore                # Configuración de Git para ignorar archivos sensibles
```

## Contribución
Las contribuciones son bienvenidas. Si encuentras un problema o tienes una mejora, por favor:
1. Crea un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Realiza tus cambios y haz commit (`git commit -m 'Añade nueva característica'`)
4. Sube tus cambios (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Licencia
Este proyecto se distribuye bajo la licencia MIT. Ver `LICENSE` para más información.

## Disclaimer
Este proyecto fue creado con propósitos educativos en el marco de un curso de ciberseguridad. El autor no se hace responsable por el mal uso de la herramienta o por las consecuencias legales de violar los términos de servicio de LinkedIn u otras plataformas.