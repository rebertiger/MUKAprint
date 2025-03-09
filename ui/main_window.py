#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MUKAprint - Otomatik Yazdırma Hizmeti
Ana pencere modülü
"""

import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QSpinBox, QCheckBox,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QTabWidget, QSplitter, QGroupBox, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QTimer
from PySide6.QtGui import QIcon, QAction, QFont, QColor
import qtawesome as qta

from file_watcher import FileWatcher
from document_processor import DocumentProcessor
from ui.settings_dialog import SettingsDialog
from ui.file_list_widget import FileListWidget
from ui.print_history_widget import PrintHistoryWidget


class MainWindow(QMainWindow):
    """MUKAprint ana penceresi"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.file_watcher = FileWatcher(config)
        self.document_processor = DocumentProcessor(config)
        
        # Dosya izleme ve yazdırma sinyallerini bağla
        self.file_watcher.file_detected.connect(self.on_file_detected)
        self.document_processor.print_started.connect(self.on_print_started)
        self.document_processor.print_completed.connect(self.on_print_completed)
        self.document_processor.print_error.connect(self.on_print_error)
        
        self.init_ui()
        self.load_printers()
        
        # Otomatik izlemeyi başlat
        if self.config.get("watch_folders"):
            self.file_watcher.start_watching()
    
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        # Ana pencere ayarları
        self.setWindowTitle("MUKAprint - Otomatik Yazdırma Hizmeti")
        self.setMinimumSize(900, 600)
        
        # Ana widget ve düzen
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Üst araç çubuğu
        toolbar_layout = QHBoxLayout()
        
        # İzleme başlat/durdur düğmesi
        self.watch_button = QPushButton("İzlemeyi Başlat")
        self.watch_button.setIcon(QIcon(qta.icon('fa5s.eye', color='green')))
        self.watch_button.clicked.connect(self.toggle_watching)
        toolbar_layout.addWidget(self.watch_button)
        
        # Klasör ekle düğmesi
        add_folder_button = QPushButton("Klasör Ekle")
        add_folder_button.setIcon(QIcon(qta.icon('fa5s.folder-plus', color='blue')))
        add_folder_button.clicked.connect(self.add_watch_folder)
        toolbar_layout.addWidget(add_folder_button)
        
        # Ayarlar düğmesi
        settings_button = QPushButton("Ayarlar")
        settings_button.setIcon(QIcon(qta.icon('fa5s.cog', color='gray')))
        settings_button.clicked.connect(self.show_settings)
        toolbar_layout.addWidget(settings_button)
        
        toolbar_layout.addStretch()
        
        # Durum etiketi
        self.status_label = QLabel("Hazır")
        toolbar_layout.addWidget(self.status_label)
        
        main_layout.addLayout(toolbar_layout)
        
        # Ana içerik bölgesi
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Dosya listesi
        self.file_list_widget = FileListWidget(self.document_processor)
        content_splitter.addWidget(self.file_list_widget)
        
        # Yazdırma ayarları ve geçmiş sekmesi
        right_panel = QTabWidget()
        
        # Yazdırma ayarları sekmesi
        print_settings_widget = QWidget()
        print_settings_layout = QVBoxLayout(print_settings_widget)
        
        # Yazıcı ayarları grubu
        printer_group = QGroupBox("Yazıcı Ayarları")
        printer_layout = QFormLayout(printer_group)
        
        # Yazıcı seçimi
        self.printer_combo = QComboBox()
        printer_layout.addRow("Yazıcı:", self.printer_combo)
        
        # Kağıt boyutu seçimi
        self.paper_size_combo = QComboBox()
        for paper in self.document_processor.get_available_paper_sizes():
            self.paper_size_combo.addItem(paper["name"])
        printer_layout.addRow("Kağıt Boyutu:", self.paper_size_combo)
        
        # Kopya sayısı
        self.copies_spin = QSpinBox()
        self.copies_spin.setMinimum(1)
        self.copies_spin.setMaximum(99)
        self.copies_spin.setValue(self.config.get("default_copies", 1))
        printer_layout.addRow("Kopya Sayısı:", self.copies_spin)
        
        # Arkalı önlü yazdırma
        self.duplex_check = QCheckBox("Arkalı Önlü Yazdır")
        self.duplex_check.setChecked(self.config.get("default_duplex", False))
        printer_layout.addRow("", self.duplex_check)
        
        print_settings_layout.addWidget(printer_group)
        
        # Yazdırma düğmeleri
        print_buttons_layout = QHBoxLayout()
        
        # Seçili dosyaları yazdır
        print_selected_button = QPushButton("Seçili Dosyaları Yazdır")
        print_selected_button.setIcon(QIcon(qta.icon('fa5s.print', color='blue')))
        print_selected_button.clicked.connect(self.print_selected_files)
        print_buttons_layout.addWidget(print_selected_button)
        
        # Tüm dosyaları yazdır
        print_all_button = QPushButton("Tüm Dosyaları Yazdır")
        print_all_button.setIcon(QIcon(qta.icon('fa5s.print', color='green')))
        print_all_button.clicked.connect(self.print_all_files)
        print_buttons_layout.addWidget(print_all_button)
        
        print_settings_layout.addLayout(print_buttons_layout)
        print_settings_layout.addStretch()
        
        # Yazdırma geçmişi sekmesi
        self.print_history_widget = PrintHistoryWidget(self.document_processor)
        
        # Sekmeleri ekle
        right_panel.addTab(print_settings_widget, "Yazdırma Ayarları")
        right_panel.addTab(self.print_history_widget, "Yazdırma Geçmişi")
        
        content_splitter.addWidget(right_panel)
        
        # Bölme oranlarını ayarla
        content_splitter.setSizes([600, 300])
        
        main_layout.addWidget(content_splitter)
        
        # Ana pencereye widget'ı ekle
        self.setCentralWidget(central_widget)
        
        # Durum çubuğu
        self.statusBar().showMessage("MUKAprint hazır")
    
    def load_printers(self):
        """Sistemdeki yazıcıları yükler"""
        self.printer_combo.clear()
        printers = self.document_processor.get_available_printers()
        
        default_printer = self.config.get("default_printer", "")
        default_index = 0
        
        for i, printer in enumerate(printers):
            self.printer_combo.addItem(printer["name"])
            if printer["name"] == default_printer or printer["is_default"]:
                default_index = i
        
        if self.printer_combo.count() > 0:
            self.printer_combo.setCurrentIndex(default_index)
    
    def toggle_watching(self):
        """İzleme işlemini başlatır veya durdurur"""
        if self.file_watcher.observers:
            # İzleme aktifse durdur
            self.file_watcher.stop_watching()
            self.watch_button.setText("İzlemeyi Başlat")
            self.watch_button.setIcon(QIcon(qta.icon('fa5s.eye', color='green')))
            self.status_label.setText("İzleme durduruldu")
            self.statusBar().showMessage("Dosya izleme durduruldu")
        else:
            # İzleme durmuşsa başlat
            if self.file_watcher.start_watching():
                self.watch_button.setText("İzlemeyi Durdur")
                self.watch_button.setIcon(QIcon(qta.icon('fa5s.eye-slash', color='red')))
                self.status_label.setText("İzleniyor...")
                self.statusBar().showMessage("Dosyalar izleniyor...")
            else:
                QMessageBox.warning(
                    self, 
                    "İzleme Başlatılamadı", 
                    "İzlenecek klasör bulunamadı. Lütfen ayarlardan klasör ekleyin."
                )
    
    def add_watch_folder(self):
        """İzlenecek klasör ekler"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "İzlenecek Klasör Seç",
            self.config.get("last_directory", "")
        )
        
        if folder:
            # Son dizini kaydet
            self.config["last_directory"] = folder
            
            # Klasörü izleme listesine ekle
            watch_folders = self.config.get("watch_folders", [])
            if folder not in watch_folders:
                watch_folders.append(folder)
                self.config["watch_folders"] = watch_folders
                
                # İzleme aktifse yeniden başlat
                if self.file_watcher.observers:
                    self.file_watcher.start_watching()
                
                self.statusBar().showMessage(f"Klasör eklendi: {folder}")
    
    def show_settings(self):
        """Ayarlar penceresini gösterir"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Ayarlar değiştiyse yapılandırmayı güncelle
            self.config = dialog.get_config()
            
            # İzleme aktifse yeniden başlat
            if self.file_watcher.observers:
                self.file_watcher.start_watching()
            
            # Yazıcı listesini güncelle
            self.load_printers()
    
    def on_file_detected(self, file_path):
        """Yeni dosya algılandığında çağrılır"""
        self.statusBar().showMessage(f"Yeni dosya algılandı: {os.path.basename(file_path)}")
        self.file_list_widget.add_file(file_path)
        
        # Otomatik yazdırma etkinse dosyayı yazdır
        if self.config.get("auto_print", False):
            self.print_document(file_path)
    
    def print_selected_files(self):
        """Seçili dosyaları yazdırır"""
        selected_files = self.file_list_widget.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "Bilgi", "Lütfen yazdırılacak dosyaları seçin.")
            return
        
        for file_path in selected_files:
            self.print_document(file_path)
    
    def print_all_files(self):
        """Listedeki tüm dosyaları yazdırır"""
        all_files = self.file_list_widget.get_all_files()
        if not all_files:
            QMessageBox.information(self, "Bilgi", "Yazdırılacak dosya bulunamadı.")
            return
        
        for file_path in all_files:
            self.print_document(file_path)
    
    def print_document(self, file_path):
        """Belgeyi yazdırır"""
        printer_name = self.printer_combo.currentText()
        paper_size = self.paper_size_combo.currentText()
        copies = self.copies_spin.value()
        duplex = self.duplex_check.isChecked()
        
        # Yazdırma işlemini başlat
        self.document_processor.print_document(
            file_path, printer_name, paper_size, copies, duplex
        )
    
    def on_print_started(self, file_path, printer_name):
        """Yazdırma başladığında çağrılır"""
        self.statusBar().showMessage(f"Yazdırılıyor: {os.path.basename(file_path)}")
        self.file_list_widget.mark_file_printing(file_path)
    
    def on_print_completed(self, file_path, success):
        """Yazdırma tamamlandığında çağrılır"""
        if success:
            self.statusBar().showMessage(f"Yazdırma tamamlandı: {os.path.basename(file_path)}")
            self.file_list_widget.mark_file_printed(file_path, True)
        else:
            self.statusBar().showMessage(f"Yazdırma hatası: {os.path.basename(file_path)}")
            self.file_list_widget.mark_file_printed(file_path, False)
    
    def on_print_error(self, file_path, error_message):
        """Yazdırma hatası oluştuğunda çağrılır"""
        self.statusBar().showMessage(f"Yazdırma hatası: {os.path.basename(file_path)}")
        self.file_list_widget.mark_file_printed(file_path, False)
        
    def get_config(self):
        """Güncellenmiş yapılandırmayı döndürür"""
        return self.config