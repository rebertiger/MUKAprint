#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MUKAprint - Otomatik Yazdırma Hizmeti
Ayarlar iletişim kutusu modülü
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QCheckBox, QListWidget,
    QListWidgetItem, QFileDialog, QMessageBox, QGroupBox,
    QFormLayout, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
import qtawesome as qta


class SettingsDialog(QDialog):
    """Uygulama ayarları iletişim kutusu"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config.copy()  # Yapılandırmanın bir kopyasını al
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        self.setWindowTitle("MUKAprint Ayarları")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Sekme widget'ı
        tab_widget = QTabWidget()
        
        # Genel ayarlar sekmesi
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # İzlenen klasörler grubu
        folders_group = QGroupBox("İzlenen Klasörler")
        folders_layout = QVBoxLayout(folders_group)
        
        # Klasör listesi
        self.folders_list = QListWidget()
        folders_layout.addWidget(self.folders_list)
        
        # Klasör işlem düğmeleri
        folder_buttons_layout = QHBoxLayout()
        
        add_folder_button = QPushButton("Klasör Ekle")
        add_folder_button.setIcon(QIcon(qta.icon('fa5s.folder-plus', color='blue')))
        add_folder_button.clicked.connect(self.add_folder)
        folder_buttons_layout.addWidget(add_folder_button)
        
        remove_folder_button = QPushButton("Klasör Kaldır")
        remove_folder_button.setIcon(QIcon(qta.icon('fa5s.folder-minus', color='red')))
        remove_folder_button.clicked.connect(self.remove_folder)
        folder_buttons_layout.addWidget(remove_folder_button)
        
        folders_layout.addLayout(folder_buttons_layout)
        general_layout.addWidget(folders_group)
        
        # Otomatik yazdırma seçeneği
        self.auto_print_check = QCheckBox("Yeni dosyaları otomatik yazdır")
        general_layout.addWidget(self.auto_print_check)
        
        # Yazdırma ayarları sekmesi
        print_tab = QWidget()
        print_layout = QVBoxLayout(print_tab)
        
        # Varsayılan yazdırma ayarları
        print_settings_group = QGroupBox("Varsayılan Yazdırma Ayarları")
        print_settings_layout = QFormLayout(print_settings_group)
        
        # Varsayılan yazıcı
        self.default_printer_combo = QComboBox()
        self._load_printers()
        print_settings_layout.addRow("Varsayılan Yazıcı:", self.default_printer_combo)
        
        # Varsayılan kağıt boyutu
        self.default_paper_combo = QComboBox()
        self.default_paper_combo.addItems(["A4", "A5", "Letter", "Legal"])
        print_settings_layout.addRow("Varsayılan Kağıt Boyutu:", self.default_paper_combo)
        
        # Varsayılan kopya sayısı
        self.default_copies_spin = QSpinBox()
        self.default_copies_spin.setMinimum(1)
        self.default_copies_spin.setMaximum(99)
        print_settings_layout.addRow("Varsayılan Kopya Sayısı:", self.default_copies_spin)
        
        # Varsayılan arkalı önlü yazdırma
        self.default_duplex_check = QCheckBox("Arkalı Önlü Yazdır")
        print_settings_layout.addRow("", self.default_duplex_check)
        
        print_layout.addWidget(print_settings_group)
        
        # Desteklenen dosya türleri
        file_types_group = QGroupBox("Desteklenen Dosya Türleri")
        file_types_layout = QVBoxLayout(file_types_group)
        
        # Dosya türleri listesi
        self.file_types_list = QListWidget()
        file_types_layout.addWidget(self.file_types_list)
        
        # Dosya türü işlem düğmeleri
        file_type_buttons_layout = QHBoxLayout()
        
        add_type_button = QPushButton("Tür Ekle")
        add_type_button.setIcon(QIcon(qta.icon('fa5s.plus', color='blue')))
        add_type_button.clicked.connect(self.add_file_type)
        file_type_buttons_layout.addWidget(add_type_button)
        
        remove_type_button = QPushButton("Tür Kaldır")
        remove_type_button.setIcon(QIcon(qta.icon('fa5s.minus', color='red')))
        remove_type_button.clicked.connect(self.remove_file_type)
        file_type_buttons_layout.addWidget(remove_type_button)
        
        file_types_layout.addLayout(file_type_buttons_layout)
        print_layout.addWidget(file_types_group)
        
        # Sekmeleri ekle
        tab_widget.addTab(general_tab, "Genel Ayarlar")
        tab_widget.addTab(print_tab, "Yazdırma Ayarları")
        
        layout.addWidget(tab_widget)
        
        # Düğmeler
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_button = QPushButton("Kaydet")
        save_button.setIcon(QIcon(qta.icon('fa5s.save', color='green')))
        save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("İptal")
        cancel_button.setIcon(QIcon(qta.icon('fa5s.times', color='red')))
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def load_settings(self):
        """Mevcut ayarları yükler"""
        # İzlenen klasörler
        self.folders_list.clear()
        for folder in self.config.get("watch_folders", []):
            self.folders_list.addItem(folder)
        
        # Otomatik yazdırma
        self.auto_print_check.setChecked(self.config.get("auto_print", False))
        
        # Varsayılan yazıcı
        default_printer = self.config.get("default_printer", "")
        if default_printer and self.default_printer_combo.findText(default_printer) >= 0:
            self.default_printer_combo.setCurrentText(default_printer)
        
        # Varsayılan kağıt boyutu
        default_paper = self.config.get("default_paper_size", "A4")
        if self.default_paper_combo.findText(default_paper) >= 0:
            self.default_paper_combo.setCurrentText(default_paper)
        
        # Varsayılan kopya sayısı
        self.default_copies_spin.setValue(self.config.get("default_copies", 1))
        
        # Varsayılan arkalı önlü yazdırma
        self.default_duplex_check.setChecked(self.config.get("default_duplex", False))
        
        # Desteklenen dosya türleri
        self.file_types_list.clear()
        for ext in self.config.get("supported_extensions", []):
            self.file_types_list.addItem(ext)
    
    def _load_printers(self):
        """Sistemdeki yazıcıları yükler"""
        import win32print
        
        self.default_printer_combo.clear()
        
        # Sistemdeki yazıcıları al
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        default_printer = win32print.GetDefaultPrinter()
        
        for printer in printers:
            printer_name = printer[2]
            self.default_printer_combo.addItem(printer_name)
            
            # Varsayılan yazıcıyı seç
            if printer_name == default_printer:
                self.default_printer_combo.setCurrentText(printer_name)
    
    def add_folder(self):
        """İzlenen klasör ekler"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "İzlenecek Klasör Seç",
            self.config.get("last_directory", "")
        )
        
        if folder:
            # Son dizini kaydet
            self.config["last_directory"] = folder
            
            # Klasörü listeye ekle (eğer zaten yoksa)
            for i in range(self.folders_list.count()):
                if self.folders_list.item(i).text() == folder:
                    return
            
            self.folders_list.addItem(folder)
    
    def remove_folder(self):
        """Seçili klasörü kaldırır"""
        selected_items = self.folders_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen kaldırılacak bir klasör seçin.")
            return
        
        for item in selected_items:
            self.folders_list.takeItem(self.folders_list.row(item))
    
    def add_file_type(self):
        """Desteklenen dosya türü ekler"""
        # Basit bir iletişim kutusu göster
        from PySide6.QtWidgets import QInputDialog
        
        file_type, ok = QInputDialog.getText(
            self, 
            "Dosya Türü Ekle", 
            "Dosya uzantısını girin (örn: .pdf):"
        )
        
        if ok and file_type:
            # Uzantının başında nokta olduğundan emin ol
            if not file_type.startswith("."):
                file_type = "." + file_type
            
            # Uzantıyı küçük harfe çevir
            file_type = file_type.lower()
            
            # Uzantıyı listeye ekle (eğer zaten yoksa)
            for i in range(self.file_types_list.count()):
                if self.file_types_list.item(i).text() == file_type:
                    return
            
            self.file_types_list.addItem(file_type)
    
    def remove_file_type(self):
        """Seçili dosya türünü kaldırır"""
        selected_items = self.file_types_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen kaldırılacak bir dosya türü seçin.")
            return
        
        for item in selected_items:
            self.file_types_list.takeItem(self.file_types_list.row(item))
    
    def accept(self):
        """Ayarları kaydeder ve iletişim kutusunu kapatır"""
        # İzlenen klasörleri güncelle
        watch_folders = []
        for i in range(self.folders_list.count()):
            watch_folders.append(self.folders_list.item(i).text())
        self.config["watch_folders"] = watch_folders
        
        # Otomatik yazdırma ayarını güncelle
        self.config["auto_print"] = self.auto_print_check.isChecked()
        
        # Varsayılan yazıcı ayarını güncelle
        self.config["default_printer"] = self.default_printer_combo.currentText()
        
        # Varsayılan kağıt boyutu ayarını güncelle
        self.config["default_paper_size"] = self.default_paper_combo.currentText()
        
        # Varsayılan kopya sayısı ayarını güncelle
        self.config["default_copies"] = self.default_copies_spin.value()
        
        # Varsayılan arkalı önlü yazdırma ayarını güncelle
        self.config["default_duplex"] = self.default_duplex_check.isChecked()
        
        # Desteklenen dosya türlerini güncelle
        supported_extensions = []
        for i in range(self.file_types_list.count()):
            supported_extensions.append(self.file_types_list.item(i).text())
        self.config["supported_extensions"] = supported_extensions
        
        # İletişim kutusunu kapat
        super().accept()
    
    def get_config(self):
        """Güncellenmiş yapılandırmayı döndürür"""
        return self.config