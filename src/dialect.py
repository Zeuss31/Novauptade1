"""
ŞİVE ÇEVİRİCİ SİSTEMİ
Karadeniz ve Ege şivelerini uygular
"""

import re

class DialectConverter:
    """Şive çevirme işlemlerini yönetir"""
    
    @staticmethod
    def convert(text, dialect='normal'):
        """
        Metni belirtilen şiveye çevir
        
        Args:
            text (str): Çevrilecek metin
            dialect (str): 'normal', 'karadeniz', 'ege'
            
        Returns:
            str: Şiveye çevrilmiş metin
        """
        if dialect == 'karadeniz':
            return DialectConverter.to_karadeniz(text)
        elif dialect == 'ege':
            return DialectConverter.to_ege(text)
        else:
            return text
    
    @staticmethod
    def to_karadeniz(text):
        """
        Karadeniz şivesine çevir
        
        Özellikler:
        - "ne yapıyorsun" → "ne yapaan"
        - "nasılsın" → "nasılsan"
        - "çok" → "pek"
        - "oğlum", "valla", "yahu" eklemeleri
        """
        
        # Kelime çevirimleri (önce uzun kelimeleri)
        replacements = {
            # Soru kalıpları
            'ne yapıyorsun': 'ne yapaan',
            'ne yapıyorsunuz': 'ne yapaanız',
            'nasılsın': 'nasılsan',
            'nasılsınız': 'nasılsanız',
            'nerelisin': 'nerelisan',
            'nereden geliyorsun': 'nerden gelaan',
            'nereye gidiyorsun': 'nereye gidaan',
            'ne iş yapıyorsun': 'ne iş yapaan',
            
            # Fiil çevirimleri (-yor → -aan/-ään)
            'yapıyorum': 'yapaam',
            'yapıyorsun': 'yapaan',
            'yapıyor': 'yapaa',
            'yapıyoruz': 'yapaaz',
            'yapıyorsunuz': 'yapaanız',
            'yapıyorlar': 'yapaalar',
            
            'gidiyorum': 'gidaam',
            'gidiyorsun': 'gidaan',
            'gidiyor': 'gidaa',
            
            'geliyorum': 'gelaam',
            'geliyorsun': 'gelaan',
            'geliyor': 'gelaa',
            
            'biliyorum': 'bilaam',
            'biliyorsun': 'bilaan',
            'biliyor': 'bilaa',
            
            'görüyorum': 'göraam',
            'görüyorsun': 'göraan',
            'görüyor': 'göraa',
            
            'anlıyorum': 'anlaam',
            'anlıyorsun': 'anlaan',
            'anlıyor': 'anlaa',
            
            'istiyorum': 'istaam',
            'istiyorsun': 'istaan',
            'istiyor': 'istaa',
            
            'oluyor': 'olaa',
            'olurum': 'oluram',
            
            # Yaygın kelimeler
            'çok': 'pek',
            'çok iyi': 'pek iyi',
            'çok güzel': 'pek güzel',
            'tamam': 'tamamdır',
            'evet': 'hee',
            'hayır': 'yok',
            'değil': 'yok',
            'ben': 'ben valla',
            'benim': 'benim',
            'var': 'var valla',
            'yok': 'yok valla',
            'gerçekten': 'harbiden',
            'çünkü': 'çünki',
            'ama': 'amma',
            'için': 'için valla',
            
            # Olumsuz fiiller
            'yapma': 'yapma haa',
            'gitme': 'gitme haa',
            'gelme': 'gelme haa',
            
            # Sıfatlar
            'güzel': 'güzel valla',
            'kötü': 'kötü valla',
            'iyi': 'iyi valla',
        }
        
        # Metni küçük harfe çevir, çevir, sonra orijinal case'i koru
        result = text
        for old, new in replacements.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(old), re.IGNORECASE)
            result = pattern.sub(new, result)
        
        # Cümle sonuna ek ifadeler
        sentences = result.split('.')
        enhanced_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                # %30 ihtimalle cümle sonuna "oğlum", "yahu" ekle
                import random
                if random.random() < 0.3 and not sentence.endswith('oğlum') and not sentence.endswith('yahu'):
                    extras = [' oğlum', ' yahu', ' valla']
                    sentence += random.choice(extras)
                enhanced_sentences.append(sentence)
        
        result = '. '.join(enhanced_sentences)
        
        # Regex ile kalan -yor/-ıyor/-iyor/-uyor/-üyor kalıplarını değiştir
        result = re.sub(r'(\w+)(ıyor|iyor|uyor|üyor)', r'\1aa', result)
        
        return result
    
    @staticmethod
    def to_ege(text):
        """
        Ege şivesine çevir
        
        Özellikler:
        - "nasılsın" → "nasılsan"
        - "ne yapıyorsun" → "ne yapıyon"
        - "çok" → "baya"
        - "yaa", "be", "abi" eklemeleri
        """
        
        # Kelime çevirimleri
        replacements = {
            # Soru kalıpları
            'ne yapıyorsun': 'ne yapıyon',
            'ne yapıyorsunuz': 'ne yapıyonuz',
            'nasılsın': 'nasılsan',
            'nasılsınız': 'nasılsanız',
            'nerelisin': 'nerelisan',
            'nereden geliyorsun': 'nerden geliyon',
            'nereye gidiyorsun': 'nereye gidiyon',
            'ne iş yapıyorsun': 'ne iş yapıyon',
            
            # Fiil çevirimleri (-yor → -yon/-yom)
            'yapıyorum': 'yapıyom',
            'yapıyorsun': 'yapıyon',
            'yapıyor': 'yapıyo',
            'yapıyoruz': 'yapıyoz',
            'yapıyorsunuz': 'yapıyonuz',
            'yapıyorlar': 'yapıyolar',
            
            'gidiyorum': 'gidiyom',
            'gidiyorsun': 'gidiyon',
            'gidiyor': 'gidiyo',
            
            'geliyorum': 'geliyom',
            'geliyorsun': 'geliyon',
            'geliyor': 'geliyo',
            
            'biliyorum': 'biliyom',
            'biliyorsun': 'biliyon',
            'biliyor': 'biliyo',
            
            'görüyorum': 'görüyom',
            'görüyorsun': 'görüyon',
            'görüyor': 'görüyo',
            
            'anlıyorum': 'anlıyom',
            'anlıyorsun': 'anlıyon',
            'anlıyor': 'anlıyo',
            
            'istiyorum': 'istiyom',
            'istiyorsun': 'istiyon',
            'istiyor': 'istiyo',
            
            'oluyor': 'oluyo',
            
            # Yaygın kelimeler
            'çok': 'baya',
            'çok iyi': 'baya iyi',
            'çok güzel': 'baya güzel',
            'tamam': 'tamam be',
            'evet': 'he',
            'hayır': 'yok be',
            'değil': 'değil ya',
            'gerçekten': 'harbiden',
            'neden': 'niye',
            'çünkü': 'çünkü',
            'ama': 'ama',
            'için': 'için',
            'var': 'var ya',
            'yok': 'yok ki',
            
            # Olumsuz fiiller
            'yapma': 'yapma ya',
            'gitme': 'gitme be',
            'gelme': 'gelme ya',
            
            # Sıfatlar
            'güzel': 'güzel ya',
            'kötü': 'kötü be',
            'iyi': 'iyi be',
        }
        
        # Metni çevir
        result = text
        for old, new in replacements.items():
            pattern = re.compile(re.escape(old), re.IGNORECASE)
            result = pattern.sub(new, result)
        
        # Cümle sonuna ek ifadeler
        sentences = result.split('.')
        enhanced_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                # %25 ihtimalle cümle sonuna "yaa", "be" ekle
                import random
                if random.random() < 0.25 and not sentence.endswith('yaa') and not sentence.endswith('be'):
                    extras = [' yaa', ' be', ' abi']
                    sentence += random.choice(extras)
                enhanced_sentences.append(sentence)
        
        result = '. '.join(enhanced_sentences)
        
        # Regex ile kalan -yor kalıplarını değiştir
        result = re.sub(r'(\w+)(ıyor|iyor|uyor|üyor)um\b', r'\1ıyom', result)
        result = re.sub(r'(\w+)(ıyor|iyor|uyor|üyor)sun\b', r'\1ıyon', result)
        result = re.sub(r'(\w+)(ıyor|iyor|uyor|üyor)\b', r'\1ıyo', result)
        
        return result


# Test fonksiyonu
if __name__ == "__main__":
    test_text = "Merhaba! Nasılsın? Bugün ne yapıyorsun? Çok güzel bir gün. Ben kod yazıyorum."
    
    print("Normal:")
    print(test_text)
    print("\nKaradeniz:")
    print(DialectConverter.convert(test_text, 'karadeniz'))
    print("\nEge:")
    print(DialectConverter.convert(test_text, 'ege'))