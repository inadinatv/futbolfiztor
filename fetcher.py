"""
Süper Lig Veri Çekici - TheSportsDB API kullanarak gerçek maç verilerini çeker
NOT: Yeni sezon başlamadığı için şu anda az veri var. 
Sezon başladığında tüm maçlar otomatik çekilecek.
"""
import requests
import json
from datetime import datetime, timedelta

class SuperLigDataFetcher:
    def __init__(self):
        self.base_url = "https://www.thesportsdb.com/api/v1/json/3"
        # Tüm Süper Lig takımları ve alternatif isimleri
        self.teams = [
            {"name": "Galatasaray", "id": "133804", "alt_names": ["Galatasaray SK", "Cimbom"]},
            {"name": "Fenerbahce", "id": "133807", "alt_names": ["Fenerbahçe SK", "Sari Lacivert"]},
            {"name": "Besiktas", "id": "133794", "alt_names": ["Beşiktaş JK", "Kara Kartal"]},
            {"name": "Trabzonspor", "id": "133796", "alt_names": ["Trabzonspor SK", "Bordo Mavi"]},
            {"name": "Basaksehir", "id": "135244", "alt_names": ["İstanbul Başakşehir FK"]},
            {"name": "Antalyaspor", "id": "135242", "alt_names": ["Antalya Spor Kulübü"]},
            {"name": "Konyaspor", "id": "135250", "alt_names": ["Konya Spor Kulübü"]},
            {"name": "Alanyaspor", "id": "135240", "alt_names": ["Alanya Spor Kulübü"]},
            {"name": "Sivasspor", "id": "135258", "alt_names": ["Sivas Spor Kulübü"]},
            {"name": "Kayserispor", "id": "135248", "alt_names": ["Kayseri Spor Kulübü"]},
            {"name": "Rizespor", "id": "135256", "alt_names": ["Çaykur Rizespor"]},
            {"name": "Gaziantep", "id": "135246", "alt_names": ["Gaziantep FK"]},
            {"name": "Kasimpasa", "id": "135252", "alt_names": ["Kasımpaşa SK"]},
            {"name": "Goztepe", "id": "135247", "alt_names": ["Göztepe SK"]},
            {"name": "Bodrumspor", "id": "140552", "alt_names": ["Bodrum FK"]},
            {"name": "Eyupspor", "id": "140550", "alt_names": ["Eyüpspor SK"]},
            {"name": "Adana Demirspor", "id": "135238", "alt_names": ["Adana Demir Spor Kulübü"]},
            {"name": "Hatayspor", "id": "135249", "alt_names": ["Hatay Spor Kulübü"]},
            {"name": "Karagumruk", "id": "139777", "alt_names": ["Fatih Karagümrük SK"]},
            {"name": "Van BB", "id": "140554", "alt_names": ["Vanspor FK"]}
        ]
        
    def get_team_matches(self, team_id, count=15):
        """Bir takımın son maçlarını getirir"""
        try:
            response = requests.get(
                f"{self.base_url}/eventslast.php?id={team_id}",
                timeout=10
            )
            data = response.json()
            
            if data.get('results') and isinstance(data['results'], list):
                matches = []
                for match in data['results'][:count]:
                    # Sadece Süper Lig maçlarını filtrele (lig ID 4339)
                    league_id = match.get('idLeague', '')
                    league_name = str(match.get('strLeague', ''))
                    
                    if league_id == '4339' or 'Super Lig' in league_name or 'Süper Lig' in league_name:
                        home_score = match.get('intHomeScore', '')
                        away_score = match.get('intAwayScore', '')
                        
                        # Skor yoksa maç oynanmamıştır
                        if home_score == '' or away_score == '':
                            continue
                            
                        matches.append({
                            'date': match.get('dateEvent', ''),
                            'time': match.get('strTime', ''),
                            'home_team': match.get('strHomeTeam', ''),
                            'away_team': match.get('strAwayTeam', ''),
                            'home_score': home_score,
                            'away_score': away_score,
                            'status': match.get('strStatus', 'FT'),
                            'venue': match.get('strVenue', ''),
                            'league': match.get('strLeague', 'Süper Lig'),
                            'round': match.get('strRound', ''),
                            'home_logo': match.get('strHomeThumb', ''),
                            'away_logo': match.get('strAwayThumb', '')
                        })
                return matches
            return []
        except Exception as e:
            print(f"Hata ({team_id}): {e}")
            return []
    
    def get_all_matches(self):
        """Tüm takımların son maçlarını birleştirir"""
        all_matches = []
        seen_matches = set()
        
        print("Takım maçları çekiliyor...")
        for i, team in enumerate(self.teams, 1):
            print(f"  [{i}/{len(self.teams)}] {team['name']}...", end=" ")
            matches = self.get_team_matches(team['id'])
            print(f"{len(matches)} maç")
            
            for match in matches:
                # Tekrarları önle
                match_key = f"{match['home_team']}-{match['away_team']}-{match['date']}"
                if match_key not in seen_matches:
                    seen_matches.add(match_key)
                    all_matches.append(match)
        
        # Tarihe göre sırala (en yeni önce)
        all_matches.sort(key=lambda x: x['date'], reverse=True)
        return all_matches
    
    def calculate_standings(self, matches):
        """Maç sonuçlarından puan durumu hesapla"""
        standings = {}
        
        for team in self.teams:
            standings[team['name']] = {
                'name': team['name'],
                'played': 0,
                'won': 0,
                'drawn': 0,
                'lost': 0,
                'goals_for': 0,
                'goals_against': 0,
                'points': 0
            }
        
        for match in matches:
            home = match['home_team']
            away = match['away_team']
            
            # Takım isimlerini normalize et
            home_normalized = self._normalize_team_name(home)
            away_normalized = self._normalize_team_name(away)
            
            home_score = match['home_score']
            away_score = match['away_score']
            
            # Skorlar geçerli mi kontrol et
            if not home_score or not away_score:
                continue
                
            try:
                home_score = int(home_score)
                away_score = int(away_score)
            except (ValueError, TypeError):
                continue
            
            # Ev sahibi takım istatistikleri
            if home_normalized in standings:
                standings[home_normalized]['played'] += 1
                standings[home_normalized]['goals_for'] += home_score
                standings[home_normalized]['goals_against'] += away_score
                
                if home_score > away_score:
                    standings[home_normalized]['won'] += 1
                    standings[home_normalized]['points'] += 3
                elif home_score == away_score:
                    standings[home_normalized]['drawn'] += 1
                    standings[home_normalized]['points'] += 1
                else:
                    standings[home_normalized]['lost'] += 1
            
            # Deplasman takım istatistikleri
            if away_normalized in standings:
                standings[away_normalized]['played'] += 1
                standings[away_normalized]['goals_for'] += away_score
                standings[away_normalized]['goals_against'] += home_score
                
                if away_score > home_score:
                    standings[away_normalized]['won'] += 1
                    standings[away_normalized]['points'] += 3
                elif away_score == home_score:
                    standings[away_normalized]['drawn'] += 1
                    standings[away_normalized]['points'] += 1
                else:
                    standings[away_normalized]['lost'] += 1
        
        # Puan durumunu sırala
        standings_list = list(standings.values())
        standings_list.sort(key=lambda x: (x['points'], x['goals_for'] - x['goals_against']), reverse=True)
        
        # Sıra numarası ekle
        for i, team in enumerate(standings_list, 1):
            team['position'] = i
            team['goal_difference'] = team['goals_for'] - team['goals_against']
        
        return standings_list
    
    def _normalize_team_name(self, name):
        """Takım ismini normalize et"""
        name_lower = name.lower()
        for team in self.teams:
            if team['name'].lower() in name_lower:
                return team['name']
            for alt in team['alt_names']:
                if alt.lower() in name_lower:
                    return team['name']
        return name
    
    def get_data(self):
        """Ana veri çekme fonksiyonu"""
        print("=" * 50)
        print("SÜPER LİG VERİLERİ ÇEKİLİYOR")
        print("=" * 50)
        
        matches = self.get_all_matches()
        print(f"\n✓ Toplam {len(matches)} maç bulundu")
        
        standings = self.calculate_standings(matches)
        print(f"✓ {len(standings)} takım için puan durumu hesaplandı")
        
        data = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'matches': matches,
            'standings': standings,
            'total_teams': len(self.teams),
            'source': 'TheSportsDB API',
            'season': '2024-2025'
        }
        
        return data

if __name__ == "__main__":
    fetcher = SuperLigDataFetcher()
    data = fetcher.get_data()
    
    # JSON olarak kaydet
    with open('super_lig_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print("SON MAÇLAR")
    print("=" * 50)
    for match in data['matches'][:10]:
        print(f"{match['date']}: {match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']}")
    
    print("\n" + "=" * 50)
    print("PUAN DURUMU (İlk 10)")
    print("=" * 50)
    for team in data['standings'][:10]:
        print(f"{team['position']:2}. {team['name']:20} | O: {team['played']:2} | G: {team['won']:2} | B: {team['drawn']:2} | M: {team['lost']:2} | AV: {team['goal_difference']:+3} | P: {team['points']:2}")
    
    print("\n✓ Veriler super_lig_data.json dosyasına kaydedildi!")
    print("✓ index.html dosyasını tarayıcıda açarak görüntüleyebilirsiniz.")
