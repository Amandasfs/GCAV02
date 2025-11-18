"""
Configurações do sistema GCA
"""

# Configurações da API
API_CONFIG = {
    'base_url': 'http://localhost:5000',
    'credentials': ('admin', 'password'),
    'timeout': 30
}

# Configurações da interface
UI_CONFIG = {
    'window_title': 'GCA - Sistema de Gerenciamento',
    'window_size': '1200x800',
    'theme_colors': {
        'primary': '#2c3e50',
        'secondary': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'light': '#ecf0f1',
        'dark': '#34495e'
    }
}

# Configurações de autenticação
AUTH_CONFIG = {
    'admin_users': {
        'admin': 'admin123',
        'supervisor': 'super123'
    }
}