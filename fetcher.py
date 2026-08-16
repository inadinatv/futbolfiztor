import json
import urllib.request
import xml.etree.ElementTree as ET

# Senin RapidAPI Anahtarın buraya eklendi
API_KEY = "23f9a5f274msh45ab2adf1d7eaf9p1648fcjsne1a9747e08f8"
LEAGUE_ID = "203" # Türkiye Süper Lig Kimliği
SEASON = "2026"   # Güncel Sezon (Bulunduğumuz yıl)

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
        print("Puan durumu çekilemedi:", e)
        return []

def get_analysis():
    # TRT Spor RSS üzerinden analizler ve haberler
    rss_url = "https://www.trtspor.com.tr/rss/futbol.xml"
    news = []
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall('./channel/item')[:12]:
                title = item.find('title').text
                link = item.find('link').text
                desc = item.find('description').text if item.find('description') is not None else ""
                
                img_url = ""
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    img_url = enclosure.get('url')
                    
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
    
    if not standings:
        standings = [
            {"pos": 1, "team": "Veri Bekleniyor", "logo": "", "p": 0, "w": 0, "d": 0, "l": 0, "pts": 0}
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
