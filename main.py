"""
ANA PROGRAM
Tüm parçaları burada bir araya getiriyoruz
"""

from config.settings import check_settings
from src.personality import Personality
from src.conversation import ConversationManager
from src.api_handler import GroqAPIHandler
from src.utils import (
    print_user, print_ai, print_error, 
    print_info, get_user_input
)

def main():
    """Ana fonksiyon - program buradan başlar"""
    
    # 1. Ayarları kontrol et
    if not check_settings():
        return
    
    # 2. Karşılama mesajını göster
    print(Personality.get_welcome_message())
    
    # 3. Gerekli sınıfları oluştur
    conversation = ConversationManager()
    api = GroqAPIHandler()
    
    # 4. Ana döngü - sohbet buradan dönüyor
    while True:
        # Kullanıcıdan input al
        user_message = get_user_input()
        
        # Boş mesaj kontrolü
        if not user_message:
            continue
        
        # Çıkış kontrolü
        if user_message.lower() in ['çıkış', 'exit', 'quit', 'q']:
            print(Personality.get_goodbye_message())
            break
        
        # Özel komutlar
        if user_message.lower() == 'temizle':
            conversation.clear()
            print_info("Sohbet geçmişi temizlendi!")
            continue
        
        if user_message.lower() == 'yardım':
            print_info("""
Komutlar:
- çıkış: Programdan çık
- temizle: Sohbet geçmişini temizle
- yardım: Bu mesajı göster
            """)
            continue
        
        # Kullanıcı mesajını sohbet geçmişine ekle
        conversation.add_user_message(user_message)
        
        # API'den cevap al
        print(f"\n🤖 Nova: ", end="", flush=True)
        
        # Streaming yanıt al (kelime kelime)
        full_response = ""
        try:
            for chunk in api.get_streaming_response(conversation.get_messages()):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()  # Yeni satır
            
            # AI cevabını geçmişe ekle
            conversation.add_assistant_message(full_response)
            
        except Exception as e:
            print_error(f"Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    main()