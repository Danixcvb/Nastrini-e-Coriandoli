#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gap Step Calculator
Applicazione per calcolare Step e Gap in base a Portata, Velocità Conveyor e Lunghezza Max Bag
"""

import sys
import subprocess

def install_package(package):
    """Installa un pacchetto se non è già installato"""
    try:
        __import__(package)
    except ImportError:
        print(f"Installazione di {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Verifica e installa le dipendenze
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                  QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                  QGroupBox, QFormLayout)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
except ImportError:
    install_package("PyQt5")
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                  QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                  QGroupBox, QFormLayout)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont


class GapStepCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Gap Step Calculator')
        self.setGeometry(100, 100, 500, 400)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Titolo
        title = QLabel('Gap Step Calculator')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Gruppo input
        input_group = QGroupBox("Dati di Input")
        input_layout = QFormLayout()
        
        self.portata_input = QLineEdit()
        self.portata_input.setPlaceholderText("Inserisci portata [1/h]")
        input_layout.addRow("Portata [1/h]:", self.portata_input)
        
        self.velocita_input = QLineEdit()
        self.velocita_input.setPlaceholderText("Inserisci velocità [m/s]")
        input_layout.addRow("Velocità Conveyor [m/s]:", self.velocita_input)
        
        self.lunghezza_input = QLineEdit()
        self.lunghezza_input.setPlaceholderText("Inserisci lunghezza max [m]")
        input_layout.addRow("Lunghezza Max Bag [m]:", self.lunghezza_input)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Pulsante calcola
        self.calculate_btn = QPushButton('Calcola')
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.calculate_btn.clicked.connect(self.calculate)
        main_layout.addWidget(self.calculate_btn)
        
        # Gruppo output
        output_group = QGroupBox("Risultati")
        output_layout = QFormLayout()
        
        self.step_output = QLineEdit()
        self.step_output.setReadOnly(True)
        self.step_output.setStyleSheet("background-color: #f0f0f0; font-weight: bold;")
        output_layout.addRow("Step [m]:", self.step_output)
        
        self.gap_output = QLineEdit()
        self.gap_output.setReadOnly(True)
        self.gap_output.setStyleSheet("background-color: #f0f0f0; font-weight: bold;")
        output_layout.addRow("Gap [m]:", self.gap_output)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Spacer
        main_layout.addStretch()
        
        # Stile applicazione
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
    
    def calculate(self):
        """Calcola Step e Gap in base agli input"""
        try:
            # Leggi gli input
            portata = float(self.portata_input.text().replace(',', '.'))
            velocita = float(self.velocita_input.text().replace(',', '.'))
            lunghezza_max = float(self.lunghezza_input.text().replace(',', '.'))
            
            # Validazione
            if portata <= 0:
                raise ValueError("La portata deve essere maggiore di zero")
            if velocita <= 0:
                raise ValueError("La velocità deve essere maggiore di zero")
            if lunghezza_max < 0:
                raise ValueError("La lunghezza max deve essere maggiore o uguale a zero")
            
            # Converti portata da 1/h a 1/s
            portata_per_secondo = portata / 3600.0
            
            # Calcola Step: Portata (in 1/s) * Velocità Conveyor
            # Per avere Step in metri, calcoliamo: Velocità / Portata_per_secondo
            # che rappresenta la distanza tra i bag
            # Ma l'utente ha detto "Portata * Velocità", quindi seguiamo quella formula
            # Convertendo la portata in 1/s: Step = (Portata/3600) * Velocità non ha senso dimensionale
            # Penso che l'utente intenda: Step = Velocità / (Portata/3600) = Velocità * 3600 / Portata
            
            # Rileggendo: "Step è calcolato come: Portata * Velocità Conveyor"
            # Se Portata è in 1/h e Velocità in m/s, per avere Step in m:
            # Step = Velocità * (3600 / Portata) = Velocità * 3600 / Portata
            # Questo rappresenta la distanza tra i bag
            
            step = (velocita * 3600.0) / portata
            
            # Calcola Gap: Step - Lunghezza Max
            gap = step - lunghezza_max
            
            # Mostra i risultati con 4 decimali
            self.step_output.setText(f"{step:.4f}")
            self.gap_output.setText(f"{gap:.4f}")
            
            # Evidenzia se il gap è negativo (warning)
            if gap < 0:
                self.gap_output.setStyleSheet("background-color: #ffcccc; font-weight: bold; color: #cc0000;")
            else:
                self.gap_output.setStyleSheet("background-color: #f0f0f0; font-weight: bold;")
                
        except ValueError as e:
            self.step_output.setText("Errore")
            self.gap_output.setText(str(e))
            self.gap_output.setStyleSheet("background-color: #ffcccc; font-weight: bold; color: #cc0000;")
        except Exception as e:
            self.step_output.setText("Errore")
            self.gap_output.setText("Inserire valori numerici validi")
            self.gap_output.setStyleSheet("background-color: #ffcccc; font-weight: bold; color: #cc0000;")


def main():
    app = QApplication(sys.argv)
    window = GapStepCalculator()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

