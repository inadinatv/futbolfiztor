import json
import urllib.request
import re

def get_league_data():
    # Public API üzerinden Türkiye Süper Lig Puan Durumu ve Fikstürü
    url = "https://api.open-ligadb.de/getbltable/tr1/2025" 
    # Alternatif doğrudan JSON simülasyon/yedek veri yapısı
    try:
        req = urllib.request.Request(
            "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/tr.1.json",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Lig verisi çekilirken hata: {e}")
        return {}

def get_youtube_highlights():
    # Bein Sports veya resmi kanallardan özet Arama Motoru İntegresi
    query = urllib.parse.quote("Trendyol Süper Lig Maç Özetleri")
    url = f"https://www.youtube.com/results?search_query={query}"
    
    highlights = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode()
            # YouTube video ID'lerini regex ile yakalama
            video_ids = re.findall(r"watch\?v=(\S{11})", html)
            unique_ids = list(dict.fromkeys(video_ids))[:6] # Son 6 özet
            
            for vid in unique_ids:
                highlights.append({
                    "id": vid,
                    "embed": f"https://www.youtube.com/embed/{vid}"
                })
    except Exception as e:
        print(f"Video özetleri çekilemedi: {e}")
        
    return highlights

def main():
    print("Veriler toplanıyor...")
    highlights = get_youtube_highlights()
    
    # Varsayılan dinamik puan durumu yapısı
    standings = [
        {"pos": 1, "team": "Galatasaray", "p": 0, "w": 0, "d": 0, "l": 0, "pts": 0},
        {"pos": 2, "team": "Fenerbahçe", "p": 0, "w": 0, "d": 0, "l": 0, "pts": 0},
        {"pos": 3, "team": "Beşiktaş", "p": 0, "w": 0, "d": 0, "l": 0, "pts": 0},
        {"pos": 4, "team": "Trabzonspor", "p": 0, "w": 0, "d": 0, "l": 0, "pts": 0},
    ]

    output_data = {
        "highlights": highlights,
        "standings": standings,
        "last_update": urllib.parse.quote("")
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print("data.json başarıyla oluşturuldu!")

if __name__ == "__main__":
    main()
