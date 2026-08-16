import json
import urllib.request
import ssl
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import random


# SSL sertifika doğrulamasını devre dışı bırak (güvenli ortamlarda kullanılmamalı)
def create_unverified_context():
    """SSL doğrulama hatasını önlemek için context oluşturur."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    except Exception:
        return None


def fetch_api_data(url: str, api_key: str = None) -> Optional[Dict]:
    """API'den JSON verisi çeker."""
    ctx = create_unverified_context()
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        if api_key:
            headers['X-Auth-Token'] = api_key
        
        req = urllib.request.Request(url, headers=headers)
        
        if ctx:
            response = urllib.request.urlopen(req, timeout=15, context=ctx)
        else:
            response = urllib.request.urlopen(req, timeout=15)
            
        data = json.loads(response.read().decode('utf-8'))
        return data
        
    except Exception as error:
        print(f"API bağlantı hatası ({url}): {error}")
        return None


def get_football_standings(api_key: str = None) -> Optional[List[Dict[str, Any]]]:
    """Football-Data.org API'den Süper Lig puan durumunu çeker."""
    url = "https://api.football-data.org/v4/competitions/TR1/standings"
    
    data = fetch_api_data(url, api_key)
    
    if not data or 'standings' not in data:
        return None
    
    standings = []
    
    try:
        # TOTAL standings tablosunu al
        total_table = None
        for table in data.get('standings', []):
            if table.get('type') == 'TOTAL':
                total_table = table.get('table', [])
                break
        
        if not total_table:
            return None
            
        for team in total_table:
            standings.append({
                "pos": str(team.get('position', 0)),
                "team": team.get('team', {}).get('name', 'Bilinmeyen'),
                "played": str(team.get('playedGames', 0)),
                "won": str(team.get('won', 0)),
                "drawn": str(team.get('draw', 0)),
                "lost": str(team.get('lost', 0)),
                "points": str(team.get('points', 0))
            })
            
        return standings
        
    except Exception as error:
        print(f"Puan durumu işleme hatası: {error}")
        return None


def get_recent_matches(api_key: str = None) -> List[Dict[str, Any]]:
    """Son oynanan maçları getirir."""
    today = datetime.now()
    start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f"https://api.football-data.org/v4/competitions/TR1/matches?dateFrom={start_date}&dateTo={end_date}"
    
    data = fetch_api_data(url, api_key)
    
    matches = []
    
    if data and 'matches' in data:
        for match in data['matches']:
            status = match.get('status', 'SCHEDULED')
            
            # Sadece tamamlanmış veya canlı maçlar
            if status in ['FINISHED', 'IN_PLAY', 'LIVE']:
                home_team = match.get('homeTeam', {}).get('name', 'Ev Sahibi')
                away_team = match.get('awayTeam', {}).get('name', 'Deplasman')
                home_score = match.get('score', {}).get('fullTime', {}).get('home', '-')
                away_score = match.get('score', {}).get('fullTime', {}).get('away', '-')
                
                if status in ['IN_PLAY', 'LIVE']:
                    home_score = match.get('score', {}).get('current', {}).get('home', '-')
                    away_score = match.get('score', {}).get('current', {}).get('away', '-')
                
                match_date = match.get('utcDate', '')[:16].replace('T', ' ')
                
                matches.append({
                    "title": f"{home_team} vs {away_team}",
                    "desc": f"📅 {match_date} | 🏆 Maç Sonucu: {home_score} - {away_score}",
                    "link": "#",
                    "img": "",
                    "status": "CANLI 🔴" if status in ['IN_PLAY', 'LIVE'] else "TAMAMLANDI ✅"
                })
    
    return matches


def generate_live_matches() -> List[Dict[str, Any]]:
    """Gerçekçi simüle edilmiş canlı maç verileri üretir."""
    teams = [
        "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor",
        "Başakşehir", "Göztepe", "Konyaspor", "Antalyaspor",
        "Alanyaspor", "Kasımpaşa", "Sivasspor", "Eyüpspor",
        "Kayserispor", "Rizespor", "Bodrum FK", "Gaziantep FK",
        "Hatayspor", "Adana Demirspor", "Samsunspor", "Karagümrük"
    ]
    
    matches = []
    num_matches = random.randint(3, 6)
    
    # Haftanın maçlarını oluştur
    today = datetime.now()
    
    for i in range(num_matches):
        # Rastgele iki takım seç
        home_idx = random.randint(0, len(teams) - 1)
        away_idx = random.randint(0, len(teams) - 1)
        while away_idx == home_idx:
            away_idx = random.randint(0, len(teams) - 1)
        
        home_team = teams[home_idx]
        away_team = teams[away_idx]
        
        # Maç durumu (çoğunlukla tamamlanmış, bazen canlı)
        is_live = random.random() < 0.2  # %20 şansla canlı maç
        
        if is_live:
            # Canlı maç - rastgele skor
            home_score = random.randint(0, 3)
            away_score = random.randint(0, 3)
            status = "CANLI 🔴"
            minute = random.randint(15, 85)
            desc = f"📅 Bugün | ⏱️ {minute}'. Dakika | 🏆 Skor: {home_score} - {away_score}"
        else:
            # Tamamlanmış maç
            match_day_offset = random.randint(-6, -1)
            match_date = today + timedelta(days=match_day_offset)
            date_str = match_date.strftime("%d.%m.%Y")
            
            # Gerçekçi skor dağılımı
            home_score = random.choices([0, 1, 2, 3, 4], weights=[20, 35, 25, 15, 5])[0]
            away_score = random.choices([0, 1, 2, 3, 4], weights=[25, 35, 25, 10, 5])[0]
            
            status = "TAMAMLANDI ✅"
            desc = f"📅 {date_str} | 🏆 Maç Sonucu: {home_score} - {away_score}"
        
        matches.append({
            "title": f"{home_team} vs {away_team}",
            "desc": desc,
            "link": "#",
            "img": "",
            "status": status
        })
    
    return matches


def generate_live_standings() -> List[Dict[str, Any]]:
    """Gerçekçi simüle edilmiş canlı puan durumu üretir."""
    teams_data = [
        ("Galatasaray", 92, 38),
        ("Fenerbahçe", 90, 38),
        ("Beşiktaş", 74, 38),
        ("Trabzonspor", 64, 38),
        ("Başakşehir FK", 62, 38),
        ("Göztepe SK", 57, 38),
        ("Konyaspor", 53, 38),
        ("Antalyaspor", 52, 38),
        ("Alanyaspor", 50, 38),
        ("Kasımpaşa SK", 49, 38),
        ("Sivasspor", 48, 38),
        ("Eyüpspor", 47, 38),
        ("Kayserispor", 46, 38),
        ("Rizespor", 44, 38),
        ("Bodrum FK", 43, 38),
        ("Gaziantep FK", 42, 38),
        ("Hatayspor", 41, 38),
        ("Adana Demirspor", 37, 38),
        ("Samsunspor", 32, 38),
        ("Karagümrük", 25, 38)
    ]
    
    standings = []
    
    # Puanlarda küçük rastgele değişiklikler (sezon devam ediyormuş gibi)
    for pos, (team, base_points, played) in enumerate(teams_data, 1):
        # Sezon ortasındaymış gibi simüle et
        current_played = random.randint(15, 25)
        points_per_game = base_points / played
        current_points = int(current_played * points_per_game * random.uniform(0.9, 1.1))
        
        won = random.randint(int(current_played * 0.3), int(current_played * 0.7))
        lost = random.randint(int(current_played * 0.1), int(current_played * 0.4))
        drawn = current_played - won - lost
        if drawn < 0:
            drawn = 0
            lost = current_played - won
        
        standings.append({
            "pos": str(pos),
            "team": team,
            "played": str(current_played),
            "won": str(won),
            "drawn": str(drawn),
            "lost": str(lost),
            "points": str(current_points)
        })
    
    return standings


def create_analysis(status: str, matches: List[Dict]) -> List[Dict[str, Any]]:
    """Analiz bölümü için veri oluşturur."""
    analysis = []
    
    # Sistem durumu
    analysis.append({
        "title": "📊 Sistem Durumu",
        "desc": status,
        "link": "#",
        "img": ""
    })
    
    # Maç özeti varsa ekle
    if matches:
        for match in matches[:10]:  # İlk 10 maçı göster
            analysis.append({
                "title": f"⚽ {match['status']} - {match['title']}",
                "desc": match['desc'],
                "link": "#",
                "img": ""
            })
    else:
        analysis.append({
            "title": "📅 Yaklaşık Maçlar",
            "desc": "Son 7 gün içinde oynanmış maç bulunamadı. Yeni sezon başladığında maç sonuçları burada görünecektir.",
            "link": "#",
            "img": ""
        })
    
    return analysis


def save_data(data: Dict, filename: str = "data.json") -> None:
    """Veriyi JSON dosyasına kaydeder."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"✅ {filename} başarıyla oluşturuldu!")


def main():
    """Ana fonksiyon."""
    print("🔄 Veriler çekiliyor...")
    
    # API anahtarı opsiyonel (football-data.org için)
    api_key = None  # İsterseniz buraya API anahtarınızı ekleyebilirsiniz
    
    # Puan durumunu çek
    standings = get_football_standings(api_key)
    
    # Maç sonuçlarını çek
    matches = get_recent_matches(api_key)
    
    use_mock_data = False
    
    if not standings:
        print("⚠️ API'den veri çekilemedi, simülasyon modu aktif...")
        standings = generate_live_standings()
        matches = generate_live_matches()
        use_mock_data = True
    
    if not matches:
        print("ℹ️ Maç verisi bulunamadı, simüle edilmiş maçlar oluşturuluyor...")
        matches = generate_live_matches()
        use_mock_data = True
    
    if use_mock_data:
        status = "🟡 Simülasyon Modu: Gerçek zamanlı maç verileri simüle ediliyor. API anahtarı ekleyerek canlı verilere ulaşabilirsiniz."
    else:
        status = "🟢 Canlı Veriler Football-Data.org API'den Başarıyla Çekildi!"
    
    # Analiz verilerini oluştur
    analysis = create_analysis(status, matches)
    
    data = {
        "standings": standings,
        "analysis": analysis,
        "matches": matches,
        "last_update": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "source": "Simülasyon" if use_mock_data else "Football-Data.org API",
        "is_live": not use_mock_data
    }
    
    save_data(data)
    print(f"📊 Toplam {len(standings)} takım ve {len(matches)} maç verisi kaydedildi.")


if __name__ == "__main__":
    main()
