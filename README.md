# Günün Maçları ve Puan Durumu Botu

Bu proje GitHub Actions ile belirli liglerdeki günün maçlarını ve puan durumunu çeker, `data/combined.json` dosyasını günceller ve Vercel üzerinde statik Next.js sitesi olarak yayınlar.

## Özellikler

- Günün maçları
- Puan durumu
- GitHub Actions ile otomatik güncelleme
- Vercel uyumlu statik export
- İsteğe bağlı oran/ücret alanı

## Kullanılan API

Örnek yapı API-Football / api-sports.io göre yazıldı.

API key al:

https://dashboard.api-football.com/

## Yerel kurulum

```bash
npm install
cp .env.example .env
```

`.env` dosyasına `FOOTBALL_API_KEY` ekle.

Sonra:

```bash
npm run fetch-data
npm run dev
```

## GitHub kurulumu

1. GitHub'da yeni repo oluştur.
2. Bu dosyaları repoya ekle.
3. GitHub > Settings > Secrets and variables > Actions kısmına git.
4. Repository secret ekle:

```text
FOOTBALL_API_KEY
```

5. İstersen repository variables ekle:

```text
LEAGUE_IDS=203,39,140
SEASON=2026
TIMEZONE=Europe/Istanbul
FETCH_ODDS=false
```

## Lig ID örnekleri

API-Football için örnek ID'ler:

```text
203: Türkiye Süper Lig
39: Premier League
140: La Liga
135: Serie A
78: Bundesliga
61: Ligue 1
```

Not: ID'ler API sağlayıcısına göre değişebilir. Kendi API panelinden doğrula.

## Vercel kurulumu

1. https://vercel.com/new adresine gir.
2. GitHub reposunu import et.
3. Framework preset: Next.js
4. Build command:

```bash
npm run build
```

5. Output directory:

```text
out
```

6. Deploy et.

GitHub Actions `data/combined.json` dosyasını güncellediğinde Vercel otomatik olarak yeni deploy alır.

## Otomatik güncelleme

Workflow dosyası:

```text
.github/workflows/update-data.yml
```

Varsayılan olarak saatte bir çalışır:

```yaml
cron: "15 * * * *"
```

API limitine göre bunu değiştirebilirsin.

Örneğin 30 dakikada bir:

```yaml
cron: "*/30 * * * *"
```

Ancak ücretsiz API planlarında rate limit olabilir.

## Oran / ücret verisi

`.env` içinde:

```env
FETCH_ODDS=true
```

yalnızca API planın odds destekliyorsa ve kullanım hakkın varsa açılmalı.

Bahis oranları birçok ülkede lisanslı veri kapsamındadır. Yayınlamadan önce kullanım hakkını kontrol et.

## Scraping hakkında

Bu proje bilinçli olarak analiz sitelerinden izinsiz veri kazımaz.

Bir siteden scraping yapmak istiyorsan:

- Yazılı izin al.
- robots.txt dosyasına uy.
- Rate limit uygula.
- Telifli analiz metinlerini birebir kopyalama.
- Sadece factual veri çekmeye çalış: maç saati, skor, takım adı, puan durumu gibi.

## Veri dosyası

Bot şu dosyayı günceller:

```text
data/combined.json
```

Sayfa bu dosyadan statik build sırasında veri okur.
