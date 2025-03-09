#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MUKAprint - Otomatik Yazdırma Hizmeti
Belge işleme ve yazdırma modülü
"""

import os
import sys
import tempfile
import win32print
import win32api
import win32con
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, QDateTime

# Belge işleme kütüphaneleri
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image


class DocumentProcessor(QObject):
    """Belge işleme ve yazdırma işlevlerini sağlayan sınıf"""
    
    # Yazdırma durumu sinyalleri
    print_started = Signal(str, str)  # dosya_yolu, yazıcı_adı
    print_completed = Signal(str, bool)  # dosya_yolu, başarılı_mı
    print_error = Signal(str, str)  # dosya_yolu, hata_mesajı
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.print_history = []
        self.history_limit = config.get("history_limit", 100)
    
    def get_available_printers(self):
        """Sistemde kullanılabilir yazıcıların listesini döndürür"""
        printers = []
        for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
            printers.append({
                "name": printer[2],
                "is_default": printer[2] == win32print.GetDefaultPrinter()
            })
        return printers
    
    def get_available_paper_sizes(self, printer_name=None):
        """Belirtilen yazıcı için kullanılabilir kağıt boyutlarını döndürür"""
        # Temel kağıt boyutları
        paper_sizes = [
            {"name": "A4", "value": win32con.DMPAPER_A4},
            {"name": "A5", "value": win32con.DMPAPER_A5},
            {"name": "Letter", "value": win32con.DMPAPER_LETTER},
            {"name": "Legal", "value": win32con.DMPAPER_LEGAL}
        ]
        
        # İleri seviye: Yazıcıya özel kağıt boyutlarını almak için
        # Bu kısım daha karmaşık olduğu için şimdilik temel boyutları döndürüyoruz
        return paper_sizes
    
    def print_document(self, file_path, printer_name=None, paper_size=None, copies=None, duplex=None):
        """Belgeyi belirtilen ayarlarla yazdırır"""
        try:
            # Yapılandırmadan varsayılan değerleri al
            if printer_name is None:
                printer_name = self.config.get("default_printer", win32print.GetDefaultPrinter())
            
            if paper_size is None:
                paper_size = self.config.get("default_paper_size", "A4")
            
            if copies is None:
                copies = self.config.get("default_copies", 1)
            
            if duplex is None:
                duplex = self.config.get("default_duplex", False)
            
            # Yazdırma başladı sinyali gönder
            self.print_started.emit(file_path, printer_name)
            
            # Dosya uzantısına göre yazdırma işlemini gerçekleştir
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == ".pdf":
                success = self._print_pdf(file_path, printer_name, paper_size, copies, duplex)
            elif ext == ".docx":
                success = self._print_docx(file_path, printer_name, paper_size, copies, duplex)
            elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
                success = self._print_image(file_path, printer_name, paper_size, copies, duplex)
            elif ext in [".txt"]:
                success = self._print_text(file_path, printer_name, paper_size, copies, duplex)
            else:
                # Desteklenmeyen dosya türü için Windows'un varsayılan yazdırma işlemini kullan
                success = self._print_generic(file_path, printer_name, copies)
            
            # Yazdırma geçmişine ekle
            self._add_to_history(file_path, printer_name, success)
            
            # Yazdırma tamamlandı sinyali gönder
            self.print_completed.emit(file_path, success)
            
            return success
            
        except Exception as e:
            error_msg = str(e)
            print(f"Yazdırma hatası: {error_msg}")
            self.print_error.emit(file_path, error_msg)
            self._add_to_history(file_path, printer_name, False, error_msg)
            return False
    
    def _print_pdf(self, file_path, printer_name, paper_size, copies, duplex):
        """PDF belgesini yazdırır"""
        try:
            # PDF dosyasının varlığını kontrol et
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF dosyası bulunamadı: {file_path}")
            
            # PyPDF2 ile PDF dosyasını aç ve sayfa sayısını kontrol et
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                page_count = len(pdf_reader.pages)
                print(f"PDF dosyası açıldı: {file_path}, {page_count} sayfa")
            
            # Alternatif yazdırma yöntemi kullan
            # ShellExecute yerine doğrudan win32print kullan
            try:
                # Yazıcının varlığını kontrol et
                printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                if printer_name not in printers:
                    raise ValueError(f"Yazıcı bulunamadı: {printer_name}")
                
                # Yazıcı bağlantısını aç
                hPrinter = win32print.OpenPrinter(printer_name)
                try:
                    # Yazdırma işi başlat
                    hJob = win32print.StartDocPrinter(hPrinter, 1, (os.path.basename(file_path), None, "RAW"))
                    try:
                        # PDF dosyasını doğrudan yazdırmak için GhostScript veya başka bir PDF işleyici gerekebilir
                        # Şimdilik dosyayı doğrudan yazıcıya göndermeyi deneyelim
                        for i in range(copies):
                            # Dosyayı oku
                            with open(file_path, 'rb') as f:
                                data = f.read()
                                # Yazıcıya gönder
                                win32print.StartPagePrinter(hPrinter)
                                win32print.WritePrinter(hPrinter, data)
                                win32print.EndPagePrinter(hPrinter)
                        return True
                    finally:
                        win32print.EndDocPrinter(hPrinter)
                finally:
                    win32print.ClosePrinter(hPrinter)
            except Exception as e:
                print(f"PDF doğrudan yazdırma hatası: {e}")
                # Doğrudan yazdırma başarısız olursa, alternatif yöntem olarak varsayılan yazdırma işlemini dene
                print("Alternatif yazdırma yöntemi deneniyor...")
                return self._print_generic_alternative(file_path, printer_name, copies)
            
        except FileNotFoundError as fnf:
            print(f"PDF dosyası hatası: {fnf}")
            return False
        except Exception as e:
            print(f"PDF yazdırma hatası: {e}")
            return False
    
    def _print_docx(self, file_path, printer_name, paper_size, copies, duplex):
        """Word belgesini yazdırır"""
        # Windows'un varsayılan Word yazdırma işlemini kullan
        return self._print_generic(file_path, printer_name, copies)
    
    def _print_image(self, file_path, printer_name, paper_size, copies, duplex):
        """Görüntü dosyasını yazdırır"""
        # Windows'un varsayılan görüntü yazdırma işlemini kullan
        return self._print_generic(file_path, printer_name, copies)
    
    def _print_text(self, file_path, printer_name, paper_size, copies, duplex):
        """Metin dosyasını yazdırır"""
        # Windows'un varsayılan metin yazdırma işlemini kullan
        return self._print_generic(file_path, printer_name, copies)
    
    def _print_generic(self, file_path, printer_name, copies=1):
        """Windows'un varsayılan yazdırma işlemini kullanarak belgeyi yazdırır"""
        try:
            # Dosyanın varlığını kontrol et
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
                
            # Yazıcının varlığını kontrol et
            printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            if printer_name not in printers:
                raise ValueError(f"Yazıcı bulunamadı: {printer_name}")
            
            # Varsayılan yazıcıyı geçici olarak değiştir
            current_printer = win32print.GetDefaultPrinter()
            win32print.SetDefaultPrinter(printer_name)
            
            try:
                # Belgeyi yazdır
                for i in range(copies):
                    try:
                        win32api.ShellExecute(
                            0, "print", file_path, None, ".", 0
                        )
                    except Exception as print_error:
                        print(f"Kopya {i+1} yazdırılırken hata: {print_error}")
                        raise
                
                return True
            finally:
                # Varsayılan yazıcıyı geri al
                try:
                    win32print.SetDefaultPrinter(current_printer)
                except Exception as reset_error:
                    print(f"Varsayılan yazıcı geri alınırken hata: {reset_error}")
                
        except FileNotFoundError as fnf:
            print(f"Dosya hatası: {fnf}")
            return False
        except ValueError as ve:
            print(f"Yazıcı hatası: {ve}")
            return False
        except Exception as e:
            print(f"Genel yazdırma hatası: {e}")
            print(f"Hata türü: {type(e).__name__}, Hata kodu: {getattr(e, 'winerror', 'Bilinmiyor')}")
            return False
    
    def _print_generic_alternative(self, file_path, printer_name, copies=1):
        """ShellExecute'e alternatif olarak belgeyi yazdırır"""
        try:
            # Dosyanın varlığını kontrol et
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
                
            # Yazıcının varlığını kontrol et
            printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            if printer_name not in printers:
                raise ValueError(f"Yazıcı bulunamadı: {printer_name}")
            
            # Varsayılan yazıcıyı geçici olarak değiştir
            current_printer = win32print.GetDefaultPrinter()
            win32print.SetDefaultPrinter(printer_name)
            
            try:
                # Alternatif yazdırma yöntemi: win32api.ShellExecute yerine subprocess kullan
                import subprocess
                for i in range(copies):
                    try:
                        # Yazdırma komutu oluştur
                        print_cmd = f'rundll32.exe printui.dll,PrintUIEntry /k /n "{printer_name}" "{file_path}"'
                        subprocess.run(print_cmd, shell=True, check=True)
                    except subprocess.SubprocessError as print_error:
                        print(f"Kopya {i+1} yazdırılırken hata: {print_error}")
                        raise
                
                return True
            finally:
                # Varsayılan yazıcıyı geri al
                try:
                    win32print.SetDefaultPrinter(current_printer)
                except Exception as reset_error:
                    print(f"Varsayılan yazıcı geri alınırken hata: {reset_error}")
                
        except FileNotFoundError as fnf:
            print(f"Dosya hatası: {fnf}")
            return False
        except ValueError as ve:
            print(f"Yazıcı hatası: {ve}")
            return False
        except Exception as e:
            print(f"Alternatif yazdırma hatası: {e}")
            print(f"Hata türü: {type(e).__name__}, Hata kodu: {getattr(e, 'winerror', 'Bilinmiyor')}")
            return False
    
    def _add_to_history(self, file_path, printer_name, success, error_msg=None):
        """Yazdırma işlemini geçmişe ekler"""
        history_item = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "printer_name": printer_name,
            "timestamp": QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "success": success
        }
        
        if error_msg:
            history_item["error"] = error_msg
        
        self.print_history.append(history_item)
        
        # Geçmiş limitini kontrol et
        if len(self.print_history) > self.history_limit:
            self.print_history = self.print_history[-self.history_limit:]
    
    def get_print_history(self):
        """Yazdırma geçmişini döndürür"""
        return self.print_history
    
    def clear_print_history(self):
        """Yazdırma geçmişini temizler"""
        self.print_history = []
        return True
    
    def _print_generic_alternative(self, file_path, printer_name, copies=1):
        """ShellExecute'e alternatif olarak belgeyi yazdırır"""
        try:
            # Dosyanın varlığını kontrol et
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
                
            # Yazıcının varlığını kontrol et
            printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            if printer_name not in printers:
                raise ValueError(f"Yazıcı bulunamadı: {printer_name}")
            
            # Varsayılan yazıcıyı geçici olarak değiştir
            current_printer = win32print.GetDefaultPrinter()
            win32print.SetDefaultPrinter(printer_name)
            
            try:
                # Alternatif yazdırma yöntemi: win32api.ShellExecute yerine subprocess kullan
                import subprocess
                for i in range(copies):
                    try:
                        # Yazdırma komutu oluştur
                        print_cmd = f'rundll32.exe printui.dll,PrintUIEntry /k /n "{printer_name}" "{file_path}"'
                        subprocess.run(print_cmd, shell=True, check=True)
                    except subprocess.SubprocessError as print_error:
                        print(f"Kopya {i+1} yazdırılırken hata: {print_error}")
                        raise
                
                return True
            finally:
                # Varsayılan yazıcıyı geri al
                try:
                    win32print.SetDefaultPrinter(current_printer)
                except Exception as reset_error:
                    print(f"Varsayılan yazıcı geri alınırken hata: {reset_error}")
                
        except FileNotFoundError as fnf:
            print(f"Dosya hatası: {fnf}")
            return False
        except ValueError as ve:
            print(f"Yazıcı hatası: {ve}")
            return False
        except Exception as e:
            print(f"Alternatif yazdırma hatası: {e}")
            print(f"Hata türü: {type(e).__name__}, Hata kodu: {getattr(e, 'winerror', 'Bilinmiyor')}")
            return False
    
    def get_document_info(self, file_path):
        """Belge hakkında temel bilgileri döndürür"""
        try:
            file_info = {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path),
                "file_type": os.path.splitext(file_path)[1].lower(),
                "last_modified": os.path.getmtime(file_path)
            }
            
            # Dosya türüne göre ek bilgiler ekle
            ext = file_info["file_type"]
            
            if ext == ".pdf":
                with open(file_path, "rb") as f:
                    pdf = PdfReader(f)
                    file_info["page_count"] = len(pdf.pages)
            
            elif ext == ".docx":
                doc = Document(file_path)
                file_info["page_count"] = len(doc.sections)  # Yaklaşık değer
            
            elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
                img = Image.open(file_path)
                file_info["dimensions"] = f"{img.width}x{img.height}"
                file_info["format"] = img.format
            
            return file_info
            
        except Exception as e:
            print(f"Belge bilgisi alınırken hata: {e}")
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "error": str(e)
            }