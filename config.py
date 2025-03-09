#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MUKAprint - Otomatik Yazdırma Hizmeti
Uygulama yapılandırma modülü
"""

import os
import json
from pathlib import Path

# Varsayılan yapılandırma dosyası yolu
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".mukaprint", "config.json")

# Varsayılan yapılandırma değerleri
DEFAULT_CONFIG = {
    "watch_folders": [],
    "default_printer": "",
    "default_paper_size": "A4",
    "default_copies": 1,
    "default_duplex": False,
    "history_limit": 100,
    "supported_extensions": [".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".jpeg", ".png", ".txt"],
    "auto_print": False,
    "theme": "light",
    "last_directory": ""
}


def load_config():
    """Yapılandırma dosyasını yükler, yoksa varsayılan değerleri kullanır"""
    try:
        # Yapılandırma dizininin varlığını kontrol et
        config_dir = os.path.dirname(CONFIG_FILE)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Yapılandırma dosyasını oku
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Eksik ayarları varsayılan değerlerle tamamla
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
        else:
            # Yapılandırma dosyası yoksa varsayılan değerleri kullan
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Yapılandırma yüklenirken hata oluştu: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """Yapılandırmayı dosyaya kaydeder"""
    try:
        # Yapılandırma dizininin varlığını kontrol et
        config_dir = os.path.dirname(CONFIG_FILE)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Yapılandırmayı dosyaya yaz
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Yapılandırma kaydedilirken hata oluştu: {e}")
        return False


def get_whatsapp_default_download_folder():
    """WhatsApp Desktop'ın varsayılan indirme klasörünü tahmin eder"""
    # Windows'ta varsayılan indirme klasörü
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    return downloads_folder