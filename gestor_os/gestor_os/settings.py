from pathlib import Path

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# CONFIGURAÇÕES BÁSICAS
# ==============================

SECRET_KEY = "django-insecure-^r@d3k=#@s(9l&zt*^tzbp_03^n!l^hgm)1vbv@oo!hyn^@te!"

DEBUG = True  # Altera para False em Produção

ALLOWED_HOSTS = ["localhost", "127.0.0.1"] 

# ALLOWED_HOSTS = ["localhost", "127.0.0.1", "seu-projeto.onrender.com"]

# ==============================
# APLICAÇÕES INSTALADAS
# ==============================

INSTALLED_APPS = [
    # Apps padrão do Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cadastro",
    "lancamento",
]

# ==============================
# MIDDLEWARE
# ==============================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==============================
# CONFIGURAÇÃO DE URL E WSGI
# ==============================

ROOT_URLCONF = "gestor_os.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Caminho para pastas de templates globais (ex: BASE_DIR / 'templates')
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "gestor_os.wsgi.application"

# ==============================
# BANCO DE DADOS
# ==============================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ==============================
# VALIDAÇÃO DE SENHAS
# ==============================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==============================
# LOCALIZAÇÃO E IDIOMA
# ==============================

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True
USE_TZ = True

# ==============================
# ARQUIVOS ESTÁTICOS
# ==============================

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ==============================
# OUTRAS CONFIGURAÇÕES
# ==============================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Corrige erro de CSRF ao usar localhost
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "https://localhost:8000",
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
]
