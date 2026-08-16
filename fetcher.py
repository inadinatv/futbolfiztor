import json
import urllib.request
import xml.etree.ElementTree as ET
import re

def get_standings():
    # Hiçbir API kullanmadan doğrudan puan tablosunu içeren açık HTML sayfasını okuyoruz
    url = "https://www.trtspor.com.tr/puan-durumu/trendyol-super-lig/"
    standings = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # HTML içindeki Tablo (tbody) alanını buluyoruz
        tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE)
        if tbody_match:
            # Tablodaki satırları (<tr>) tek tek ayırıyoruz
            trs = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody_match.group(1), re.DOTALL | re.IGNORECASE)
            for tr in trs:
                # Satırdaki sütunları (<td>) buluyoruz
                tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL | re.IGNORECASE)
                if len(tds) >= 8:
                    # İçerisindeki HTML link etiketlerini (<a href..>) temizliyoruz
                    clean_tds = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
                    
                    pos = clean_tds[0]
                    team_name = clean_tds[1]
                    
                    # Eğer ilk sütun bir sayı ise (sıra numarası), bu geçerli bir takımdır
                    if pos.isdigit():
                        standings.append({
                            "pos": pos,
                            "team": team_name,
                            "p": clean_tds[2],  # Oynanan Maç
                            "w": clean_tds[3],  # Galibiyet
                            "d": clean_tds[4],  # Beraberlik
                            "l": clean_tds[5],  # Mağlubiyet
                            "pts": clean_tds[-1] # Puan (Son sütun)
                        })
    except Exception as e:
        print("Puan durumu HTML sayfasından çekilemedi:", e)
        
    return standings

def get_analysis():
    # TRT Spor'un tamamen açık RSS beslemesinden maç analizlerini ve spor haberlerini çekiyoruz
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
    print("API'siz sistem çalışıyor, veriler toplanıyor...")
    
    standings = get_standings()
    analysis = get_analysis()
    
    if not standings:
        standings = [
            {"pos": 1, "team": "Veriler şu an güncelleniyor...", "p": 0, "w": 0, "d": 0, "l": 0, "pts": 0}
        ]
        
    output_data = {
        "standings": standings,
        "analysis": analysis
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print("data.json tamamen açık kaynaklardan başarıyla güncellendi!")

if __name__ == "__main__":
    main()
