#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MUKAprint - Otomatik Yazdırma Hizmeti
Dosya izleme modülü
"""

import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PySide6.QtCore import QObject, Signal


class FileWatcher(QObject):
    """WhatsApp ve diğer klasörleri izleyen sınıf"""
    
    # Yeni dosya algılandığında sinyal gönder
    file_detected = Signal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.observers = []
        self.supported_extensions = config.get("supported_extensions", [])
        
    def start_watching(self):
        """İzleme işlemini başlatır"""
        # Önceki izleyicileri durdur
        self.stop_watching()
        
        # Yapılandırmadaki izleme klasörlerini kontrol et
        watch_folders = self.config.get("watch_folders", [])
        
        if not watch_folders:
            print("İzlenecek klasör bulunamadı. Lütfen ayarlardan klasör ekleyin.")
            return False
        
        # Her klasör için bir izleyici oluştur
        for folder in watch_folders:
            if os.path.exists(folder) and os.path.isdir(folder):
                event_handler = WhatsAppFileHandler(self)
                observer = Observer()
                observer.schedule(event_handler, folder, recursive=True)
                observer.start()
                self.observers.append(observer)
                print(f"İzleme başlatıldı: {folder}")
            else:
                print(f"Klasör bulunamadı: {folder}")
        
        return len(self.observers) > 0
    
    def stop_watching(self):
        """İzleme işlemini durdurur"""
        for observer in self.observers:
            observer.stop()
        
        for observer in self.observers:
            observer.join()
        
        self.observers = []
        print("Tüm klasör izlemeleri durduruldu.")
    
    def is_supported_file(self, file_path):
        """Dosya uzantısının desteklenip desteklenmediğini kontrol eder"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions


class WhatsAppFileHandler(FileSystemEventHandler):
    """WhatsApp klasöründeki dosya olaylarını işleyen sınıf"""
    
    def __init__(self, file_watcher):
        self.file_watcher = file_watcher
        self.last_processed_files = set()
    
    def on_created(self, event):
        """Yeni dosya oluşturulduğunda çağrılır"""
        if not event.is_directory and self.file_watcher.is_supported_file(event.src_path):
            # Dosyanın tamamen yazılmasını bekle
            self._wait_for_file_ready(event.src_path)
            
            # Dosya daha önce işlenmediyse sinyal gönder
            if event.src_path not in self.last_processed_files:
                self.last_processed_files.add(event.src_path)
                self.file_watcher.file_detected.emit(event.src_path)
                
                # Son işlenen dosyaların sayısını sınırla
                if len(self.last_processed_files) > 100:
                    self.last_processed_files = set(list(self.last_processed_files)[-100:])
    
    def _wait_for_file_ready(self, file_path, timeout=5):
        """Dosyanın tamamen yazılmasını bekler"""
        start_time = time.time()
        last_size = -1
        
        while time.time() - start_time < timeout:
            try:
                current_size = os.path.getsize(file_path)
                if current_size == last_size and current_size > 0:
                    # Dosya boyutu değişmediyse, dosya hazır demektir
                    return True
                last_size = current_size
                time.sleep(0.5)
            except (OSError, FileNotFoundError):
                # Dosya henüz erişilebilir değilse bekle
                time.sleep(0.5)
        
        return False