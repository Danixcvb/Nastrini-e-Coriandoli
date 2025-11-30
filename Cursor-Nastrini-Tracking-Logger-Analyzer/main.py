#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite Database Analyzer - Nastrini Tracking Logger Analyzer
Analizza dati da database SQLite con struttura gerarchica NodeId -> ConveyorID -> PhotocellID
"""

import sys
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTreeWidget, QTreeWidgetItem, QFileDialog, QLabel, QLineEdit,
        QCheckBox, QPushButton, QMessageBox, QHeaderView
    )
    from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
    from PyQt5.QtGui import QFont, QColor, QBrush, QPainter, QLinearGradient, QPen
except ImportError:
    print("PyQt5 non trovato. Installazione in corso...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTreeWidget, QTreeWidgetItem, QFileDialog, QLabel, QLineEdit,
        QCheckBox, QPushButton, QMessageBox, QHeaderView
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QColor, QBrush


class CustomTitleBar(QWidget):
    """Barra del titolo personalizzata"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.dragging = False
        self.drag_position = QPoint()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gradiente elegante per la barra del titolo
        gradient = QLinearGradient(0, 0, 0, self.height())
        if self.parent.dark_mode:
            gradient.setColorAt(0, QColor(25, 25, 30))
            gradient.setColorAt(1, QColor(20, 20, 25))
        else:
            gradient.setColorAt(0, QColor(255, 255, 255))
            gradient.setColorAt(1, QColor(248, 249, 250))
        
        painter.fillRect(self.rect(), gradient)
        
        # Bordo inferiore elegante
        pen = QPen(QColor(255, 215, 0, 100) if self.parent.dark_mode else QColor(74, 144, 226, 80), 1)
        painter.setPen(pen)
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)


class TitleBarButton(QPushButton):
    """Pulsanti personalizzati per la barra del titolo"""
    def __init__(self, icon_text, parent):
        super().__init__(icon_text, parent)
        self.setFixedSize(40, 40)
        self.hover = False
        self.main_window = None  # Sarà impostato dopo
        
    def set_main_window(self, main_window):
        """Imposta il riferimento alla finestra principale"""
        self.main_window = main_window
        
    def enterEvent(self, event):
        self.hover = True
        self.update()
        
    def leaveEvent(self, event):
        self.hover = False
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        dark_mode = self.main_window.dark_mode if self.main_window else False
        
        if self.hover:
            painter.fillRect(self.rect(), QColor(255, 255, 255, 30) if dark_mode else QColor(0, 0, 0, 10))
        
        painter.setPen(QColor(255, 255, 255) if dark_mode else QColor(60, 60, 70))
        font = QFont("Segoe UI", 14)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())


class DatabaseAnalyzer(QMainWindow):
    """Finestra principale dell'applicazione"""
    
    CONFIG_FILE = "last_file.json"
    
    def __init__(self):
        super().__init__()
        self.db_path = None
        self.conn = None
        self.slot_length = 4.0
        self.slot_length_enabled = False
        self.dark_mode = True  # Tema scuro di default
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.init_ui()
        self.load_default_database()
        
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.setWindowTitle("Nastrini Tracking Logger Analyzer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Font raffinato
        self.setFont(QFont("Segoe UI", 9))
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # Barra del titolo custom
        self.title_bar = CustomTitleBar(self)
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar_layout.setSpacing(0)
        self.title_bar.setLayout(title_bar_layout)
        
        # Pulsanti barra del titolo
        self.minimize_btn = TitleBarButton("−", self.title_bar)
        self.minimize_btn.set_main_window(self)
        self.minimize_btn.clicked.connect(self.showMinimized)
        
        self.maximize_btn = TitleBarButton("□", self.title_bar)
        self.maximize_btn.set_main_window(self)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = TitleBarButton("×", self.title_bar)
        self.close_btn.set_main_window(self)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
        """)
        
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(self.minimize_btn)
        title_bar_layout.addWidget(self.maximize_btn)
        title_bar_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(self.title_bar)
        
        # Header elegante con gradiente
        header_widget = QWidget()
        header_widget.setFixedHeight(70)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 15, 30, 15)
        header_widget.setLayout(header_layout)
        
        # Titolo elegante e discreto
        title_label = QLabel("Nastrini Tracking Logger")
        title_label.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 20pt;
                font-weight: 300;
                color: #FFD700;
                background: transparent;
                letter-spacing: 1px;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Pulsante toggle tema elegante
        self.theme_button = QPushButton("☀")
        self.theme_button.setFixedSize(44, 44)
        self.theme_button.setStyleSheet("""
            QPushButton {
                font-size: 20pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD700, stop:1 #FFC700);
                color: #1a1a1a;
                border: none;
                border-radius: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFED4E, stop:1 #FFD700);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFC700, stop:1 #FFB700);
            }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button)
        
        main_layout.addWidget(header_widget)
        
        # Container per il contenuto principale con glassmorphism
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_widget.setLayout(content_layout)
        
        # Barra superiore con selezione file e SlotLength - Glass effect
        top_bar = QHBoxLayout()
        top_bar.setSpacing(20)
        
        # Selezione file con glass effect
        file_label = QLabel("Database SQLite:")
        file_label.setObjectName("fileLabel")
        self.file_path_label = QLabel("Nessun file selezionato")
        self.file_path_label.setObjectName("filePathLabel")
        self.file_path_label.setMinimumWidth(350)
        self.file_path_label.setMinimumHeight(38)
        browse_button = QPushButton("Sfoglia...")
        browse_button.setObjectName("browseButton")
        browse_button.setMinimumHeight(38)
        browse_button.clicked.connect(self.browse_database)
        
        top_bar.addWidget(file_label)
        top_bar.addWidget(self.file_path_label)
        top_bar.addWidget(browse_button)
        top_bar.addStretch()
        
        # SlotLength con glass effect
        slot_label = QLabel("SlotLength (cm):")
        slot_label.setObjectName("slotLabel")
        self.slot_length_input = QLineEdit()
        self.slot_length_input.setObjectName("slotInput")
        self.slot_length_input.setMaximumWidth(120)
        self.slot_length_input.setMinimumHeight(38)
        self.slot_length_input.setText("4")
        self.slot_length_input.textChanged.connect(self.on_slot_length_changed)
        
        self.slot_length_checkbox = QCheckBox("Abilita")
        self.slot_length_checkbox.setObjectName("slotCheckbox")
        self.slot_length_checkbox.setMinimumHeight(38)
        self.slot_length_checkbox.stateChanged.connect(self.on_slot_length_enabled_changed)
        
        top_bar.addWidget(slot_label)
        top_bar.addWidget(self.slot_length_input)
        top_bar.addWidget(self.slot_length_checkbox)
        
        content_layout.addLayout(top_bar)
        
        # Tree widget per i dati gerarchici con glass effect
        self.tree_widget = QTreeWidget()
        self.tree_widget.setObjectName("treeWidget")
        self.tree_widget.setHeaderLabels([
            "ITEM", "Offset (media)", "MaxOffset+", "MaxOffset-", 
            "DimX"
        ])
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setRootIsDecorated(True)
        self.tree_widget.setExpandsOnDoubleClick(True)
        
        # Imposta larghezza colonne e altezza header
        header = self.tree_widget.header()
        header.setFixedHeight(36)  # Altezza fissa per l'header
        header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # Centra il testo
        # Tutte le colonne con larghezza uguale e equidistribuite
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        content_layout.addWidget(self.tree_widget)
        
        # Connetti il segnale di selezione per rimuovere gli sfondi per colonna quando selezionato
        self.tree_widget.itemSelectionChanged.connect(self.on_item_selection_changed)
        
        main_layout.addWidget(content_widget)
        
        # Status bar
        self.statusBar().setObjectName("statusBar")
        self.statusBar().showMessage("Pronto")
        
        # Applica tema iniziale
        self.apply_theme()
        
        # Forza l'aggiornamento dell'header dopo l'applicazione del tema
        if hasattr(self, 'tree_widget'):
            header = self.tree_widget.header()
            header.setFixedHeight(36)  # Assicura che l'altezza sia corretta
            header.setDefaultAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # Assicura che il testo sia centrato
            header.setStyleSheet(header.styleSheet())  # Forza il refresh dello stile
            # Assicura che tutte le colonne abbiano larghezza uguale
            for i in range(5):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            header.update()
            header.repaint()  # Forza il ridisegno
    
    def toggle_maximize(self):
        """Toggle tra massimizzato e normale"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")
        
    def apply_modern_style(self):
        """Applica uno stile moderno all'applicazione"""
        pass  # Lo stile viene applicato da apply_theme()
    
    def toggle_theme(self):
        """Cambia tra tema chiaro e scuro"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
    
    def apply_theme(self):
        """Applica il tema corrente con gradienti eleganti e liquid glass"""
        if self.dark_mode:
            # Tema scuro cyberpunk con gradienti
            bg_gradient_start = "#0f0f14"
            bg_gradient_end = "#1a1a20"
            bg_glass = "rgba(42, 42, 50, 0.85)"
            text_primary = "#FFD700"
            text_secondary = "#ffffff"
            text_muted = "#b0b0b0"
            accent_gradient_start = "#FFD700"
            accent_gradient_end = "#FFC700"
            # Colori selezione più scuri e meno saturi
            selection_gradient_start = "#D4B800"  # Più scuro e meno saturo di #FFD700
            selection_gradient_end = "#B89A00"    # Più scuro e meno saturo di #FFC700
            selection_text = "#1a1a1a"
            border_glow = "#FFD700"
            input_glass = "rgba(60, 60, 70, 0.6)"
            header_gradient_start = "#1a1a1f"
            header_gradient_end = "#25252a"
            row_alt_bg = "rgba(50, 50, 60, 0.4)"  # Sfondo alternato più chiaro per contrasto
            self.theme_button.setText("☾")
        else:
            # Tema chiaro elegante con gradienti
            bg_gradient_start = "#f8f9fa"
            bg_gradient_end = "#e9ecef"
            bg_glass = "rgba(255, 255, 255, 0.7)"
            text_primary = "#212529"
            text_secondary = "#495057"
            text_muted = "#6c757d"
            accent_gradient_start = "#4a90e2"
            accent_gradient_end = "#357abd"
            # Colori selezione più scuri e meno saturi
            selection_gradient_start = "#3d7bc4"  # Più scuro e meno saturo di #4a90e2
            selection_gradient_end = "#2d5a8f"    # Più scuro e meno saturo di #357abd
            selection_text = "#ffffff"
            border_glow = "#4a90e2"
            input_glass = "rgba(255, 255, 255, 0.9)"
            header_gradient_start = "#ffffff"
            header_gradient_end = "#f8f9fa"
            row_alt_bg = "rgba(248, 249, 250, 0.5)"  # Colore alternato per tema chiaro
            self.theme_button.setText("☀")
        
        # Stile principale con gradiente di sfondo
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {bg_gradient_start}, stop:1 {bg_gradient_end});
            }}
             QWidget#contentWidget {{
                 background: {bg_glass};
                 border-radius: 0px;
                 border: 1px solid rgba(255, 255, 255, 0.1);
             }}
        """)
        
        # Titolo elegante
        for widget in self.findChildren(QLabel):
            if "Nastrini Tracking Logger" in widget.text():
                widget.setStyleSheet(f"""
                    QLabel {{
                        font-family: 'Segoe UI', 'Inter', sans-serif;
                        font-size: 20pt;
                        font-weight: 300;
                        color: {text_primary};
                        background: transparent;
                        letter-spacing: 1px;
                    }}
                """)
        
        # Header con gradiente
        for widget in self.findChildren(QWidget):
            if widget.height() == 70:
                widget.setStyleSheet(f"""
                    QWidget {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {header_gradient_start}, stop:1 {header_gradient_end});
                        border: none;
                    }}
                """)
        
        # Pulsante tema con gradiente e glass effect
        self.theme_button.setStyleSheet(f"""
            QPushButton {{
                font-size: 20pt;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {accent_gradient_start}, stop:1 {accent_gradient_end});
                color: {"#1a1a1a" if self.dark_mode else "#ffffff"};
                border: none;
                border-radius: 22px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {"#FFED4E" if self.dark_mode else "#5ba0f2"}, 
                    stop:1 {"#FFD700" if self.dark_mode else "#4a90e2"});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {"#FFC700" if self.dark_mode else "#357abd"}, 
                    stop:1 {"#FFB700" if self.dark_mode else "#2a5f8f"});
            }}
        """)
        
        # Labels con font raffinato
        for widget in self.findChildren(QLabel):
            if widget.objectName() in ["fileLabel", "slotLabel"]:
                widget.setStyleSheet(f"""
                    QLabel {{
                        font-family: 'Segoe UI', 'Inter', sans-serif;
                        font-size: 11pt;
                        font-weight: 500;
                        color: {text_primary};
                        background: transparent;
                    }}
                """)
        
        # File path label con glass effect
        self.file_path_label.setStyleSheet(f"""
            QLabel {{
                background: {input_glass};
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 14px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 10pt;
                font-weight: 400;
                color: {text_secondary};
            }}
        """)
        
        # Browse button con gradiente elegante
        for btn in self.findChildren(QPushButton):
            if btn.objectName() == "browseButton":
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {accent_gradient_start}, stop:1 {accent_gradient_end});
                        color: {"#1a1a1a" if self.dark_mode else "#ffffff"};
                        border: none;
                        border-radius: 8px;
                        padding: 8px 24px;
                        font-family: 'Segoe UI', 'Inter', sans-serif;
                        font-size: 10pt;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {"#FFED4E" if self.dark_mode else "#5ba0f2"}, 
                            stop:1 {"#FFD700" if self.dark_mode else "#4a90e2"});
                    }}
                    QPushButton:pressed {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {"#FFC700" if self.dark_mode else "#357abd"}, 
                            stop:1 {"#FFB700" if self.dark_mode else "#2a5f8f"});
                    }}
                """)
        
        # SlotLength input con glass effect
        self.slot_length_input.setStyleSheet(f"""
            QLineEdit {{
                background: {input_glass};
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 14px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 10pt;
                font-weight: 400;
                color: {text_secondary};
            }}
            QLineEdit:focus {{
                border: 2px solid {border_glow};
                background: {"rgba(80, 80, 90, 0.8)" if self.dark_mode else "rgba(255, 255, 255, 0.95)"};
            }}
        """)
        
        # Checkbox elegante
        self.slot_length_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 10pt;
                font-weight: 400;
                color: {text_primary};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {text_muted};
                border-radius: 4px;
                background: {input_glass};
            }}
            QCheckBox::indicator:checked {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {accent_gradient_start}, stop:1 {accent_gradient_end});
                border-color: {border_glow};
            }}
            QCheckBox::indicator:hover {{
                border-color: {border_glow};
            }}
        """)
        
        # Tree widget con glass effect e gradiente header
        self.tree_widget.setStyleSheet(f"""
            QTreeWidget {{
                background: {input_glass};
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 10pt;
                font-weight: 400;
                color: {text_secondary};
                gridline-color: {"rgba(255, 255, 255, 0.1)" if self.dark_mode else "rgba(0, 0, 0, 0.08)"};
                selection-background-color: {accent_gradient_start};
                alternate-background-color: {row_alt_bg};
            }}
            QTreeWidget::item {{
                padding: 6px;
                border: none;
                min-height: 28px;
                color: {text_secondary};
            }}
            QTreeWidget::item:hover {{
                background: {"rgba(255, 255, 255, 0.08)" if self.dark_mode else "rgba(74, 144, 226, 0.08)"};
            }}
             QTreeWidget::item:selected {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {selection_gradient_start}, stop:1 {selection_gradient_end});
                 color: {selection_text};
             }}
             QTreeWidget::item:selected:!active {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {selection_gradient_start}, stop:1 {selection_gradient_end});
                 color: {selection_text};
             }}
             QTreeWidget::branch:selected {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {selection_gradient_start}, stop:1 {selection_gradient_end});
             }}
             QTreeWidget::branch:has-siblings:!adjoins-item:selected {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {selection_gradient_start}, stop:1 {selection_gradient_end});
             }}
             QTreeWidget::branch:has-siblings:adjoins-item:selected {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {selection_gradient_start}, stop:1 {selection_gradient_end});
             }}
             QTreeWidget::branch:has-children:!has-siblings:closed:selected,
             QTreeWidget::branch:closed:has-children:has-siblings:selected {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {selection_gradient_start}, stop:1 {selection_gradient_end});
             }}
             QTreeWidget::branch:open:has-children:!has-siblings:selected,
             QTreeWidget::branch:open:has-children:has-siblings:selected {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {selection_gradient_start}, stop:1 {selection_gradient_end});
             }}
             QHeaderView {{
                 background: transparent;
                 min-height: 36px;
                 max-height: 36px;
             }}
             QHeaderView::section {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {accent_gradient_start}, stop:0.5 {accent_gradient_start}, stop:1 {accent_gradient_end});
                 color: {"#1a1a1a" if self.dark_mode else "#ffffff"};
                 padding: 8px 12px;
                 border: none;
                 border-right: 2px solid {"rgba(0, 0, 0, 0.15)" if self.dark_mode else "rgba(255, 255, 255, 0.25)"};
                 font-family: 'Segoe UI', 'Inter', sans-serif;
                 font-size: 10pt;
                 font-weight: 600;
                 letter-spacing: 0.8px;
                 text-transform: uppercase;
                 min-height: 36px;
                 max-height: 36px;
             }}
             QHeaderView::section:first {{
                 border-top-left-radius: 0px;
             }}
             QHeaderView::section:last {{
                 border-top-right-radius: 0px;
                 border-right: none;
             }}
             QHeaderView::section:hover {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {"#FFED4E" if self.dark_mode else "#5ba0f2"}, 
                     stop:0.5 {"#FFE55C" if self.dark_mode else "#65a8f5"},
                     stop:1 {"#FFD700" if self.dark_mode else "#4a90e2"});
             }}
             QHeaderView::section:pressed {{
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                     stop:0 {"#FFC700" if self.dark_mode else "#357abd"}, 
                     stop:1 {"#FFB700" if self.dark_mode else "#2a5f8f"});
             }}
        """)
        
        # Status bar con gradiente
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {header_gradient_start}, stop:1 {header_gradient_end});
                color: {text_secondary};
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 9pt;
                font-weight: 400;
            }}
        """)
        
        # Aggiorna i colori degli item esistenti
        self.update_item_colors()
    
    def on_item_selection_changed(self):
        """Rimuove gli sfondi per colonna quando un item è selezionato per permettere al gradiente CSS di funzionare"""
        selected_items = self.tree_widget.selectedItems()
        for item in selected_items:
            # Rimuovi gli sfondi per colonna per permettere al gradiente CSS di coprire tutta la riga
            for col in range(6):
                item.setBackground(col, QBrush())
        
        # Ripristina gli sfondi per gli item non selezionati
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            node_item = root.child(i)
            if node_item not in selected_items:
                self._restore_item_background(node_item)
            for j in range(node_item.childCount()):
                conveyor_item = node_item.child(j)
                if conveyor_item not in selected_items:
                    self._restore_item_background(conveyor_item)
                for k in range(conveyor_item.childCount()):
                    photocell_item = conveyor_item.child(k)
                    if photocell_item not in selected_items:
                        self._restore_item_background(photocell_item)
    
    def _restore_item_background(self, item):
        """Ripristina lo sfondo di un item in base al suo tipo"""
        if self.dark_mode:
            node_bg = QColor(60, 60, 70, 180)
            conveyor_bg = QColor(70, 70, 80, 150)
            alt_bg = QColor(50, 50, 60, 100)
        else:
            node_bg = QColor(230, 240, 255, 200)
            conveyor_bg = QColor(240, 248, 255, 180)
            alt_bg = QColor(248, 249, 250, 150)
        
        text = item.text(0)
        if "NodeId" in text:
            for col in range(6):
                item.setBackground(col, QBrush(node_bg))
        elif "ConveyorID" in text:
            for col in range(6):
                item.setBackground(col, QBrush(conveyor_bg))
        elif "PhotocellID" in text:
            # Per PhotocellID, applica colore alternato se necessario
            parent = item.parent()
            if parent:
                index = parent.indexOfChild(item)
                if index % 2 == 1 and self.dark_mode:
                    for col in range(6):
                        item.setBackground(col, QBrush(alt_bg))
    
    def update_item_colors(self):
        """Aggiorna i colori degli item nella tree view in base al tema"""
        if self.dark_mode:
            node_bg = QColor(60, 60, 70, 180)  # Con trasparenza per glass effect
            conveyor_bg = QColor(70, 70, 80, 150)
            node_fg = QColor(255, 215, 0)
            conveyor_fg = QColor(255, 235, 100)
            photocell_fg = QColor(255, 255, 255)
            alt_bg = QColor(50, 50, 60, 100)
        else:
            node_bg = QColor(230, 240, 255, 200)
            conveyor_bg = QColor(240, 248, 255, 180)
            node_fg = QColor(30, 60, 120)
            conveyor_fg = QColor(50, 100, 150)
            photocell_fg = QColor(60, 60, 70)
            alt_bg = QColor(248, 249, 250, 150)
        
        # Aggiorna i colori degli item esistenti (solo se non selezionati)
        root = self.tree_widget.invisibleRootItem()
        selected_items = self.tree_widget.selectedItems()
        
        for i in range(root.childCount()):
            node_item = root.child(i)
            if node_item not in selected_items:
                # NodeId con gradiente leggero
                for col in range(6):
                    node_item.setBackground(col, QBrush(node_bg))
            node_item.setForeground(0, QBrush(node_fg))
            
            for j in range(node_item.childCount()):
                conveyor_item = node_item.child(j)
                if conveyor_item not in selected_items:
                    # ConveyorID
                    for col in range(6):
                        conveyor_item.setBackground(col, QBrush(conveyor_bg))
                conveyor_item.setForeground(0, QBrush(conveyor_fg))
                
                for k in range(conveyor_item.childCount()):
                    photocell_item = conveyor_item.child(k)
                    if photocell_item not in selected_items:
                        # PhotocellID - applica colore alternato per contrasto
                        if k % 2 == 1 and self.dark_mode:
                            for col in range(6):
                                photocell_item.setBackground(col, QBrush(alt_bg))
                    photocell_item.setForeground(0, QBrush(photocell_fg))
        
    def load_default_database(self):
        """Carica il database di default (ultimo aperto o log01.sqlite)"""
        # Prova a caricare l'ultimo file aperto
        last_file = self.load_last_file()
        if last_file and os.path.exists(last_file):
            self.load_database(last_file)
        elif os.path.exists("log01.sqlite"):
            self.load_database("log01.sqlite")
        else:
            self.statusBar().showMessage("Nessun database trovato. Seleziona un file.")
            
    def load_last_file(self) -> Optional[str]:
        """Carica l'ultimo file aperto dal file di configurazione"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('last_file')
            except:
                return None
        return None
        
    def save_last_file(self, file_path: str):
        """Salva l'ultimo file aperto nel file di configurazione"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump({'last_file': file_path}, f)
        except:
            pass
            
    def browse_database(self):
        """Apre il dialog per selezionare un database"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona database SQLite",
            "",
            "SQLite Database (*.sqlite *.db);;All Files (*)"
        )
        
        if file_path:
            self.load_database(file_path)
            
    def load_database(self, file_path: str):
        """Carica e analizza il database"""
        try:
            self.db_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            self.save_last_file(file_path)
            
            # Connetti al database
            if self.conn:
                self.conn.close()
            self.conn = sqlite3.connect(file_path)
            
            # Analizza i dati
            self.analyze_data()
            
            self.statusBar().showMessage(f"Database caricato: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nel caricamento del database:\n{str(e)}"
            )
            self.statusBar().showMessage("Errore nel caricamento del database")
            
    def analyze_data(self):
        """Analizza i dati dal database e popola la tree view"""
        if not self.conn:
            return
            
        self.tree_widget.clear()
        
        try:
            cursor = self.conn.cursor()
            
            # Query per ottenere i dati aggregati per NodeId, ConveyorID, PhotocellID
            # Solo per EventType = 1
            query = """
                SELECT 
                    l.NodeId,
                    m.ConveyorID,
                    m.PhotocellID,
                    AVG(m.OffsetCtrl) as AvgOffset,
                    MAX(m.OffsetCtrl) as MaxOffset,
                    MIN(m.OffsetCtrl) as MinOffset,
                    AVG(m.DIM_X) as AvgDimX,
                    COUNT(*) as Count
                FROM Logs l
                JOIN Msg00101 m ON l.MsgNumber = m.MsgNumber
                WHERE l.MsgId = 101 AND m.EventType = 1
                GROUP BY l.NodeId, m.ConveyorID, m.PhotocellID
                ORDER BY l.NodeId, m.ConveyorID, m.PhotocellID
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Organizza i dati in una struttura gerarchica
            hierarchy: Dict[int, Dict[int, List[Tuple]]] = {}
            
            for row in rows:
                node_id, conveyor_id, photocell_id, avg_offset, max_offset, min_offset, avg_dim_x, count = row
                
                if node_id not in hierarchy:
                    hierarchy[node_id] = {}
                if conveyor_id not in hierarchy[node_id]:
                    hierarchy[node_id][conveyor_id] = []
                    
                hierarchy[node_id][conveyor_id].append((
                    photocell_id, avg_offset, max_offset, min_offset, avg_dim_x, count
                ))
            
            # Popola la tree view
            for node_id in sorted(hierarchy.keys()):
                node_item = QTreeWidgetItem(self.tree_widget)
                node_item.setText(0, f"NodeId: {node_id}")
                node_item.setExpanded(False)  # Inizia collassato
                # Colore per NodeId (verrà aggiornato da update_item_colors)
                font = QFont()
                font.setBold(True)
                font.setPointSize(10)
                node_item.setFont(0, font)
                # Applica font bold anche alle colonne numeriche
                for col in range(1, 5):
                    node_item.setFont(col, font)
                
                # Calcola totali per NodeId usando query diretta
                node_totals = self.calculate_node_totals_from_db(cursor, node_id)
                self.set_item_values(node_item, node_totals)
                
                for conveyor_id in sorted(hierarchy[node_id].keys()):
                    conveyor_item = QTreeWidgetItem(node_item)
                    conveyor_item.setText(0, f"ConveyorID: {conveyor_id}")
                    conveyor_item.setExpanded(False)  # Inizia collassato
                    # Colore per ConveyorID (verrà aggiornato da update_item_colors)
                    font2 = QFont()
                    font2.setBold(True)
                    font2.setPointSize(9)
                    conveyor_item.setFont(0, font2)
                    # Applica font bold anche alle colonne numeriche
                    for col in range(1, 5):
                        conveyor_item.setFont(col, font2)
                    
                    # Calcola totali per ConveyorID usando query diretta
                    conveyor_totals = self.calculate_conveyor_totals_from_db(cursor, node_id, conveyor_id)
                    self.set_item_values(conveyor_item, conveyor_totals)
                    
                    for photocell_data in hierarchy[node_id][conveyor_id]:
                        photocell_id, avg_offset, max_offset, min_offset, avg_dim_x, count = photocell_data
                        photocell_item = QTreeWidgetItem(conveyor_item)
                        photocell_item.setText(0, f"PhotocellID: {photocell_id}")
                        # Colore normale per PhotocellID (verrà aggiornato da update_item_colors)
                        
                        self.set_item_values(photocell_item, {
                            'avg_offset': avg_offset,
                            'max_offset': max_offset,
                            'min_offset': min_offset,
                            'avg_dim_x': avg_dim_x
                        })
            
            # Aggiorna i colori dopo aver popolato la tree
            self.update_item_colors()
                        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore nell'analisi dei dati:\n{str(e)}"
            )
            
    def calculate_node_totals_from_db(self, cursor, node_id: int) -> Dict:
        """Calcola i totali per un NodeId direttamente dal database"""
        query = """
            SELECT 
                AVG(m.OffsetCtrl) as AvgOffset,
                MAX(m.OffsetCtrl) as MaxOffset,
                MIN(m.OffsetCtrl) as MinOffset,
                AVG(m.DIM_X) as AvgDimX,
                AVG(m.DIM_Z) as AvgDimZ
            FROM Logs l
            JOIN Msg00101 m ON l.MsgNumber = m.MsgNumber
            WHERE l.MsgId = 101 AND m.EventType = 1 AND l.NodeId = ?
        """
        cursor.execute(query, (node_id,))
        row = cursor.fetchone()
        
        if row and row[0] is not None:
            return {
                'avg_offset': row[0] or 0,
                'max_offset': row[1] or 0,
                'min_offset': row[2] or 0,
                'avg_dim_x': row[3] or 0,
                'avg_dim_z': row[4] or 0
            }
        return {'avg_offset': 0, 'max_offset': 0, 'min_offset': 0, 'avg_dim_x': 0, 'avg_dim_z': 0}
        
    def calculate_conveyor_totals_from_db(self, cursor, node_id: int, conveyor_id: int) -> Dict:
        """Calcola i totali per un ConveyorID direttamente dal database"""
        query = """
            SELECT 
                AVG(m.OffsetCtrl) as AvgOffset,
                MAX(m.OffsetCtrl) as MaxOffset,
                MIN(m.OffsetCtrl) as MinOffset,
                AVG(m.DIM_X) as AvgDimX
            FROM Logs l
            JOIN Msg00101 m ON l.MsgNumber = m.MsgNumber
            WHERE l.MsgId = 101 AND m.EventType = 1 AND l.NodeId = ? AND m.ConveyorID = ?
        """
        cursor.execute(query, (node_id, conveyor_id))
        row = cursor.fetchone()
        
        if row and row[0] is not None:
            return {
                'avg_offset': row[0] or 0,
                'max_offset': row[1] or 0,
                'min_offset': row[2] or 0,
                'avg_dim_x': row[3] or 0
            }
        return {'avg_offset': 0, 'max_offset': 0, 'min_offset': 0, 'avg_dim_x': 0}
        
    def format_number(self, value: float, apply_slot_length: bool = False, unit: str = "") -> str:
        """Formatta un numero: interi senza decimali, decimali con 2 cifre"""
        if value is None:
            value = 0.0
        
        # Applica SlotLength solo se richiesto (per gli Offset)
        if apply_slot_length and self.slot_length_enabled and self.slot_length > 0:
            value = value * self.slot_length / 100.0
        
        # Formatta il numero
        if abs(value - round(value)) < 0.001:
            formatted = str(int(round(value)))
        else:
            formatted = f"{value:.2f}"
        
        # Aggiungi unità se presente
        if unit:
            return f"{formatted} {unit}"
        return formatted
    
    def set_item_values(self, item: QTreeWidgetItem, values: Dict):
        """Imposta i valori nelle colonne dell'item"""
        avg_offset = values.get('avg_offset', 0) or 0
        max_offset = values.get('max_offset', 0) or 0
        min_offset = values.get('min_offset', 0) or 0
        avg_dim_x = values.get('avg_dim_x', 0) or 0
        
        # Formatta i valori Offset (con SlotLength e unità "m" se abilitato)
        offset_unit = "m" if self.slot_length_enabled and self.slot_length > 0 else ""
        item.setText(1, self.format_number(avg_offset, apply_slot_length=True, unit=offset_unit))
        item.setText(2, self.format_number(max_offset, apply_slot_length=True, unit=offset_unit))
        item.setText(3, self.format_number(min_offset, apply_slot_length=True, unit=offset_unit))
        
        # DimX sempre in metri (m) come unità fissa
        item.setText(4, self.format_number(avg_dim_x, apply_slot_length=False, unit="m"))
        
        # Allinea tutte le colonne numeriche a destra
        for col in range(1, 5):
            item.setTextAlignment(col, Qt.AlignRight | Qt.AlignVCenter)
        
    def on_slot_length_changed(self, text: str):
        """Gestisce il cambio del valore SlotLength"""
        try:
            self.slot_length = float(text) if text else 0.0
            if self.slot_length_enabled:
                self.refresh_data()
        except ValueError:
            pass
            
    def on_slot_length_enabled_changed(self, state: int):
        """Gestisce l'abilitazione/disabilitazione di SlotLength"""
        self.slot_length_enabled = (state == Qt.Checked)
        self.refresh_data()
        
    def refresh_data(self):
        """Ricarica i dati con le nuove impostazioni preservando lo stato espanso"""
        if self.db_path:
            # Salva lo stato espanso/collassato di tutti gli item
            expanded_states = {}
            root = self.tree_widget.invisibleRootItem()
            for i in range(root.childCount()):
                node_item = root.child(i)
                node_id = node_item.text(0)
                expanded_states[node_id] = {
                    'expanded': node_item.isExpanded(),
                    'children': {}
                }
                for j in range(node_item.childCount()):
                    conveyor_item = node_item.child(j)
                    conveyor_id = conveyor_item.text(0)
                    expanded_states[node_id]['children'][conveyor_id] = conveyor_item.isExpanded()
            
            # Ricarica i dati
            self.analyze_data()
            
            # Ripristina lo stato espanso/collassato
            root = self.tree_widget.invisibleRootItem()
            for i in range(root.childCount()):
                node_item = root.child(i)
                node_id = node_item.text(0)
                if node_id in expanded_states:
                    node_item.setExpanded(expanded_states[node_id]['expanded'])
                    for j in range(node_item.childCount()):
                        conveyor_item = node_item.child(j)
                        conveyor_id = conveyor_item.text(0)
                        if conveyor_id in expanded_states[node_id]['children']:
                            conveyor_item.setExpanded(expanded_states[node_id]['children'][conveyor_id])
            
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        if self.conn:
            self.conn.close()
        event.accept()


def install_dependencies():
    """Installa le dipendenze mancanti"""
    required_packages = ['PyQt5']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PyQt5':
                __import__('PyQt5.QtWidgets')
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Installazione dipendenze mancanti: {', '.join(missing_packages)}")
        import subprocess
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} installato con successo")
            except Exception as e:
                print(f"✗ Errore nell'installazione di {package}: {e}")
                return False
    return True


def main():
    """Funzione principale"""
    # Installa dipendenze se necessario
    if not install_dependencies():
        print("Errore nell'installazione delle dipendenze")
        return
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Stile moderno
    
    window = DatabaseAnalyzer()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

