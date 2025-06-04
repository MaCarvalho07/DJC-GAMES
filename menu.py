#!/usr/bin/env python3

import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedLayout,
    QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient


class MinimalistBackground(QWidget):
    """
    Widget que desenha um fundo minimalista com linha e forma decorativa.
    """
    def __init__(self):
        super().__init__()
        # Não há atributos adicionais, apenas desenho customizado no paintEvent

    def paintEvent(self, event):
        """
        Sobrescreve o método paintEvent para desenhar o fundo:
         - Preenche com cor sólida escura
         - Desenha uma linha horizontal fina
         - Desenha um círculo com gradiente suave
        """
        painter = QPainter(self)

        # 1) Preencher toda a área com um tom de preto-azulado
        painter.fillRect(self.rect(), QColor(10, 10, 15))

        # 2) Desenhar linha horizontal fina 1/3 abaixo do topo
        painter.setPen(QColor(80, 80, 120))  # Tom de azul aplicado à linha
        y_line = self.height() // 3
        painter.drawLine(0, y_line, self.width(), y_line)

        # 3) Desenhar círculo decorativo com gradiente linear
        painter.setPen(Qt.NoPen)  # Sem contorno para o círculo
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(80, 70, 180, 30))   # Começa com roxo semitransparente
        gradient.setColorAt(1, QColor(50, 50, 80, 10))    # Termina com azul escuro translúcido
        painter.setBrush(gradient)

        # O círculo terá 60% do menor lado (largura ou altura)
        size = int(min(self.width(), self.height()) * 0.6)
        # Desenha o círculo no canto inferior direito, centralizado no tamanho
        x = int(self.width() - size // 2)
        y = int(self.height() - size // 2)
        painter.drawEllipse(x, y, size, size)


class MainWindow(QMainWindow):
    """
    Janela principal do aplicativo, com layout minimalista e navegação.
    """
    def __init__(self):
        super().__init__()
        # Define o título da janela
        self.setWindowTitle("DJC Games - Python Games")

        # Aplica estilo global para QLabel e QPushButton
        self.setStyleSheet("""
            QLabel { color: white; }  /* Cores de texto claras */
            QPushButton {
                background-color: transparent;           /* Botões sem fundo sólido */
                border: none;                            /* Sem borda padrão */
                border-left: 3px solid #6366f1;         /* Borda esquerda colorida */
                border-radius: 0;                       /* Nada arredondado */
                padding: 15px;                          /* Espaço interno */
                color: white;                           /* Texto dos botões */
                text-align: left;                       /* Texto alinhado à esquerda */
                font-size: 18px;                        /* Tamanho da fonte */
                letter-spacing: 2px;                    /* Espaçamento entre letras */
            }
            QPushButton:hover {
                background-color: rgba(99, 102, 241, 0.1); /* Hover suave */
                border-left: 3px solid #818cf8;            /* Borda esquerda muda de tom */
                padding-left: 25px;                        /* Emprega texto ao clicar */
            }
        """)

        # Cria o widget de fundo personalizado
        central = MinimalistBackground()

        # Layout vertical principal
        main_layout = QVBoxLayout(central)
        main_layout.setAlignment(Qt.AlignCenter)     # Alinha ao centro vertical e horizontalmente
        main_layout.setSpacing(40)                   # Espaçamento entre seções
        main_layout.setContentsMargins(60, 60, 60, 60)  # Margens internas generosas

        # === Cabeçalho com título e subtítulo ===
        title_layout = QHBoxLayout()  # Layout horizontal para elemento decorativo + textos

        # Linha vertical decorativa à esquerda do título
        line_widget = QWidget()
        line_widget.setFixedWidth(5)
        line_widget.setStyleSheet("background-color: #6366f1;")
        title_layout.addWidget(line_widget)
        title_layout.addSpacing(20)  # Espaço entre linha e textos

        # Container vertical para título e subtítulo
        title_container = QVBoxLayout()

        # Título principal em fonte grande e negrito
        self.title = QLabel("DJC Games - Python Games")
        self.title.setFont(QFont("Arial", 50, QFont.Bold))
        self.title.setStyleSheet("letter-spacing: 5px;")  # Espaçamento entre letras extra
        title_container.addWidget(self.title)

        # Subtítulo em fonte menor e cor diferenciada
        self.subtitle = QLabel("VERSÃO 2.0")
        self.subtitle.setFont(QFont("Arial", 14))
        self.subtitle.setStyleSheet("color: #6366f1; letter-spacing: 8px;")
        title_container.addWidget(self.subtitle)

        title_layout.addLayout(title_container)
        title_layout.addStretch()  # Empurra o restante para a direita
        main_layout.addLayout(title_layout)
        main_layout.addSpacing(40)

        # === Área de botões principais ===
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setAlignment(Qt.AlignLeft)

        # Botões: INICIAR, CRÉDITOS e SAIR
        self.btn_play   = QPushButton("INICIAR")
        self.btn_credit = QPushButton("CRÉDITOS")
        self.btn_exit   = QPushButton("SAIR")
        for btn in [self.btn_play, self.btn_credit, self.btn_exit]:
            btn.setFixedWidth(300)          # Largura fixa
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)
        main_layout.addStretch()  # Empurra elementos seguintes para o topo

        # === Rodapé simples ===
        footer = QLabel("DJC Games - Python Games © 2025")
        footer.setAlignment(Qt.AlignRight)  # Alinha o texto à direita
        footer.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 12px; letter-spacing: 2px;")
        main_layout.addWidget(footer)

        # Conecta cliques dos botões às funções de navegação
        self.btn_play.clicked.connect(self.show_game_selection)
        self.btn_credit.clicked.connect(self.show_credits)
        self.btn_exit.clicked.connect(self.close)

        # === Configuração de páginas empilhadas ===
        self.stack = QStackedLayout()
        self.stack.addWidget(central)                # Página inicial
        self.stack.addWidget(GameSelectionPage(self))
        self.stack.addWidget(CreditsPage(self))
        self.stack.setCurrentIndex(0)                # Começa na página inicial

        # Container que segura o stack e é definido como central
        container = QWidget()
        container.setLayout(self.stack)
        self.setCentralWidget(container)

    def show_game_selection(self):
        """Navega para a página de seleção de jogos"""
        self.stack.setCurrentIndex(1)

    def show_credits(self):
        """Navega para a página de créditos"""
        self.stack.setCurrentIndex(2)


class GameSelectionPage(QWidget):
    """
    Página para seleção de scripts de jogos (snake e tetris).
    """
    GAME_PATHS = {"snake": "jogos/snake.py",  "Tank Survivor": "jogos/Tank_Survivor/main.py", "Space Invaders": "jogos/Space-Invaders/main.py", "Pong": "jogos/pong.py"}

    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        # Aplica estilo local para esta página
        self.setStyleSheet("""
            QWidget { background-color: #0a0a0f; color: white; }
            QLabel { color: white; }
            QPushButton {
                background-color: transparent;
                border: none;
                border-left: 3px solid #6366f1;
                padding: 15px;
                color: white;
                text-align: left;
                font-size: 18px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: rgba(99, 102, 241, 0.1);
                border-left: 3px solid #818cf8;
                padding-left: 25px;
            }
            QPushButton#back-btn {
                border-left: 3px solid #4f46e5;
                font-size: 16px;
            }
            QPushButton#back-btn:hover {
                border-left: 3px solid #6366f1;
            }
        """)

        # Layout vertical da página de seleção
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft)
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)

        # Cabeçalho com linha e título
        title_layout = QHBoxLayout()
        line_widget = QWidget()
        line_widget.setFixedWidth(5)
        line_widget.setStyleSheet("background-color: #6366f1;")
        title_layout.addWidget(line_widget)
        title_layout.addSpacing(20)

        title = QLabel("SELECIONAR JOGO")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setStyleSheet("letter-spacing: 3px;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        layout.addSpacing(40)

        # Botões para cada jogo disponível
        for name, path in self.GAME_PATHS.items():
            if os.path.exists(path):
                btn = QPushButton(name.upper())
                btn.setFixedWidth(300)
                btn.clicked.connect(lambda _, p=path: subprocess.Popen([sys.executable, p]))
                layout.addWidget(btn)

        layout.addSpacing(30)
        # Botão "VOLTAR" com objeto de nome para estilo customizado
        btn_back = QPushButton("VOLTAR")
        btn_back.setObjectName("back-btn")
        btn_back.setFixedWidth(200)
        btn_back.clicked.connect(lambda: self.main_win.stack.setCurrentIndex(0))
        layout.addWidget(btn_back)
        layout.addStretch()
        
        
    def paintEvent(self, event):
        """
        Sobrescreve o método paintEvent para desenhar o fundo:
         - Preenche com cor sólida escura
         - Desenha uma linha horizontal fina
         - Desenha um círculo com gradiente suave
        """
        painter = QPainter(self)

        # 1) Preencher toda a área com um tom de preto-azulado
        painter.fillRect(self.rect(), QColor(10, 10, 15))

        # 2) Desenhar linha horizontal fina 1/3 abaixo do topo
        painter.setPen(QColor(80, 80, 120))  # Tom de azul aplicado à linha
        y_line = self.height() // 3
        painter.drawLine(0, y_line, self.width(), y_line)

        # 3) Desenhar círculo decorativo com gradiente linear
        painter.setPen(Qt.NoPen)  # Sem contorno para o círculo
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(80, 70, 180, 30))   # Começa com roxo semitransparente
        gradient.setColorAt(1, QColor(50, 50, 80, 10))    # Termina com azul escuro translúcido
        painter.setBrush(gradient)

        # O círculo terá 60% do menor lado (largura ou altura)
        size = int(min(self.width(), self.height()) * 0.6)
        # Desenha o círculo no canto inferior direito, centralizado no tamanho
        x = int(self.width() - size // 2)
        y = int(self.height() - size // 2)
        painter.drawEllipse(x, y, size, size)


class CreditsPage(QWidget):
    """
    Página de créditos, com desenvolvedor, estúdio e ano.
    """
    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        # Estilo local para página de créditos
        self.setStyleSheet("""
            QWidget { background-color: #0; color: white; }
            QLabel { color: white; }
            QPushButton {
                background-color: transparent;
                border: none;
                border-left: 3px solid #4f46e5;
                padding: 15px;
                color: white;
                text-align: left;
                font-size: 16px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: rgba(99, 102, 241, 0.1);
                border-left: 3px solid #6366f1;
                padding-left: 25px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft)
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)

        # Cabeçalho com linha decorativa e título
        title_layout = QHBoxLayout()
        line_widget = QWidget()
        line_widget.setFixedWidth(5)
        line_widget.setStyleSheet("background-color: #6366f1;")
        title_layout.addWidget(line_widget)
        title_layout.addSpacing(20)

        title = QLabel("CRÉDITOS")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setStyleSheet("letter-spacing: 3px;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        layout.addSpacing(40)

        # Seção de informações de crédito
        credits_layout = QVBoxLayout()
        credits_layout.setSpacing(10)
        credits_layout.setContentsMargins(30, 0, 0, 0)

        # Label de seção e valor para cada item
        for label_text, value_text in [
            ("DESENVOLVIDO POR", "Matheus Carvalho e Gabriel Loquetti"),
             
            ("ESTÚDIO", "DJC Games"),
            ("ANO", "2025"),
        ]:
            section_label = QLabel(label_text)
            section_label.setFont(QFont("Arial", 14))
            section_label.setStyleSheet("color: #6366f1; letter-spacing: 2px;")
            credits_layout.addWidget(section_label)

            value_label = QLabel(value_text)
            value_label.setFont(QFont("Arial", 24, QFont.Bold))
            value_label.setStyleSheet("letter-spacing: 1px;")
            credits_layout.addWidget(value_label)

            credits_layout.addSpacing(20)

        layout.addLayout(credits_layout)
        layout.addSpacing(40)

        # Botão voltar no rodapé da página de créditos
        btn_back = QPushButton("VOLTAR")
        btn_back.setFixedWidth(200)
        btn_back.clicked.connect(lambda: self.main_win.stack.setCurrentIndex(0))
        layout.addWidget(btn_back)
        layout.addStretch()
    
    def paintEvent(self, event):
        """
        Sobrescreve o método paintEvent para desenhar o fundo:
         - Preenche com cor sólida escura
         - Desenha uma linha horizontal fina
         - Desenha um círculo com gradiente suave
        """
        painter = QPainter(self)

        # 1) Preencher toda a área com um tom de preto-azulado
        painter.fillRect(self.rect(), QColor(10, 10, 15))

        # 2) Desenhar linha horizontal fina 1/3 abaixo do topo
        painter.setPen(QColor(80, 80, 120))  # Tom de azul aplicado à linha
        y_line = self.height() // 3
        painter.drawLine(0, y_line, self.width(), y_line)

        # 3) Desenhar círculo decorativo com gradiente linear
        painter.setPen(Qt.NoPen)  # Sem contorno para o círculo
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(80, 70, 180, 30))   # Começa com roxo semitransparente
        gradient.setColorAt(1, QColor(50, 50, 80, 10))    # Termina com azul escuro translúcido
        painter.setBrush(gradient)

        # O círculo terá 60% do menor lado (largura ou altura)
        size = int(min(self.width(), self.height()) * 0.6)
        # Desenha o círculo no canto inferior direito, centralizado no tamanho
        x = int(self.width() - size // 2)
        y = int(self.height() - size // 2)
        painter.drawEllipse(x, y, size, size)


if __name__ == "__main__":
    # Ponto de entrada da aplicação
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showFullScreen()  # Abre a janela em tela cheia
    sys.exit(app.exec_())  # Executa o loop de eventos
    # O loop de eventos é encerrado quando a janela é fechada