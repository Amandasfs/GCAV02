# screens_app/styles.py
class AppStyles:
    # Cores
    PRIMARY_COLOR = '#667eea'
    SECONDARY_COLOR = '#2c3e50'
    SUCCESS_COLOR = '#27ae60'
    WARNING_COLOR = '#f39c12'
    DANGER_COLOR = '#e74c3c'
    INFO_COLOR = '#3498db'
    LIGHT_BG = '#f8f9fa'
    WHITE = 'white'
    
    # Fontes
    TITLE_FONT = ('Arial', 24, 'bold')
    SUBTITLE_FONT = ('Arial', 12)
    HEADER_FONT = ('Arial', 18, 'bold')
    NORMAL_FONT = ('Arial', 10)
    SMALL_FONT = ('Arial', 9)
    
    @staticmethod
    def get_button_style(bg_color, font_size=10):
        return {
            'font': ('Arial', font_size, 'bold'),
            'fg': 'white',
            'bg': bg_color,
            'relief': 'flat',
            'bd': 0
        }