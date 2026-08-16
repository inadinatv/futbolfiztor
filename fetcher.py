import json
import urllib.request
import xml.etree.ElementTree as ET
import os

# BURAYA RAPIDAPI'DEN ALDIĞIN ANAHTARI GİRMELİSİN
API_KEY = "BURAYA_KENDI_RAPIDAPI_ANAHTARINI_YAZ"
LEAGUE_ID = "203" # Türkiye Süper Lig Kimliği
SEASON = "2026"   # Güncel Sezon

def get_standings():
    url = f"https://api-football-v1.p.rapidapi.com/v3/standings?season={SEASON}&league={LEAGUE_ID}"
    req = urllib.request.Request(url)
    req.add_header("x-rapidapi-key", API_KEY)
    req.add_header("x-rapidapi-host", "api-football-v1.p.rapidapi.com")
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            standings_data = data['response'][0]['league']['standings'][0]
            
            standings = []
            for team in standings_data:
                standings.append({
                    "pos": team['rank'],
                    "team": team['team']['name'],
                    "logo": team['team']['logo'],
                    "p": team['all']['played'],
                    "w": team['all']['win'],
                    "d": team['all']['draw'],
                    "l": team['all']['lose'],
                    "pts": team['points']
                })
            return standings
    except Exception as e:
        print("Puan durumu çekilemedi (API Key hatalı veya limit dolmuş olabilir):", e)
        return []

def get_analysis():
    # Güvenilir Kaynak: Profesyonel analizler ve özetler için RSS entegrasyonu
    rss_url = "https://www.trtspor.com.tr/rss/futbol.xml"
    news = []
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Son 12 analizi/haberi alalım
            for item in root.findall('./channel/item')[:12]:
                title = item.find('title').text
                link = item.find('link').text
                desc = item.find('description').text if item.find('description') is not None else ""
                
                # Görsel çekme işlemi
                img_url = ""
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    img_url = enclosure.get('url')
                    
                # İçeriği temizleyip kırpalım
                clean_desc = desc[:130] + "..." if len(desc) > 130 else desc
                
                news.append({
                    "title": title,
                    "desc": clean_desc,
                    "link": link,
                    "img": img_url
                })
    except Exception as e:
        print("Analizler çekilirken hata oluştu:", e)
        
    return news

def main():
    print("Sistem çalışıyor, veriler toplanıyor...")
    
    standings = get_standings()
    analysis = get_analysis()
    
    # API key girilmemişse veya hata varsa placeholder veri
    if not standings:
        standings = [
            {"pos": 1, "team": "Lütfen API Anahtarınızı Girin", "logo": "", "p": 0, "w": 0, "d": 0, "l": 0, "pts": 0}
        ]
        
    output_data = {
        "standings": standings,
        "analysis": analysis
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print("data.json başarıyla güncellendi!")

if __name__ == "__main__":
    main()
