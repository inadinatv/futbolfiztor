import json
import urllib.request
import re
from datetime import datetime
from typing import Optional


def clean_html(text: str) -> str:
    """HTML etiketlerini temizler."""
    return re.sub(r'<[^>]+>', '', text).replace('&nbsp;', '').strip()


def get_tff_standings() -> Optional[list]:
    """TFF web sitesinden Süper Lig puan durumunu çeker."""
    url = "https://www.tff.org/default.aspx?pageID=198"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        # Tüm tabloları bul
        tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        
        for table in tables:
            # Puan durumu tablosunu bul (Takım ve Puan kelimelerini içerir)
            if 'Takım' in table and 'Puan' in table:
                standings = []
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL | re.IGNORECASE)
                
                for row in rows:
                    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
                    
                    if len(cells) >= 8:
                        cleaned = [clean_html(td) for td in cells]
                        
                        # Sıra numarası rakam olan satırları al
                        if cleaned[0].isdigit():
                            standings.append({
                                "pos": cleaned[0],
                                "team": cleaned[1],
                                "played": cleaned[2],
                                "won": cleaned[3],
                                "drawn": cleaned[4],
                                "lost": cleaned[5],
                                "points": cleaned[-1]
                            })
                
                return standings
                
    except Exception as error:
        print(f"TFF bağlantı hatası: {error}")
    
    return None


def create_fallback_standings() -> list:
    """API erişilemezse kullanılacak yedek veriler."""
    return [
        {"pos": "1", "team": "Galatasaray A.Ş.", "played": "0", "won": "0", "drawn": "0", "lost": "0", "points": "0"},
        {"pos": "2", "team": "Fenerbahçe A.Ş.", "played": "0", "won": "0", "drawn": "0", "lost": "0", "points": "0"},
        {"pos": "3", "team": "Beşiktaş A.Ş.", "played": "0", "won": "0", "drawn": "0", "lost": "0", "points": "0"},
        {"pos": "4", "team": "Trabzonspor A.Ş.", "played": "0", "won": "0", "drawn": "0", "lost": "0", "points": "0"}
    ]


def create_analysis(status: str) -> list:
    """Analiz bölümü için veri oluşturur."""
    return [
        {
            "title": "Sistem Bağlantı Durumu",
            "desc": f"Bot aktif olarak çalışıyor. Durum: {status}. Veri akışı sorunsuz sağlandığında maç analizleri burada listelenecektir.",
            "link": "#",
            "img": ""
        }
    ]


def save_data(data: dict, filename: str = "data.json") -> None:
    """Veriyi JSON dosyasına kaydeder."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"{filename} başarıyla oluşturuldu!")


def main():
    """Ana fonksiyon."""
    standings = get_tff_standings()
    
    if not standings:
        standings = create_fallback_standings()
        status = "🔴 TFF Bağlantısı Gecikti (Geçici Yedek Veriler Gösteriliyor)"
    else:
        status = "🟢 Veriler TFF'den Başarıyla Çekildi"

    data = {
        "standings": standings,
        "analysis": create_analysis(status),
        "last_update": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }

    save_data(data)


if __name__ == "__main__":
    main()
