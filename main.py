"""
Script principale per l'avvio dell'applicazione di configurazione nastri trasportatori.
Questo file viene utilizzato per avviare l'applicazione in modalità debug.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
# from tkinter import messagebox  # No longer needed directly here
# from interfaccia_grafica import create_gui # Will be replaced by PyQt6 App class
# from installazione_pacchetti import check_and_install_packages # Keep this
import subprocess

# Determine if running as script or frozen executable
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    try:
        application_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:  # __file__ is not defined (e.g., in interactive interpreter)
        application_path = os.getcwd()

REQUIREMENTS_FILE = os.path.join(application_path, 'requirements.txt')

def check_and_install_packages(requirements_file):
    """
    Checks if packages listed in requirements.txt are installed and prompts for installation if not.

    Args:
        requirements_file (str): Path to the requirements.txt file.

    Returns:
        bool: True if all packages are installed or installation was successful/skipped,
              False if installation failed or was cancelled.
    """
    try:
        import pkg_resources
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        missing_packages = []
        for package in packages:
            try:
                # Use the base package name for checking (e.g., PyQt6 for PyQt6==x.y.z)
                dist_name = package.split('==')[0].split('>=')[0].split('<=')[0].split('<')[0].split('>')[0]
                pkg_resources.get_distribution(dist_name)
            except pkg_resources.DistributionNotFound:
                missing_packages.append(package)

        if missing_packages:
            print(f"Pacchetti mancanti: {', '.join(missing_packages)}")

            reply = input("Alcuni pacchetti necessari non sono installati. Vuoi installarli ora? (s/n): ").lower()
            if reply == 's':
                print("Installazione pacchetti in corso...")
                try:
                    # Use sys.executable to ensure pip matches the current Python interpreter
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
                    print("Installazione completata.")
                    # Need to restart the app usually after installing GUI libs
                    print("\nRiavvia l'applicazione per applicare le modifiche.")
                    return False # Indicate restart needed
                except subprocess.CalledProcessError as e:
                    print(f"Errore durante l'installazione: {e}")
                    print("Installa manualmente i pacchetti elencati in requirements.txt e riavvia.")
                    return False
            else:
                print("Installazione annullata. L'applicazione potrebbe non funzionare correttamente.")
                return False
        return True
    except FileNotFoundError:
        print(f"Errore: {requirements_file} non trovato.")
        return False
    except Exception as e:
        print(f"Errore durante il controllo dei pacchetti: {e}")
        return False

def main():
    """
    Funzione principale per avviare l'applicazione.
    """
    if not check_and_install_packages(REQUIREMENTS_FILE):
        sys.exit(1) # Exit if packages are missing and not installed or need restart

    # Import necessary Qt classes for palette and application FIRST
    from PyQt6.QtGui import QPalette, QColor, QFont
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QApplication

    # Now import the PyQt6 interface AFTER checking packages and basic Qt imports
    try:
        from interfaccia_grafica_qt import NastriApp # Import the new PyQt6 App class
    except ImportError as e:
        print(f"Errore: Impossibile importare l'interfaccia grafica PyQt6 (interfaccia_grafica_qt.py): {e}")
        print("Assicurati che PyQt6 sia installato correttamente e che il file dell'interfaccia esista.")
        sys.exit(1)

    app = QApplication(sys.argv)

    # --- Apply Dark Theme ---
    app.setStyle("Fusion") # Fusion provides a good base

    # Custom dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white) # White text on highlight

    # Disabled state colors
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))
    app.setPalette(dark_palette)

    # Set default font
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    # Refined Stylesheet
    app.setStyleSheet("""
        QMainWindow, QDialog {
            background-color: #353535; /* Slightly different bg for windows */
        }
        QWidget {
             /* General widget text color - inherited unless overridden */
             color: #e0e0e0;
        }
        QToolTip {
            color: #ffffff;
            background-color: #2a82da;
            border: 1px solid white;
            padding: 4px;
            border-radius: 3px;
        }
        QLabel {
             background-color: transparent; /* Ensure labels are transparent */
             color: #e0e0e0; /* Default label color */
             padding: 2px;
        }
        QPushButton {
            border: 1px solid #5A5A5A;
            border-radius: 4px;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                             stop: 0 #606060, stop: 1 #505050);
            min-width: 70px;
            min-height: 25px; /* Adjusted default button height */
            padding: 5px;
            color: white;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                             stop: 0 #707070, stop: 1 #606060);
            border-color: #777777;
        }
        QPushButton:pressed {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                             stop: 0 #505050, stop: 1 #404040);
            border-color: #5A5A5A;
        }
        QPushButton:disabled {
            background-color: #404040;
            border-color: #505050;
            color: #808080;
        }
        QComboBox {
            border: 1px solid #5A5A5A;
            border-radius: 3px;
            padding: 4px 18px 4px 8px; /* Adjusted padding */
            min-width: 6em;
            background-color: #424242;
            color: white;
            selection-background-color: #2a82da; /* Background for selected item text */
        }
        QComboBox:hover {
            border-color: #777777;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #5A5A5A;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            background-color: #555555;
        }
        QComboBox::down-arrow {
            image: url(:/qt-project.org/styles/commonstyle/images/standardbutton-down-16.png); /* Standard arrow */
        }
        QComboBox::down-arrow:on {
             /* Maybe change arrow color/image when dropdown is open */
        }
        QComboBox QAbstractItemView {
            border: 1px solid #5A5A5A;
            selection-background-color: #2a82da;
            background-color: #424242;
            color: white;
            padding: 4px;
        }
        QLineEdit {
            border: 1px solid #5A5A5A;
            padding: 5px;
            background: #424242;
            border-radius: 3px;
            color: white;
            selection-background-color: #2a82da;
            selection-color: white;
        }
        QLineEdit:read-only {
             background: #4A4A4A; /* Slightly different for read-only */
             color: #b0b0b0;
        }
        QListWidget {
             border: 1px solid #5A5A5A;
             background-color: #424242;
             padding: 4px;
             border-radius: 3px;
        }
        QListWidget::item {
             padding: 3px;
             color: #e0e0e0;
        }
        QListWidget::item:selected {
             background-color: #2a82da;
             color: white;
        }
        QStatusBar {
             background-color: #353535;
             color: #e0e0e0;
             border-top: 1px solid #5A5A5A;
        }
        QStatusBar::item {
             border: none; /* Remove borders within status bar items */
        }
         QScrollArea {
             border: none; /* Remove border from scroll area itself */
             background-color: transparent;
         }
         /* Style scrollbars if needed */
         QScrollBar:vertical {
             border: 1px solid #5A5A5A;
             background: #424242;
             width: 12px;
             margin: 0px 0px 0px 0px;
         }
         QScrollBar::handle:vertical {
             background: #606060;
             min-height: 20px;
             border-radius: 6px;
         }
         QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
             height: 0px;
             background: none;
         }
         QScrollBar:horizontal {
             border: 1px solid #5A5A5A;
             background: #424242;
             height: 12px;
             margin: 0px 0px 0px 0px;
         }
         QScrollBar::handle:horizontal {
             background: #606060;
             min-width: 20px;
             border-radius: 6px;
         }
         QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
             width: 0px;
             background: none;
         }
         QFrame[frameShape="4"], /* HLine */
         QFrame[frameShape="5"]  /* VLine */
         {
              border: none; /* Remove border from QFrame used as separator */
              background-color: #5A5A5A; /* Set color for separator line */
              min-height: 1px; /* Ensure HLine is visible */
              max-height: 1px;
              min-width: 1px; /* Ensure VLine is visible */
              max-width: 1px;
         }
    """)

    main_window = NastriApp()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()