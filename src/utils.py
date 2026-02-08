"""
YARDIMCI FONKSİYONLAR
Küçük yardımcı işleri burada yapıyoruz
"""

from colorama import Fore, Style, init

# Colorama'yı başlat (renkli yazı için)
init(autoreset=True)

class Colors:
    """Renkli yazı için kodlar"""
    USER = Fore.CYAN
    AI = Fore.GREEN
    ERROR = Fore.RED
    INFO = Fore.YELLOW
    RESET = Style.RESET_ALL


def print_user(message):
    """Kullanıcı mesajını renkli yazdırır"""
    print(f"\n{Colors.USER}👤 Sen: {Colors.RESET}{message}")


def print_ai(message):
    """AI cevabını renkli yazdırır"""
    print(f"\n{Colors.AI}🤖 Nova: {Colors.RESET}{message}")


def print_error(message):
    """Hata mesajını renkli yazdırır"""
    print(f"\n{Colors.ERROR}❌ {message}{Colors.RESET}")


def print_info(message):
    """Bilgi mesajını renkli yazdırır"""
    print(f"\n{Colors.INFO}💡 {message}{Colors.RESET}")


def get_user_input():
    """Kullanıcıdan input alır"""
    try:
        user_input = input(f"\n{Colors.USER}👤 Sen: {Colors.RESET}").strip()
        return user_input
    except KeyboardInterrupt:
        return "çıkış"
    except EOFError:
        return "çıkış"


def clear_screen():
    """Ekranı temizler (opsiyonel)"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')