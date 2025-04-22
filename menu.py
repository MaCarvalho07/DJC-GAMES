import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QPushButton, QStackedLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DJC Games")
        self.setStyleSheet("""
            QWidget { background-color: #1a1a1a; color: white; }
            QPushButton { background-color: #333; border-radius: 10px; padding: 15px; }
            QPushButton:hover { background-color: #444; }
            QPushButton:pressed { background-color: #555; }
        """)
        
        # Central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        # Title
        title = QLabel("DJC GAMES")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Buttons
        self.btn_play = QPushButton("JOGAR")
        self.btn_credit = QPushButton("CRÉDITOS")
        self.btn_exit = QPushButton("SAIR")
        for btn in (self.btn_play, self.btn_credit, self.btn_exit):
            btn.setFont(QFont("Arial", 20))
            btn.setFixedSize(250, 70)
            layout.addWidget(btn, alignment=Qt.AlignCenter)

        # Connections
        self.btn_play.clicked.connect(self.show_game_selection)
        self.btn_credit.clicked.connect(self.show_credits)
        self.btn_exit.clicked.connect(self.close)

        # Stacked pages
        self.stack = QStackedLayout()
        self.game_page = GameSelectionPage(self)
        self.credit_page = CreditsPage(self)
        self.stack.addWidget(central)
        self.stack.addWidget(self.game_page)
        self.stack.addWidget(self.credit_page)

        # Use a container to hold stack
        container = QWidget()
        container.setLayout(self.stack)
        self.setCentralWidget(container)
        self.stack.setCurrentWidget(central)

    def show_game_selection(self):
        self.stack.setCurrentWidget(self.game_page)

    def show_credits(self):
        self.stack.setCurrentWidget(self.credit_page)


class GameSelectionPage(QWidget):
    GAME_PATHS = {"snake": "snake.py", "tetris": "tetris.py"}

    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Escolha o Jogo")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Game buttons
        for name, path in self.GAME_PATHS.items():
            if os.path.exists(path):
                btn = QPushButton(name.upper())
                btn.setFont(QFont("Arial", 18))
                btn.setFixedSize(200, 60)
                btn.clicked.connect(lambda checked, p=path: self.launch_game(p))
                layout.addWidget(btn, alignment=Qt.AlignCenter)

        # Back button
        btn_back = QPushButton("VOLTAR")
        btn_back.setFont(QFont("Arial", 16))
        btn_back.setFixedSize(150, 50)
        btn_back.clicked.connect(self.back_to_menu)
        layout.addWidget(btn_back, alignment=Qt.AlignCenter)

    def launch_game(self, script_path):
        try:
            subprocess.Popen([sys.executable, script_path])
        except Exception as e:
            print(f"Erro ao iniciar o jogo: {e}")

    def back_to_menu(self):
        self.main_win.stack.setCurrentIndex(0)


class CreditsPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Créditos")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        text = QLabel("Desenvolvido por Matheus\nDJC Games\n2025")
        text.setFont(QFont("Arial", 18))
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)

        btn_back = QPushButton("VOLTAR")
        btn_back.setFont(QFont("Arial", 16))
        btn_back.setFixedSize(150, 50)
        btn_back.clicked.connect(lambda: self.main_win.stack.setCurrentIndex(0))
        layout.addWidget(btn_back, alignment=Qt.AlignCenter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showFullScreen()
    sys.exit(app.exec_())
