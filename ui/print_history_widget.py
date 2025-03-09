#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MUKAprint - Otomatik Yazdırma Hizmeti
Yazdırma geçmişi widget modülü
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QIcon, QColor, QBrush, QFont
import qtawesome as qta


class PrintHistoryWidget(QWidget):
    """Yazdırma geçmişi widget'ı"""
    
    def __init__(self, document_processor):
        super().__init__()
        self.document_processor = document_processor
        self.init_ui()
        
        # Yazdırma tamamlandı sinyalini bağla
        self.document_processor.print_completed.connect(self.on_print_completed)
    
    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        layout = QVBoxLayout(self)
        
        # Başlık
        title_layout = QHBoxLayout()
        title_label = QLabel("Yazdırma Geçmişi")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_layout.addWidget(title_label)
        
        # Temizle düğmesi
        clear_button = QPushButton("Geçmişi Temizle")
        clear_button.setIcon(QIcon(qta.icon('fa5s.trash-alt', color='red')))
        clear_button.clicked.connect(self.clear_history)
        title_layout.addWidget(clear_button)
        
        layout.addLayout(title_layout)
        
        # Geçmiş tablosu
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Dosya Adı", "Yazıcı", "Tarih/Saat", "Durum"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table_widget)
        
        # Durum etiketi
        self.status_label = QLabel("Yazdırma geçmişi boş")
        layout.addWidget(self.status_label)
        
        # Geçmişi yükle
        self.load_history()
    
    def load_history(self):
        """Yazdırma geçmişini yükler"""
        history = self.document_processor.get_print_history()
        self.table_widget.setRowCount(0)  # Tabloyu temizle
        
        for item in history:
            self.add_history_item(item)
        
        # Durum etiketini güncelle
        self.update_status_label()
    
    def add_history_item(self, item):
        """Geçmiş tablosuna yeni bir öğe ekler"""
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)
        
        # Dosya adı
        file_name_item = QTableWidgetItem(item["file_name"])
        file_name_item.setToolTip(item["file_path"])
        self.table_widget.setItem(row, 0, file_name_item)
        
        # Yazıcı adı
        printer_item = QTableWidgetItem(item["printer_name"])
        self.table_widget.setItem(row, 1, printer_item)
        
        # Tarih/Saat
        time_item = QTableWidgetItem(item["timestamp"])
        self.table_widget.setItem(row, 2, time_item)
        
        # Durum
        status_text = "Başarılı" if item["success"] else "Hata"
        status_item = QTableWidgetItem(status_text)
        
        if item["success"]:
            status_item.setForeground(QBrush(QColor("green")))
        else:
            status_item.setForeground(QBrush(QColor("red")))
            if "error" in item:
                status_item.setToolTip(item["error"])
        
        self.table_widget.setItem(row, 3, status_item)
        
        # Durum etiketini güncelle
        self.update_status_label()
    
    def on_print_completed(self, file_path, success):
        """Yazdırma tamamlandığında çağrılır"""
        # Geçmişi yeniden yükle
        self.load_history()
    
    def clear_history(self):
        """Yazdırma geçmişini temizler"""
        self.document_processor.clear_print_history()
        self.table_widget.setRowCount(0)
        self.status_label.setText("Yazdırma geçmişi boş")
    
    def update_status_label(self):
        """Durum etiketini günceller"""
        count = self.table_widget.rowCount()
        if count > 0:
            self.status_label.setText(f"{count} yazdırma işlemi listelendi")
        else:
            self.status_label.setText("Yazdırma geçmişi boş")