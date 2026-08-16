import json
import urllib.request
import re
from datetime import datetime

def get_tff_standings():
    url = "https://www.tff.org/default.aspx?pageID=198"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        for table in tables:
            if 'Takım' in table and 'Puan' in table:
                standings = []
                trs = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL | re.IGNORECASE)
                for tr in trs:
                    tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL | re.IGNORECASE)
                    if len(tds) >= 8:
                        clean_tds = [re.sub(r'<[^>]+>', '', td).replace('&nbsp;', '').strip() for td in tds]
                        if clean_tds[0].isdigit():
                            standings.append({
                                "pos": clean_tds[0], "team": clean_tds[1],
                                "p": clean_tds[2], "w": clean_tds[3], "d": clean_tds[4], "l": clean_tds[5],
                                "pts": clean_tds[-1]
                            })
                return standings
    except Exception as e:
        pass
    return None

def main():
    standings = get_tff_standings()
    
    # EĞER TFF BOTU ENGELLERSE KESİNLİKLE BOŞ KALMAYACAK YEDEK VERİ
    if not standings:
        standings = [
            {"pos": "1", "team": "Galatasaray A.Ş.", "p": "0", "w": "0", "d": "0", "l": "0", "pts": "0"},
            {"pos": "2", "team": "Fenerbahçe A.Ş.", "p": "0", "w": "0", "d": "0", "l": "0", "pts": "0"},
            {"pos": "3", "team": "Beşiktaş A.Ş.", "p": "0", "w": "0", "d": "0", "l": "0", "pts": "0"},
            {"pos": "4", "team": "Trabzonspor A.Ş.", "p": "0", "w": "0", "d": "0", "l": "0", "pts": "0"}
        ]
        status = "🔴 TFF Bağlantısı Gecikti (Geçici Yedek Veriler Gösteriliyor)"
    else:
        status = "🟢 Veriler TFF'den Başarıyla Çekildi"

    analysis = [
        {
            "title": "Sistem Bağlantı Durumu",
            "desc": f"Bot aktif olarak çalışıyor. Durum: {status}. Veri akışı sorunsuz sağlandığında maç analizleri burada listelenecektir.",
            "link": "#",
            "img": ""
        }
    ]

    data = {
        "standings": standings,
        "analysis": analysis,
        "last_update": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("data.json başarıyla oluşturuldu!")

if __name__ == "__main__":
    main()
