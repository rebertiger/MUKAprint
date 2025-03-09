# MUKAprint - Otomatik Yazdırma Hizmeti

## Proje Açıklaması
MUKAprint, kırtasiye dükkanları için WhatsApp Desktop uygulamasından gelen belgeleri otomatik olarak izleyen ve yazdıran bir otomasyon aracıdır. Müşterilerden WhatsApp veya e-posta yoluyla gelen belgeleri (DOCX, XLSX, PDF vb.) otomatik olarak tespit edip, belirlenen ayarlarda yazdırma işlemini gerçekleştirir.

## Özellikler
- WhatsApp Desktop'tan gelen dosyaları otomatik izleme
- Desteklenen dosya formatları: DOCX, XLSX, PDF ve diğer yaygın belge formatları
- Kullanıcı dostu arayüz ile dosya görüntüleme ve seçme
- Yazdırma ayarları:
  - Yazıcı seçimi
  - Sayfa boyutu seçimi
  - Kopya adedi belirleme
  - Arkalı önlü / tek taraflı yazdırma seçeneği
- Yazdırılan dosyaları işaretleme ve takip etme
- Yazdırma işlemi geçmişi

## Teknik Gereksinimler
- Python 3.8+
- PyQt5 veya PySide6 (Kullanıcı arayüzü için)
- Watchdog (Dosya sistemi izleme için)
- PyWin32 (Windows yazdırma hizmetleri entegrasyonu için)
- python-docx, PyPDF2 (Belge işleme için)

## Kurulum
```
pip install -r requirements.txt
```

## Kullanım
1. Uygulamayı başlatın
2. WhatsApp Desktop'ın dosyaları kaydettiği klasörü seçin
3. Yazdırma ayarlarını yapılandırın
4. Gelen dosyaları izleyin ve yazdırın

## Proje Yapısı
- `main.py`: Ana uygulama başlatıcı
- `file_watcher.py`: WhatsApp dosyalarını izleyen modül
- `document_processor.py`: Belge işleme ve yazdırma işlevleri
- `ui/`: Kullanıcı arayüzü bileşenleri
- `config.py`: Uygulama yapılandırması
- `utils.py`: Yardımcı fonksiyonlar

## Lisans
Bu proje özel kullanım için geliştirilmiştir.