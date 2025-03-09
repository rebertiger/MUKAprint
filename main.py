#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MUKAprint - Otomatik Yazdırma Hizmeti
Ana uygulama başlatıcı modülü
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import qtawesome as qta

from ui.main_window import MainWindow
from config import load_config, save_config


def main():
    """Ana uygulama başlatıcı fonksiyonu"""
    # Uygulama yapılandırmasını yükle
    config = load_config()
    
    # QApplication oluştur
    app = QApplication(sys.argv)
    app.setApplicationName("MUKAprint")
    app.setApplicationDisplayName("MUKAprint - Otomatik Yazdırma Hizmeti")
    app.setWindowIcon(QIcon(qta.icon('fa5s.print', color='#1a5fb4')))
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow(config)
    window.show()
    
    # Uygulama döngüsünü başlat
    exit_code = app.exec()
    
    # Çıkış yapmadan önce yapılandırmayı kaydet
    save_config(window.get_config())
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())