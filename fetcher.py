import json
import urllib.request
import xml.etree.ElementTree as ET
import re

def get_standings():
    # Bot koruması OLMAYAN en güvenilir kaynak: Türkiye Futbol Federasyonu (TFF) Ana Sayfası
    url = "https://www.tff.org/default.aspx?pageID=198"
    standings = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # HTML içindeki tüm tabloları bul ve içinde 'Takım' ve 'Puan' kelimeleri olanı seç
        tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        for table in tables:
            if 'Takım' in table and 'Puan' in table:
                trs = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL | re.IGNORECASE)
                for tr in trs:
                    tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL | re.IGNORECASE)
                    if len(tds) >= 8:
                        # İçindeki gereksiz HTML etiketlerini ve boşlukları temizle
                        clean_tds = [re.sub(r'<[^>]+>', '', td).replace('&nbsp;', '').strip() for td in tds]
                        
                        pos = clean_tds[0]
                        team_name = clean_tds[1]
                        
                        if pos.isdigit(): # Sadece gerçek takımların olduğu satırları al (Sıra numarası varsa)
                            standings.append({
                                "pos": pos,
                                "team": team_name,
                                "p": clean_tds[2],  # O
                                "w": clean_tds[3],  # G
                                "d": clean_tds[4],  # B
                                "l": clean_tds[5],  # M
                                "pts": clean_tds[-1] # TFF'de puan her zaman son sütundur
                            })
                if len(standings) > 0:
                    break
    except Exception as e:
        print("TFF Puan durumu çekilemedi:", e)
        
    return standings

def get_analysis():
    # NTV Spor'un RSS servisi, genelde veri merkezi IP'lerini engellemez
    rss_url = "https://www.ntv.com.tr/spor.rss"
    news = []
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall('./channel/item')[:12]:
                title = item.find('title').text
                link = item.find('link').text
                desc = item.find('description').text if item.find('description') is not None else ""
                
                # Görsel bulma işlemi (NTV RSS'te bazen enclosure, bazen HTML içi img olur)
                img_url = ""
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    img_url = enclosure.get('url')
                else:
                    img_match = re.search(r'<img[^>]+src="([^">]+)"', desc)
                    if img_match:
                        img_url = img_match.group(1)
                        
                clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
                clean_desc = clean_desc[:130] + "..." if len(clean_desc) > 130 else clean_desc
                
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
    print("API'siz sistem çalışıyor, veriler toplanıyor...")
    
    standings = get_standings()
    analysis = get_analysis()
    
    # 🚨 EĞER İKİ SİTE DE GITHUB'I ENGELLERSE (YEDEK SİSTEM)
    if not standings:
        standings = [
            {"pos": 1, "team": "Galatasaray A.Ş.", "p": "-", "w": "-", "d": "-", "l": "-", "pts": "-"},
            {"pos": 2, "team": "Fenerbahçe A.Ş.", "p": "-", "w": "-", "d": "-", "l": "-", "pts": "-"},
            {"pos": 3, "team": "Beşiktaş A.Ş.", "p": "-", "w": "-", "d": "-", "l": "-", "pts": "-"},
            {"pos": 4, "team": "Trabzonspor A.Ş.", "p": "-", "w": "-", "d": "-", "l": "-", "pts": "-"},
        ]
        
    if not analysis:
        analysis = [
            {
                "title": "Veri Çekme İşlemi Beklemede (Bot Koruması)",
                "desc": "Spor sitelerinin güvenlik sistemleri (Cloudflare) şu an anlık veri çekmemizi durdurdu. Bot sistemi 1 saat sonra farklı bir kanaldan tekrar veri çekmeyi deneyecektir.",
                "link": "#",
                "img": ""
            }
        ]
        
    output_data = {
        "standings": standings,
        "analysis": analysis
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print("Veriler başarıyla yazıldı!")

if __name__ == "__main__":
    main()
