#!/bin/bash
# Süper Lig Veri Botu - Otomatik Çalıştırma Scripti

echo "🚀 Süper Lig Analiz Merkezi - Veri Botu Başlatılıyor..."

# Python botunu çalıştır
python fetcher.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Veriler başarıyla güncellendi!"
    echo "📄 data.json dosyası oluşturuldu."
    echo "🌐 index.html sayfasını açarak maç sonuçlarını ve puan durumunu görebilirsiniz."
else
    echo ""
    echo "❌ Bir hata oluştu. Lütfen console çıktısını kontrol edin."
    exit 1
fi
