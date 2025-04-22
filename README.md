<!-- README.md for DJC Games Menu Application -->

# DJC Games Menu

Este repositório contém uma aplicação em **PyQt5** que serve como menu principal em tela cheia para o projeto **DJC Games**. Através dele é possível: iniciar jogos externos (por exemplo, `snake.py` e `tetris.py`), visualizar créditos e sair da aplicação.

---

## Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
- [Documentação de Componentes](#documentação-de-componentes)
  - [MainWindow](#mainwindow)
  - [GameSelectionPage](#gameselectionpage)
  - [CreditsPage](#creditspage)
- [Instalação e Execução](#instalação-e-execução)
- [Personalização](#personalização)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Visão Geral

O aplicativo apresenta três telas principais:

1. **Menu Principal**: botões para *Jogar*, *Créditos* e *Sair*.
2. **Seleção de Jogos**: lista apenas scripts Python existentes e permite executá-los em processos separados.
3. **Créditos**: exibe informações de autoria e ano.

A navegação entre telas é realizada via um layout empilhado (`QStackedLayout`), garantindo transições simples e consistentes.

---

## Funcionalidades

- **Menu principal em tela cheia** com botões estilizados.
- **Detecção dinâmica** de scripts de jogos no diretório.
- **Execução** de cada jogo em novo processo Python.
- **Estilo** escuro customizado via CSS.

---

## Estrutura de Arquivos

```
├── djc_games_menu.py    # Script principal
├── snake.py             # Exemplo de jogo “Cobrinha” (opcional)
└── tetris.py            # Exemplo de jogo “Tetris”    (opcional)
```

---

## Documentação de Componentes

### MainWindow

Classe principal que herda de `QMainWindow`.

#### `__init__(self)`
1. Inicializa `QMainWindow` e define título.
2. Aplica CSS global para cores e botões.
3. Cria três botões: **JOGAR**, **CRÉDITOS**, **SAIR**.
4. Conecta eventos de clique:
   - `JOGAR` → `show_game_selection()`
   - `CRÉDITOS` → `show_credits()`
   - `SAIR` → `close()`
5. Configura `QStackedLayout` com páginas: menu, seleção e créditos.

#### `show_game_selection(self)`
Muda a tela ativa para `GameSelectionPage`.

#### `show_credits(self)`
Muda a tela ativa para `CreditsPage`.

---

### GameSelectionPage

`QWidget` que lista e executa scripts de jogos.

#### `__init__(self, main_win)`
- Recebe referência à `MainWindow` para voltar ao menu.
- Cria layout vertical e título.
- Itera sobre `GAME_PATHS = {"snake": "snake.py", "tetris": "tetris.py"}`.
- Para cada arquivo existente, cria botão que chama `launch_game(path)`.
- Adiciona botão **VOLTAR** que chama `back_to_menu()`.

#### `launch_game(self, script_path)`
Inicia o jogo em novo processo: `subprocess.Popen([sys.executable, script_path])`.

#### `back_to_menu(self)`
Retorna ao índice 0 do `QStackedLayout`, exibindo o menu principal.

---

### CreditsPage

`QWidget` que exibe créditos do projeto.

#### `__init__(self, main_win)`
- Recebe referência à `MainWindow`.
- Cria layout vertical com título **Créditos** e texto fixo:
  ```
  Desenvolvido por Matheus
  DJC Games
  2025
  ```
- Botão **VOLTAR** chama `main_win.stack.setCurrentIndex(0)`.

---

## Instalação e Execução

1. **Pré-requisitos**:
   - Python 3.x
   - PyQt5: `pip install PyQt5`

2. **Clone este repositório**:
   ```bash
   git clone https://github.com/SEU_USUARIO/djc-games-menu.git
   cd djc-games-menu
   ```

3. **Execute**:
   ```bash
   python djc_games_menu.py
   ```

A aplicação abrirá em tela cheia automaticamente.

---

## Personalização

- **Caminhos de Jogos**: edite o dicionário `GAME_PATHS` em `GameSelectionPage`.
- **Estilo Visual**: ajuste o CSS em `MainWindow.setStyleSheet(...)`.
- **Dimensões e Fontes**: modifique `setFixedSize`, `QFont` e espaçamentos.

---

## Contribuição

1. Fork este repositório.
2. Crie uma branch: `git checkout -b feature/minha-melhora`.
3. Faça commit das alterações: `git commit -m "Adiciona x"`.
4. Push para a branch: `git push origin feature/minha-melhora`.
5. Abra um Pull Request.

---

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

