#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MUKAprint - Otomatik Yazdırma Hizmeti
Dosya listesi widget modülü
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QPushButton, QHBoxLayout, QMenu, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QColor, QBrush, QFont
import qtawesome as qta


class FileListWidget(QWidget):
    """Dosya listesi widget'ı"""
    
    def __init__(self, document_processor):
        super().__init__()
        self.document_processor = document_processor
        self.files = {}  # Dosya yolu -> ListWidgetItem eşlemesi
        self.init_ui()
    
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        layout = QVBoxLayout(self)
        
        # Başlık
        title_layout = QHBoxLayout()
        title_label = QLabel("Dosya Listesi")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_layout.addWidget(title_label)
        
        # Temizle düğmesi
        clear_button = QPushButton("Listeyi Temizle")
        clear_button.setIcon(QIcon(qta.icon('fa5s.trash-alt', color='red')))
        clear_button.clicked.connect(self.clear_list)
        title_layout.addWidget(clear_button)
        
        layout.addLayout(title_layout)
        
        # Dosya listesi
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)
        
        # Durum etiketi
        self.status_label = QLabel("Hazır")
        layout.addWidget(self.status_label)
    
    def add_file(self, file_path):
        """Dosya listesine yeni bir dosya ekler"""
        if file_path in self.files:
            # Dosya zaten listede, güncelle
            item = self.files[file_path]
            item.setText(os.path.basename(file_path))
            item.setToolTip(file_path)
            return
        
        # Yeni dosya öğesi oluştur
        item = QListWidgetItem(os.path.basename(file_path))
        item.setToolTip(file_path)
        item.setIcon(self._get_file_icon(file_path))
        
        # Dosyayı listeye ekle
        self.list_widget.addItem(item)
        self.files[file_path] = item
        
        # Durum etiketini güncelle
        self.status_label.setText(f"{len(self.files)} dosya listelendi")
    
    def mark_file_printing(self, file_path):
        """Dosyayı yazdırılıyor olarak işaretler"""
        if file_path in self.files:
            item = self.files[file_path]
            item.setForeground(QBrush(QColor("orange")))
            item.setText(f"{os.path.basename(file_path)} (Yazdırılıyor...)")
    
    def mark_file_printed(self, file_path, success=True):
        """Dosyayı yazdırıldı olarak işaretler"""
        if file_path in self.files:
            item = self.files[file_path]
            if success:
                item.setForeground(QBrush(QColor("green")))
                item.setText(f"{os.path.basename(file_path)} (Yazdırıldı)")
            else:
                item.setForeground(QBrush(QColor("red")))
                item.setText(f"{os.path.basename(file_path)} (Hata)")
    
    def remove_file(self, file_path):
        """Dosyayı listeden kaldırır"""
        if file_path in self.files:
            item = self.files[file_path]
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)
            del self.files[file_path]
            
            # Durum etiketini güncelle
            self.status_label.setText(f"{len(self.files)} dosya listelendi")
    
    def clear_list(self):
        """Tüm dosya listesini temizler"""
        self.list_widget.clear()
        self.files = {}
        self.status_label.setText("Hazır")
    
    def get_selected_files(self):
        """Seçili dosyaların yollarını döndürür"""
        selected_files = []
        for item in self.list_widget.selectedItems():
            for file_path, file_item in self.files.items():
                if file_item == item:
                    selected_files.append(file_path)
                    break
        return selected_files
    
    def get_all_files(self):
        """Tüm dosyaların yollarını döndürür"""
        return list(self.files.keys())
    
    def show_context_menu(self, position):
        """Sağ tıklama menüsünü gösterir"""
        menu = QMenu()
        
        # Seçili öğe var mı kontrol et
        if self.list_widget.selectedItems():
            # Yazdır seçeneği
            print_action = menu.addAction(QIcon(qta.icon('fa5s.print')), "Yazdır")
            print_action.triggered.connect(self._print_selected)
            
            # Kaldır seçeneği
            remove_action = menu.addAction(QIcon(qta.icon('fa5s.trash')), "Listeden Kaldır")
            remove_action.triggered.connect(self._remove_selected)
            
            menu.addSeparator()
        
        # Tümünü seç seçeneği
        select_all_action = menu.addAction("Tümünü Seç")
        select_all_action.triggered.connect(self.list_widget.selectAll)
        
        # Listeyi temizle seçeneği
        clear_action = menu.addAction(QIcon(qta.icon('fa5s.trash-alt')), "Listeyi Temizle")
        clear_action.triggered.connect(self.clear_list)
        
        # Menüyü göster
        menu.exec(self.list_widget.mapToGlobal(position))
    
    def _print_selected(self):
        """Seçili dosyaları yazdırır"""
        selected_files = self.get_selected_files()
        for file_path in selected_files:
            # Bu metod, ana penceredeki print_document metoduna bağlanmalı
            # Şimdilik doğrudan document_processor'ı kullanıyoruz
            self.document_processor.print_document(file_path)
    
    def _remove_selected(self):
        """Seçili dosyaları listeden kaldırır"""
        selected_files = self.get_selected_files()
        for file_path in selected_files:
            self.remove_file(file_path)
    
    def _get_file_icon(self, file_path):
        """Dosya türüne göre ikon döndürür"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return QIcon(qta.icon('fa5s.file-pdf', color='#e74c3c'))
        elif ext in [".doc", ".docx"]:
            return QIcon(qta.icon('fa5s.file-word', color='#3498db'))
        elif ext in [".xls", ".xlsx"]:
            return QIcon(qta.icon('fa5s.file-excel', color='#2ecc71'))
        elif ext in [".ppt", ".pptx"]:
            return QIcon(qta.icon('fa5s.file-powerpoint', color='#e67e22'))
        elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
            return QIcon(qta.icon('fa5s.file-image', color='#9b59b6'))
        elif ext == ".txt":
            return QIcon(qta.icon('fa5s.file-alt', color='#7f8c8d'))
        else:
            return QIcon(qta.icon('fa5s.file', color='#95a5a6'))