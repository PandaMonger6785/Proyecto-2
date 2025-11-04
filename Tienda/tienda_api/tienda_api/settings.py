from pathlib import Path

# Raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad / debug
SECRET_KEY = 'django-insecure-pon-aqui-tu-clave'
DEBUG = True
ALLOWED_HOSTS = []  # añade dominios/ips si lo expones fuera de localhost

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',  # DRF
    'tienda',          # tu app
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tienda_api.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Además de APP_DIRS, usa "frontend" si guardas html ahí
        'DIRS': [BASE_DIR / "frontend"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tienda_api.wsgi.application'

# ---------- Base de datos MySQL (XAMPP) ----------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tienda_db',
        'USER': 'Admin',
        'PASSWORD': 'Panda15w6',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Localización
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = False

# ---------- Archivos estáticos ----------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "tienda" / "static",
    BASE_DIR / "frontend",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------- Archivos de usuario (MEDIA) ----------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------- Sesión (requisito de 60 s de inactividad) ----------
SESSION_COOKIE_AGE = 60                 # 60 s
SESSION_SAVE_EVERY_REQUEST = True       # renueva si hay actividad

# ---------- Auth redirects (si aún no los tienes) ----------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
