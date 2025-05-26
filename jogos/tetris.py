import pygame
import random
import os
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any

# Constants
COLORS = [
    (0, 0, 0),         # Black (background)
    (120, 37, 179),    # Purple
    (100, 179, 179),   # Cyan
    (80, 134, 22),     # Green
    (180, 34, 22),     # Red
    (180, 134, 22),    # Orange
    (180, 34, 122),    # Pink
    (0, 180, 255),     # Light Blue
]

# Game settings
FPS = 60
INITIAL_LEVEL = 1
LEVEL_SPEED_FACTOR = 5  # How much faster each level is
SCORE_PER_LINE = 100
SCORE_BONUS_MULTIPLIER = 2  # Bonus for multiple lines at once
SCORE_FOR_SOFT_DROP = 1
SCORE_FOR_HARD_DROP = 2

# UI Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (0, 150, 255)
GOLD = (255, 215, 0)

# File paths
RANK_FILE = "tetris_ranking.json"
SETTINGS_FILE = "tetris_settings.json"


class Figure:
    """Represents a Tetris piece (tetromino)"""
    
    # Tetromino definitions - each number represents a position in a 4x4 grid
    # Each sublist represents a rotation state
    TETROMINOS = [
        # I-piece
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        # Z-piece
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        # S-piece
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        # J-piece
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        # L-piece
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        # T-piece
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        # O-piece
        [[1, 2, 5, 6]],
    ]
    
    # Names for each piece type (for display and statistics)
    PIECE_NAMES = ["I", "Z", "S", "J", "L", "T", "O"]

    x = 0
    y = 0
    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.TETROMINOS) - 1)
        self.color = random.randint(1, len(COLORS) - 1)
        self.rotation = 0

    def image(self) -> List[int]:
        """Get the current rotation state of the piece"""
        return self.TETROMINOS[self.type][self.rotation]

    def rotate(self, clockwise: bool = False) -> None:
        """Rotate the piece (counterclockwise by default)"""
        if clockwise:
            self.rotation = (self.rotation + 1) % len(self.TETROMINOS[self.type])
        else:
            self.rotation = (self.rotation - 1) % len(self.TETROMINOS[self.type])

    def get_name(self) -> str:
        """Get the name of the current piece"""
        return self.PIECE_NAMES[self.type]


class GameStats:
    """Tracks game statistics"""
    
    def __init__(self):
        self.lines_cleared = 0
        self.pieces_placed = 0
        self.piece_stats = {name: 0 for name in Figure.PIECE_NAMES}
        self.start_time = datetime.now()
        self.game_duration = 0
        
    def add_piece(self, piece_type: int) -> None:
        """Record a placed piece"""
        self.pieces_placed += 1
        self.piece_stats[Figure.PIECE_NAMES[piece_type]] += 1
        
    def add_lines(self, lines: int) -> None:
        """Record cleared lines"""
        self.lines_cleared += lines
        
    def end_game(self) -> None:
        """Calculate final game duration"""
        self.game_duration = (datetime.now() - self.start_time).total_seconds()
        
    def get_duration_str(self) -> str:
        """Get formatted duration string"""
        if self.game_duration == 0:  # Game still in progress
            seconds = (datetime.now() - self.start_time).total_seconds()
        else:
            seconds = self.game_duration
            
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"


class Tetris:
    """Main game logic class"""
    
    def __init__(self, height: int, width: int, screen_width: int, screen_height: int):
        self.level = INITIAL_LEVEL
        self.score = 0
        self.state = "start"
        self.field: List[List[int]] = []
        self.height = height
        self.width = width
        self.stats = GameStats()
        self.next_figure: Optional[Figure] = None
        self.held_figure: Optional[Figure] = None
        self.can_hold = True
        
        # Calculate zoom factor and position
        self.zoom = min(screen_width // (width + 12), screen_height // (height + 2))
        self.x = (screen_width - self.zoom * width) // 2
        self.y = screen_height // 20
        
        # Initialize game field
        self.reset_field()
        
        # Preview and hold box positions
        self.preview_x = self.x + self.zoom * (width + 1)
        self.preview_y = self.y + self.zoom * 2
        self.hold_x = self.x - self.zoom * 5
        self.hold_y = self.y + self.zoom * 2
        
        # Current active piece
        self.figure: Optional[Figure] = None
        
        # Ghost piece (shows where piece will land)
        self.ghost_y = 0
        
        # Pause state
        self.paused = False
        
        # Animation effects
        self.cleared_lines: List[int] = []
        self.clear_animation = 0
        self.level_up_animation = 0
        
        # Game over animation
        self.game_over_animation = 0
        
    def reset_field(self) -> None:
        """Initialize or reset the game field"""
        self.field = []
        for _ in range(self.height):
            new_line = [0] * self.width
            self.field.append(new_line)

    def new_figure(self) -> None:
        """Create a new active figure"""
        if self.next_figure:
            self.figure = self.next_figure
            self.next_figure = Figure(3, 0)
        else:
            self.figure = Figure(3, 0)
            self.next_figure = Figure(3, 0)
        
        # Calculate ghost piece position
        self.update_ghost()
        
    def update_ghost(self) -> None:
        """Update the ghost piece position"""
        if not self.figure:
            return
            
        # Start from current position
        self.ghost_y = self.figure.y
        
        # Move down until collision
        while not self.check_collision(0, self.ghost_y + 1):
            self.ghost_y += 1
    
    def hold(self) -> None:
        """Hold the current piece or swap with held piece"""
        if not self.can_hold or not self.figure:
            return
            
        if self.held_figure:
            # Swap current and held
            self.figure, self.held_figure = self.held_figure, self.figure
            # Reset position
            self.figure.x, self.figure.y = 3, 0
        else:
            # Store current and get new
            self.held_figure = self.figure
            self.new_figure()
            
        # Prevent multiple holds in a row
        self.can_hold = False
        
        # Update ghost
        self.update_ghost()
    
    def check_collision(self, dx: int = 0, dy: int = 0, test_rotation: int = None) -> bool:
        """Check if the figure collides with walls or other pieces"""
        if not self.figure:
            return False
            
        # Get the rotation to test
        old_rotation = self.figure.rotation
        if test_rotation is not None:
            self.figure.rotation = test_rotation
            
        # Check each block of the piece
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    # Calculate new position
                    new_y = i + self.figure.y + dy
                    new_x = j + self.figure.x + dx
                    
                    # Check boundaries and collisions
                    if (new_y >= self.height or 
                        new_x >= self.width or 
                        new_x < 0 or 
                        (new_y >= 0 and self.field[new_y][new_x] > 0)):
                        
                        # Restore rotation if needed
                        if test_rotation is not None:
                            self.figure.rotation = old_rotation
                        return True
                        
        # Restore rotation if needed
        if test_rotation is not None:
            self.figure.rotation = old_rotation
            
        return False

    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        return True
        return False

    def break_lines(self) -> None:
        """Check for and clear completed lines"""
        self.cleared_lines = []
        
        # Find completed lines
        for i in range(1, self.height):
            if all(self.field[i]):
                self.cleared_lines.append(i)
                
        if not self.cleared_lines:
            return
            
        # Start clear animation
        self.clear_animation = 10
        
        # Update stats
        lines_count = len(self.cleared_lines)
        self.stats.add_lines(lines_count)
        
        # Calculate score based on level and lines cleared
        line_score = SCORE_PER_LINE * self.level
        # Bonus for multiple lines
        if lines_count > 1:
            line_score *= lines_count * SCORE_BONUS_MULTIPLIER
            
        self.score += line_score
        
        # Check for level up (every 10 lines)
        old_level = self.level
        self.level = max(INITIAL_LEVEL, (self.stats.lines_cleared // 10) + INITIAL_LEVEL)
        
        if self.level > old_level:
            self.level_up_animation = 20

    def clear_completed_lines(self) -> None:
        """Remove completed lines and shift blocks down"""
        if not self.cleared_lines:
            return
            
        # Clear lines from bottom to top to avoid issues
        for line in sorted(self.cleared_lines, reverse=True):
            # Remove the line
            for i in range(line, 0, -1):
                for j in range(self.width):
                    self.field[i][j] = self.field[i-1][j]
                    
            # Clear the top line
            for j in range(self.width):
                self.field[0][j] = 0
                
        # Reset cleared lines
        self.cleared_lines = []

    def go_space(self) -> None:
        """Hard drop - move piece to bottom instantly"""
        if not self.figure or self.state != "start":
            return
            
        # Count how many cells we drop for scoring
        drop_distance = 0
        
        # Move down until collision
        while not self.check_collision(0, 1):
            self.figure.y += 1
            drop_distance += 1
            
        # Add score for hard drop
        self.score += drop_distance * SCORE_FOR_HARD_DROP
        
        # Lock the piece
        self.freeze()

    def go_down(self, manual: bool = False) -> None:
        """Move piece down one cell"""
        if not self.figure or self.state != "start":
            return
            
        self.figure.y += 1
        
        if self.check_collision():
            self.figure.y -= 1
            self.freeze()
        elif manual:  # Add points for soft drop
            self.score += SCORE_FOR_SOFT_DROP

    def freeze(self) -> None:
        """Lock the current piece into the field"""
        if not self.figure:
            return
            
        # Add the piece to the field
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y >= 0:  # Only if visible on field
                        self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        
        # Update statistics
        self.stats.add_piece(self.figure.type)
        
        # Check for completed lines
        self.break_lines()
        
        # Allow holding again
        self.can_hold = True
        
        # Create new piece
        self.new_figure()
        
        # Check for game over
        if self.check_collision():
            self.state = "gameover"
            self.stats.end_game()
            self.game_over_animation = 60  # Frames for animation

    def go_side(self, dx: int) -> None:
        """Move piece horizontally"""
        if not self.figure or self.state != "start":
            return
            
        old_x = self.figure.x
        self.figure.x += dx
        
        if self.check_collision():
            self.figure.x = old_x
        else:
            # Update ghost piece
            self.update_ghost()

    def rotate(self, clockwise: bool = False) -> None:
        """Rotate the current piece with wall kicks"""
        if not self.figure or self.state != "start":
            return
            
        old_rotation = self.figure.rotation
        self.figure.rotate(clockwise)
        
        # Try basic rotation
        if not self.check_collision():
            # Success - update ghost
            self.update_ghost()
            return
            
        # Try wall kicks - move left/right to make rotation work
        for kick_x in [-1, 1, -2, 2]:
            self.figure.x += kick_x
            if not self.check_collision():
                # Success - update ghost
                self.update_ghost()
                return
            self.figure.x -= kick_x
            
        # If all fails, revert rotation
        self.figure.rotation = old_rotation

    def toggle_pause(self) -> None:
        """Toggle game pause state"""
        if self.state == "start":
            self.paused = not self.paused

    def restart(self) -> None:
        """Reset the game to initial state"""
        self.level = INITIAL_LEVEL
        self.score = 0
        self.state = "start"
        self.paused = False
        self.reset_field()
        self.stats = GameStats()
        self.figure = None
        self.next_figure = None
        self.held_figure = None
        self.can_hold = True
        self.cleared_lines = []
        self.clear_animation = 0
        self.level_up_animation = 0
        self.game_over_animation = 0
        self.new_figure()

    def update(self) -> None:
        """Update game state for each frame"""
        if self.state != "start" or self.paused:
            return
            
        # Handle animations
        if self.clear_animation > 0:
            self.clear_animation -= 1
            if self.clear_animation == 0:
                self.clear_completed_lines()
            return
            
        # Normal game update - gravity
        self.go_down()

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

# Funções de ranking
RANK_FILE = "ranking.json"

class RankingSystem:
    """Handles high score tracking and display"""
    
    def __init__(self, filename: str = RANK_FILE, max_entries: int = 10):
        self.filename = filename
        self.max_entries = max_entries
        self.entries: List[Dict[str, Any]] = self.load()
        
    def load(self) -> List[Dict[str, Any]]:
        """Load ranking data from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
        
    def save(self) -> None:
        """Save ranking data to file"""
        try:
            with open(self.filename, "w") as f:
                json.dump(self.entries, f, indent=4)
        except IOError:
            print(f"Error saving ranking to {self.filename}")
            
    def add_score(self, name: str, score: int, stats: GameStats) -> bool:
        """
        Add a new score to the ranking
        Returns True if it made it to the high scores
        """
        # Create entry with additional stats
        entry = {
            "name": name,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "lines": stats.lines_cleared,
            "pieces": stats.pieces_placed,
            "duration": stats.get_duration_str()
        }
        
        # Check if score is high enough
        if len(self.entries) < self.max_entries or score > self.entries[-1]["score"]:
            self.entries.append(entry)
            self.entries.sort(key=lambda x: x["score"], reverse=True)
            self.entries = self.entries[:self.max_entries]
            self.save()
            return True
        return False
        
    def is_high_score(self, score: int) -> bool:
        """Check if a score would make it to the ranking"""
        return len(self.entries) < self.max_entries or score > self.entries[-1]["score"]
        
    def get_rank(self, score: int) -> int:
        """Get the rank a score would achieve (1-based)"""
        for i, entry in enumerate(self.entries):
            if score >= entry["score"]:
                return i + 1
        return len(self.entries) + 1 if len(self.entries) < self.max_entries else 0

def load_ranking():
    if os.path.exists(RANK_FILE):
        with open(RANK_FILE, "r") as f:
            return json.load(f)
    return []

def save_ranking(ranking):
    with open(RANK_FILE, "w") as f:
        json.dump(ranking, f)

def add_score(name, score):
    ranking = load_ranking()
    ranking.append({"name": name, "score": score})
    ranking.sort(key=lambda x: x["score"], reverse=True)
    save_ranking(ranking[:10])  # mantém só top 10

class SettingsManager:
    """Manages game settings and controls"""
    
    DEFAULT_CONTROLS = {
        "move_left": pygame.K_LEFT,
        "move_right": pygame.K_RIGHT,
        "rotate_ccw": pygame.K_UP,
        "rotate_cw": pygame.K_x,
        "soft_drop": pygame.K_DOWN,
        "hard_drop": pygame.K_SPACE,
        "hold": pygame.K_c,
        "pause": pygame.K_p
    }
    
    DEFAULT_SETTINGS = {
        "fullscreen": True,
        "show_ghost": True,
        "show_grid": True,
        "music_volume": 0.5,
        "sfx_volume": 0.7
    }
    
    def __init__(self, filename: str = SETTINGS_FILE):
        self.filename = filename
        self.controls = self.DEFAULT_CONTROLS.copy()
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load()
        
    def load(self) -> None:
        """Load settings from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    if "controls" in data:
                        # Convert string keys back to integers for pygame keys
                        self.controls = {k: int(v) for k, v in data["controls"].items()}
                    if "settings" in data:
                        self.settings.update(data["settings"])
            except (json.JSONDecodeError, IOError, ValueError):
                # Use defaults if file is corrupted
                pass
                
    def save(self) -> None:
        """Save settings to file"""
        try:
            data = {
                "controls": self.controls,
                "settings": self.settings
            }
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=4)
        except IOError:
            print(f"Error saving settings to {self.filename}")
            
    def get_key_name(self, key_code: int) -> str:
        """Convert pygame key code to readable name"""
        return pygame.key.name(key_code).upper()
        
    def update_control(self, action: str, key_code: int) -> None:
        """Update a control binding"""
        if action in self.controls:
            self.controls[action] = key_code
            self.save()
            
    def update_setting(self, setting: str, value: Any) -> None:
        """Update a game setting"""
        if setting in self.settings:
            self.settings[setting] = value
            self.save()
            
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.controls = self.DEFAULT_CONTROLS.copy()
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save()

class TetrisGame:
    """Main game class that handles the game loop and UI"""
    
    def __init__(self):
        pygame.init()
        
        # Load settings
        self.settings = SettingsManager()
        
        # Set up display
        self.info = pygame.display.Info()
        self.screen_width = self.info.current_w
        self.screen_height = self.info.current_h
        
        # Initialize screen based on fullscreen setting
        self.update_screen_mode()
        
        pygame.display.set_caption("Tetris")
        
        # Load fonts
        self.title_font = pygame.font.SysFont('Arial', 60, True, False)
        self.font = pygame.font.SysFont('Arial', 40, True, False)
        self.small_font = pygame.font.SysFont('Arial', 30, True, False)
        self.tiny_font = pygame.font.SysFont('Arial', 20, True, False)
        
        # Set up clock
        self.clock = pygame.time.Clock()
        
        # Initialize ranking system
        self.ranking = RankingSystem()
        
        # Game state
        self.game = None
        self.state = "menu"  # menu, game, ranking, settings, controls, gameover
        self.player_name = ""
        
        # For settings menu
        self.selected_setting = 0
        self.changing_control = None
        
    def update_screen_mode(self) -> None:
        """Update screen based on fullscreen setting"""
        if self.settings.settings["fullscreen"]:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height), 
                pygame.FULLSCREEN
            )
        else:
            # Windowed mode (80% of screen size)
            w = int(self.screen_width * 0.8)
            h = int(self.screen_height * 0.8)
            self.screen = pygame.display.set_mode((w, h))
            
    def draw_text(self, text: str, font, color: Tuple[int, int, int], x: int, y: int, 
                 align: str = "left") -> None:
        """Draw text with alignment options"""
        text_surface = font.render(text, True, color)
        if align == "center":
            x = x - text_surface.get_width() // 2
        elif align == "right":
            x = x - text_surface.get_width()
        self.screen.blit(text_surface, (x, y))
        
    def draw_centered_text(self, text: str, y: int, font=None, color: Tuple[int, int, int] = WHITE) -> None:
        """Draw text centered horizontally"""
        if font is None:
            font = self.font
        self.draw_text(text, font, color, self.screen.get_width() // 2, y, "center")
        
    def draw_menu(self) -> None:
        """Draw the main menu"""
        self.screen.fill(BLACK)
        
        # Title
        title_y = self.screen.get_height() // 6
        self.draw_centered_text("TETRIS", title_y, self.title_font, LIGHT_BLUE)
        
        # Menu options
        menu_y = self.screen.get_height() // 3
        menu_spacing = 60
        
        options = [
            "1 - Play Game",
            "2 - High Scores",
            "3 - Settings",
            "ESC - Exit"
        ]
        
        for i, option in enumerate(options):
            self.draw_centered_text(option, menu_y + i * menu_spacing)
            
    def draw_settings_menu(self) -> None:
        """Draw the settings menu"""
        self.screen.fill(BLACK)
        
        # Title
        self.draw_centered_text("SETTINGS", 50, self.title_font)
        
        # Settings options
        settings_y = 150
        spacing = 50
        
        options = [
            f"Fullscreen: {'ON' if self.settings.settings['fullscreen'] else 'OFF'}",
            f"Show Ghost Piece: {'ON' if self.settings.settings['show_ghost'] else 'OFF'}",
            f"Show Grid: {'ON' if self.settings.settings['show_grid'] else 'OFF'}",
            f"Music Volume: {int(self.settings.settings['music_volume'] * 100)}%",
            f"Sound Effects: {int(self.settings.settings['sfx_volume'] * 100)}%",
            "Configure Controls",
            "Reset to Defaults",
            "Back to Menu"
        ]
        
        for i, option in enumerate(options):
            color = GOLD if i == self.selected_setting else WHITE
            self.draw_centered_text(option, settings_y + i * spacing, self.font, color)
            
        # Instructions
        instructions = "Use UP/DOWN to select, LEFT/RIGHT to change, ENTER to confirm"
        self.draw_centered_text(instructions, self.screen.get_height() - 50, self.small_font, GRAY)
        
    def draw_controls_menu(self) -> None:
        """Draw the controls configuration menu"""
        self.screen.fill(BLACK)
        
        # Title
        self.draw_centered_text("CONTROLS", 50, self.title_font)
        
        # Controls list
        controls_y = 150
        spacing = 50
        
        control_names = {
            "move_left": "Move Left",
            "move_right": "Move Right",
            "rotate_ccw": "Rotate Counter-Clockwise",
            "rotate_cw": "Rotate Clockwise",
            "soft_drop": "Soft Drop",
            "hard_drop": "Hard Drop",
            "hold": "Hold Piece",
            "pause": "Pause Game"
        }
        
        i = 0
        for action, name in control_names.items():
            key_name = self.settings.get_key_name(self.settings.controls[action])
            text = f"{name}: {key_name}"
            
            # Highlight if currently changing this control
            if self.changing_control == action:
                color = LIGHT_BLUE
                text = f"{name}: Press a key..."
            elif i == self.selected_setting:
                color = GOLD
            else:
                color = WHITE
                
            self.draw_centered_text(text, controls_y + i * spacing, self.font, color)
            i += 1
            
        # Back option
        back_text = "Back to Settings"
        color = GOLD if i == self.selected_setting else WHITE
        self.draw_centered_text(back_text, controls_y + i * spacing, self.font, color)
        
        # Instructions
        if self.changing_control:
            instructions = "Press any key to assign, or ESC to cancel"
        else:
            instructions = "Use UP/DOWN to select, ENTER to change, ESC to go back"
        self.draw_centered_text(instructions, self.screen.get_height() - 50, self.small_font, GRAY)
        
    def draw_name_input(self) -> None:
        """Draw the name input screen"""
        self.screen.fill(BLACK)
        
        # Title
        self.draw_centered_text("Enter Your Name", self.screen.get_height() // 3, self.title_font)
        
        # Name input
        name_box_width = 400
        name_box_height = 60
        name_box_x = (self.screen.get_width() - name_box_width) // 2
        name_box_y = self.screen.get_height() // 2
        
        # Draw input box
        pygame.draw.rect(self.screen, GRAY, 
                        (name_box_x, name_box_y, name_box_width, name_box_height), 2)
        
        # Draw name
        self.draw_centered_text(self.player_name + "▌", name_box_y + name_box_height // 2 - 15)
        
        # Instructions
        instructions = "Enter 3-10 characters, press ENTER when done"
        self.draw_centered_text(instructions, name_box_y + name_box_height + 40, self.small_font, GRAY)
        
    def draw_ranking(self) -> None:
        """Draw the high scores screen"""
        self.screen.fill(BLACK)
        
        # Title
        self.draw_centered_text("HIGH SCORES", 50, self.title_font, GOLD)
        
        # Column headers
        header_y = 130
        self.draw_text("RANK", self.small_font, LIGHT_BLUE, 100, header_y)
        self.draw_text("NAME", self.small_font, LIGHT_BLUE, 200, header_y)
        self.draw_text("SCORE", self.small_font, LIGHT_BLUE, 400, header_y)
        self.draw_text("LINES", self.small_font, LIGHT_BLUE, 550, header_y)
        self.draw_text("TIME", self.small_font, LIGHT_BLUE, 650, header_y)
        self.draw_text("DATE", self.small_font, LIGHT_BLUE, 750, header_y)
        
        # Draw horizontal line
        pygame.draw.line(self.screen, GRAY, (80, header_y + 35), 
                        (self.screen.get_width() - 80, header_y + 35), 2)
        
        # Entries
        entries_y = header_y + 50
        spacing = 40
        
        if not self.ranking.entries:
            self.draw_centered_text("No high scores yet!", entries_y + 100, self.font, GRAY)
        else:
            for i, entry in enumerate(self.ranking.entries):
                # Rank
                self.draw_text(f"{i+1}.", self.small_font, WHITE, 100, entries_y + i * spacing)
                
                # Name
                self.draw_text(entry["name"], self.small_font, WHITE, 200, entries_y + i * spacing)
                
                # Score
                self.draw_text(f"{entry['score']}", self.small_font, WHITE, 400, entries_y + i * spacing)
                
                # Additional stats if available
                if "lines" in entry:
                    self.draw_text(f"{entry['lines']}", self.small_font, WHITE, 550, entries_y + i * spacing)
                
                if "duration" in entry:
                    self.draw_text(entry["duration"], self.small_font, WHITE, 650, entries_y + i * spacing)
                
                # Date (shortened)
                date = entry["date"].split()[0] if "date" in entry else ""
                self.draw_text(date, self.small_font, WHITE, 750, entries_y + i * spacing)
        
        # Instructions
        self.draw_centered_text("Press any key to return to menu", 
                              self.screen.get_height() - 50, self.small_font, GRAY)
        
    def draw_game_field(self) -> None:
        """Draw the main game field"""
        if not self.game:
            return
            
        # Draw field background
        field_bg = pygame.Rect(
            self.game.x - 5, 
            self.game.y - 5,
            self.game.zoom * self.game.width + 10,
            self.game.zoom * self.game.height + 10
        )
        pygame.draw.rect(self.screen, DARK_GRAY, field_bg)
        
        # Draw grid and blocks
        for i in range(self.game.height):
            for j in range(self.game.width):
                # Draw grid if enabled
                if self.settings.settings["show_grid"]:
                    pygame.draw.rect(
                        self.screen, 
                        GRAY, 
                        [
                            self.game.x + self.game.zoom * j, 
                            self.game.y + self.game.zoom * i, 
                            self.game.zoom, 
                            self.game.zoom
                        ], 
                        1
                    )
                
                # Draw blocks
                if self.game.field[i][j] > 0:
                    color_idx = self.game.field[i][j]
                    
                    # Flashing effect for lines being cleared
                    if i in self.game.cleared_lines:
                        if self.game.clear_animation % 2 == 0:
                            color_idx = 7  # Use light blue for flash effect
                    
                    pygame.draw.rect(
                        self.screen, 
                        COLORS[color_idx], 
                        [
                            self.game.x + self.game.zoom * j + 1, 
                            self.game.y + self.game.zoom * i + 1, 
                            self.game.zoom - 2, 
                            self.game.zoom - 2
                        ]
                    )
        
        # Draw ghost piece if enabled
        if (self.settings.settings["show_ghost"] and 
            self.game.figure and 
            self.game.state == "start" and
            not self.game.paused):
            
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.figure.image():
                        # Draw ghost piece with transparency
                        ghost_rect = pygame.Rect(
                            self.game.x + self.game.zoom * (j + self.game.figure.x) + 1,
                            self.game.y + self.game.zoom * (i + self.game.ghost_y) + 1,
                            self.game.zoom - 2,
                            self.game.zoom - 2
                        )
                        
                        # Create a transparent surface
                        s = pygame.Surface((ghost_rect.width, ghost_rect.height))
                        s.set_alpha(80)  # 0-255, lower is more transparent
                        s.fill(COLORS[self.game.figure.color])
                        self.screen.blit(s, ghost_rect)
                        
                        # Draw outline
                        pygame.draw.rect(
                            self.screen,
                            COLORS[self.game.figure.color],
                            ghost_rect,
                            1
                        )
        
        # Draw active piece
        if self.game.figure and self.game.state == "start" and not self.game.paused:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.figure.image():
                        pygame.draw.rect(
                            self.screen, 
                            COLORS[self.game.figure.color], 
                            [
                                self.game.x + self.game.zoom * (j + self.game.figure.x) + 1, 
                                self.game.y + self.game.zoom * (i + self.game.figure.y) + 1, 
                                self.game.zoom - 2, 
                                self.game.zoom - 2
                            ]
                        )
    
    def draw_preview_box(self) -> None:
        """Draw the next piece preview box"""
        if not self.game or not self.game.next_figure:
            return
            
        # Box title
        self.draw_text("NEXT", self.small_font, WHITE, 
                      self.game.preview_x, self.game.y - 30)
        
        # Box background
        preview_bg = pygame.Rect(
            self.game.preview_x - 5,
            self.game.preview_y - 5,
            self.game.zoom * 4 + 10,
            self.game.zoom * 4 + 10
        )
        pygame.draw.rect(self.screen, DARK_GRAY, preview_bg)
        pygame.draw.rect(self.screen, GRAY, preview_bg, 2)
        
        # Draw next piece
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in self.game.next_figure.image():
                    pygame.draw.rect(
                        self.screen,
                        COLORS[self.game.next_figure.color],
                        [
                            self.game.preview_x + self.game.zoom * j,
                            self.game.preview_y + self.game.zoom * i,
                            self.game.zoom - 2,
                            self.game.zoom - 2
                        ]
                    )
    
    def draw_hold_box(self) -> None:
        """Draw the hold piece box"""
        if not self.game:
            return
            
        # Box title
        self.draw_text("HOLD", self.small_font, WHITE, 
                      self.game.hold_x, self.game.y - 30)
        
        # Box background
        hold_bg = pygame.Rect(
            self.game.hold_x - 5,
            self.game.hold_y - 5,
            self.game.zoom * 4 + 10,
            self.game.zoom * 4 + 10
        )
        pygame.draw.rect(self.screen, DARK_GRAY, hold_bg)
        pygame.draw.rect(self.screen, GRAY, hold_bg, 2)
        
        # Draw held piece if exists
        if self.game.held_figure:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.game.held_figure.image():
                        # Use a dimmed color if can't hold
                        color = COLORS[self.game.held_figure.color]
                        if not self.game.can_hold:
                            # Create a dimmed version of the color
                            color = tuple(max(c // 2, 0) for c in color)
                            
                        pygame.draw.rect(
                            self.screen,
                            color,
                            [
                                self.game.hold_x + self.game.zoom * j,
                                self.game.hold_y + self.game.zoom * i,
                                self.game.zoom - 2,
                                self.game.zoom - 2
                            ]
                        )
    
    def draw_stats(self) -> None:
        """Draw game statistics"""
        if not self.game:
            return
            
        # Position for stats
        stats_x = self.game.hold_x
        stats_y = self.game.hold_y + self.game.zoom * 6
        spacing = 30
        
        # Stats background
        stats_bg = pygame.Rect(
            stats_x - 5,
            stats_y - 5,
            self.game.zoom * 4 + 10,
            spacing * 6 + 10
        )
        pygame.draw.rect(self.screen, DARK_GRAY, stats_bg)
        pygame.draw.rect(self.screen, GRAY, stats_bg, 2)
        
        # Draw stats
        self.draw_text("STATS", self.small_font, WHITE, stats_x, stats_y)
        self.draw_text(f"Score: {self.game.score}", self.small_font, WHITE, 
                      stats_x, stats_y + spacing)
        self.draw_text(f"Level: {self.game.level}", self.small_font, WHITE, 
                      stats_x, stats_y + spacing * 2)
        self.draw_text(f"Lines: {self.game.stats.lines_cleared}", self.small_font, WHITE, 
                      stats_x, stats_y + spacing * 3)
        self.draw_text(f"Pieces: {self.game.stats.pieces_placed}", self.small_font, WHITE, 
                      stats_x, stats_y + spacing * 4)
        self.draw_text(f"Time: {self.game.stats.get_duration_str()}", self.small_font, WHITE, 
                      stats_x, stats_y + spacing * 5)
        
        # Draw controls reminder
        controls_y = stats_y + spacing * 7
        controls_bg = pygame.Rect(
            stats_x - 5,
            controls_y - 5,
            self.game.zoom * 4 + 10,
            spacing * 4 + 10
        )
        pygame.draw.rect(self.screen, DARK_GRAY, controls_bg)
        pygame.draw.rect(self.screen, GRAY, controls_bg, 2)
        
        self.draw_text("CONTROLS", self.tiny_font, WHITE, stats_x, controls_y)
        self.draw_text(f"Hold: {self.settings.get_key_name(self.settings.controls['hold'])}", 
                      self.tiny_font, WHITE, stats_x, controls_y + spacing)
        self.draw_text(f"Pause: {self.settings.get_key_name(self.settings.controls['pause'])}", 
                      self.tiny_font, WHITE, stats_x, controls_y + spacing * 2)
        self.draw_text("ESC: Menu", self.tiny_font, WHITE, stats_x, controls_y + spacing * 3)
    
    def draw_game_over(self) -> None:
        """Draw game over screen overlay"""
        if not self.game or self.game.state != "gameover":
            return
            
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(min(200, self.game.game_over_animation * 4))
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        if self.game.game_over_animation > 30:  # Only show when animation is halfway
            self.draw_centered_text("GAME OVER", self.screen.get_height() // 3, 
                                  self.title_font, LIGHT_BLUE)
            
            # Show final score
            score_text = f"Final Score: {self.game.score}"
            self.draw_centered_text(score_text, self.screen.get_height() // 2, self.font)
            
            # Show if it's a high score
            if self.ranking.is_high_score(self.game.score):
                rank = self.ranking.get_rank(self.game.score)
                high_score_text = f"NEW HIGH SCORE! Rank: #{rank}"
                self.draw_centered_text(high_score_text, 
                                      self.screen.get_height() // 2 + 50, 
                                      self.font, GOLD)
            
            # Instructions
            self.draw_centered_text("Press ENTER to continue", 
                                  self.screen.get_height() // 2 + 120, 
                                  self.small_font, GRAY)
    
    def draw_pause_screen(self) -> None:
        """Draw pause screen overlay"""
        if not self.game or not self.game.paused:
            return
            
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        self.draw_centered_text("PAUSED", self.screen.get_height() // 3, 
                              self.title_font, LIGHT_BLUE)
        
        # Instructions
        instructions = [
            f"Press {self.settings.get_key_name(self.settings.controls['pause'])} to resume",
            "Press R to restart",
            "Press ESC to quit to menu"
        ]
        
        for i, instruction in enumerate(instructions):
            self.draw_centered_text(instruction, 
                                  self.screen.get_height() // 2 + i * 50, 
                                  self.small_font)
    
    def draw_level_up_animation(self) -> None:
        """Draw level up animation"""
        if not self.game or self.game.level_up_animation <= 0:
            return
            
        # Flash effect based on animation counter
        if self.game.level_up_animation % 4 < 2:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay.set_alpha(100)
            overlay.fill(GOLD)
            self.screen.blit(overlay, (0, 0))
            
            # Level up text
            self.draw_centered_text(f"LEVEL UP! {self.game.level}", 
                                  self.screen.get_height() // 3, 
                                  self.title_font, WHITE)
    
    def draw_game_screen(self) -> None:
        """Draw the main game screen"""
        self.screen.fill(BLACK)
        
        # Draw game elements
        self.draw_game_field()
        self.draw_preview_box()
        self.draw_hold_box()
        self.draw_stats()
        
        # Draw animations and overlays
        self.draw_level_up_animation()
        self.draw_game_over()
        self.draw_pause_screen()
    
    def handle_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input on the main menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.state = "name_input"
                self.player_name = ""
            elif event.key == pygame.K_2:
                self.state = "ranking"
            elif event.key == pygame.K_3:
                self.state = "settings"
                self.selected_setting = 0
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
    
    def handle_name_input(self, event: pygame.event.Event) -> None:
        """Handle input on the name input screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.player_name) >= 3:
                # Start the game
                self.state = "game"
                self.game = Tetris(20, 10, self.screen.get_width(), self.screen.get_height())
                self.game.new_figure()
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"
            elif len(self.player_name) < 10 and event.unicode.isalnum():
                self.player_name += event.unicode
    
    def handle_ranking_input(self, event: pygame.event.Event) -> None:
        """Handle input on the ranking screen"""
        if event.type == pygame.KEYDOWN:
            self.state = "menu"
    
    def handle_settings_input(self, event: pygame.event.Event) -> None:
        """Handle input on the settings screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "menu"
            elif event.key == pygame.K_UP:
                self.selected_setting = (self.selected_setting - 1) % 8
            elif event.key == pygame.K_DOWN:
                self.selected_setting = (self.selected_setting + 1) % 8
            elif event.key == pygame.K_RETURN:
                if self.selected_setting == 5:  # Configure Controls
                    self.state = "controls"
                    self.selected_setting = 0
                    self.changing_control = None
                elif self.selected_setting == 6:  # Reset to Defaults
                    self.settings.reset_to_defaults()
                    self.update_screen_mode()
                elif self.selected_setting == 7:  # Back to Menu
                    self.state = "menu"
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                # Toggle boolean settings
                if self.selected_setting == 0:  # Fullscreen
                    self.settings.update_setting("fullscreen", 
                                               not self.settings.settings["fullscreen"])
                    self.update_screen_mode()
                elif self.selected_setting == 1:  # Show Ghost
                    self.settings.update_setting("show_ghost", 
                                               not self.settings.settings["show_ghost"])
                elif self.selected_setting == 2:  # Show Grid
                    self.settings.update_setting("show_grid", 
                                               not self.settings.settings["show_grid"])
                # Adjust volume settings
                elif self.selected_setting == 3:  # Music Volume
                    delta = 0.1 if event.key == pygame.K_RIGHT else -0.1
                    new_vol = max(0.0, min(1.0, self.settings.settings["music_volume"] + delta))
                    self.settings.update_setting("music_volume", new_vol)
                elif self.selected_setting == 4:  # SFX Volume
                    delta = 0.1 if event.key == pygame.K_RIGHT else -0.1
                    new_vol = max(0.0, min(1.0, self.settings.settings["sfx_volume"] + delta))
                    self.settings.update_setting("sfx_volume", new_vol)
    
    def handle_controls_input(self, event: pygame.event.Event) -> None:
        """Handle input on the controls screen"""
        if self.changing_control:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Cancel key assignment
                    self.changing_control = None
                else:
                    # Assign new key
                    self.settings.update_control(self.changing_control, event.key)
                    self.changing_control = None
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "settings"
                    self.selected_setting = 5  # Return to Controls option
                elif event.key == pygame.K_UP:
                    self.selected_setting = (self.selected_setting - 1) % 9
                elif event.key == pygame.K_DOWN:
                    self.selected_setting = (self.selected_setting + 1) % 9
                elif event.key == pygame.K_RETURN:
                    if self.selected_setting == 8:  # Back option
                        self.state = "settings"
                        self.selected_setting = 5  # Return to Controls option
                    else:
                        # Start changing a control
                        control_actions = list(self.settings.controls.keys())
                        self.changing_control = control_actions[self.selected_setting]
    
    def handle_game_input(self, event: pygame.event.Event) -> None:
        """Handle input during gameplay"""
        if not self.game:
            return
            
        if event.type == pygame.KEYDOWN:
            # Game controls
            if self.game.state == "start" and not self.game.paused:
                # Movement and rotation
                if event.key == self.settings.controls["move_left"]:
                    self.game.go_side(-1)
                elif event.key == self.settings.controls["move_right"]:
                    self.game.go_side(1)
                elif event.key == self.settings.controls["rotate_ccw"]:
                    self.game.rotate()
                elif event.key == self.settings.controls["rotate_cw"]:
                    self.game.rotate(True)
                elif event.key == self.settings.controls["soft_drop"]:
                    self.game.go_down(True)
                elif event.key == self.settings.controls["hard_drop"]:
                    self.game.go_space()
                elif event.key == self.settings.controls["hold"]:
                    self.game.hold()
                
            # Pause toggle
            if event.key == self.settings.controls["pause"] and self.game.state == "start":
                self.game.toggle_pause()
                
            # Other controls
            if event.key == pygame.K_r and (self.game.paused or self.game.state == "gameover"):
                # Restart game
                self.game.restart()
            elif event.key == pygame.K_ESCAPE:
                if self.game.paused or self.game.state == "gameover":
                    # Return to menu
                    self.state = "menu"
                else:
                    # Pause the game
                    self.game.toggle_pause()
            elif event.key == pygame.K_RETURN and self.game.state == "gameover":
                # Game over - add score to ranking
                if self.game.game_over_animation <= 0:
                    is_high_score = self.ranking.add_score(
                        self.player_name, self.game.score, self.game.stats)
                    self.state = "ranking" if is_high_score else "menu"
                    
        elif event.type == pygame.KEYUP:
            # Handle key releases
            pass
    
    def handle_input(self) -> None:
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            # Route input handling based on game state
            if self.state == "menu":
                self.handle_menu_input(event)
            elif self.state == "name_input":
                self.handle_name_input(event)
            elif self.state == "ranking":
                self.handle_ranking_input(event)
            elif self.state == "settings":
                self.handle_settings_input(event)
            elif self.state == "controls":
                self.handle_controls_input(event)
            elif self.state == "game":
                self.handle_game_input(event)
    
    def update_game(self) -> None:
        """Update game state"""
        if self.state == "game" and self.game:
            # Update animations
            if self.game.level_up_animation > 0:
                self.game.level_up_animation -= 1
                
            if self.game.game_over_animation > 0:
                self.game.game_over_animation -= 1
                
            # Update game logic
            if not self.game.paused:
                self.game.update()
    
    def run(self) -> None:
        """Main game loop"""
        running = True
        while running:
            # Handle input
            self.handle_input()
            
            # Update game state
            self.update_game()
            
            # Draw current screen
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "name_input":
                self.draw_name_input()
            elif self.state == "ranking":
                self.draw_ranking()
            elif self.state == "settings":
                self.draw_settings_menu()
            elif self.state == "controls":
                self.draw_controls_menu()
            elif self.state == "game":
                self.draw_game_screen()
            
            # Update display
            pygame.display.flip()
            
            # Cap framerate
            self.clock.tick(FPS)

# Pygame
pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Tetris Rank")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

font = pygame.font.SysFont('Calibri', 40, True, False)
small_font = pygame.font.SysFont('Calibri', 30, True, False)

clock = pygame.time.Clock()
fps = 25

def draw_text_center(text, y):
    txt = font.render(text, True, WHITE)
    screen.blit(txt, ((screen_width - txt.get_width()) // 2, y))

def menu():
    while True:
        screen.fill(BLACK)
        draw_text_center("1 - Jogar", screen_height//3)
        draw_text_center("2 - Ver Ranking", screen_height//3 + 50)
        draw_text_center("ESC - Sair", screen_height//3 + 100)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "jogar"
                if event.key == pygame.K_2:
                    return "ranking"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); exit()

def get_player_name():
    name = ""
    while True:
        screen.fill(BLACK)
        draw_text_center("Digite seu nome: " + name, screen_height // 2)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name != "":
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10 and event.unicode.isalnum():
                    name += event.unicode

def show_ranking():
    ranking = load_ranking()
    screen.fill(BLACK)
    draw_text_center("Ranking", 50)
    for idx, entry in enumerate(ranking):
        txt = f"{idx+1}. {entry['name']} - {entry['score']}"
        text = small_font.render(txt, True, WHITE)
        screen.blit(text, (100, 150 + idx * 40))
    draw_text_center("Pressione qualquer tecla para voltar", screen_height - 50)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False
            if event.type == pygame.QUIT:
                pygame.quit(); exit()

while True:
    choice = menu()
    if choice == "ranking":
        show_ranking()
    elif choice == "jogar":
        player_name = get_player_name()
        game = Tetris(20, 10, screen_width, screen_height)
        counter = 0
        pressing_down = False
        done = False
        while not done:
            if game.figure is None:
                game.new_figure()
            counter += 1
            if counter > 100000:
                counter = 0
            if counter % (fps // game.level // 2) == 0 or pressing_down:
                if game.state == "start":
                    game.go_down()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game.rotate()
                    if event.key == pygame.K_DOWN:
                        pressing_down = True
                    if event.key == pygame.K_LEFT:
                        game.go_side(-1)
                    if event.key == pygame.K_RIGHT:
                        game.go_side(1)
                    if event.key == pygame.K_SPACE:
                        game.go_space()
                    if event.key == pygame.K_ESCAPE:
                        done = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        pressing_down = False

            screen.fill(BLACK)
            for i in range(game.height):
                for j in range(game.width):
                    pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
                    if game.field[i][j] > 0:
                        pygame.draw.rect(screen, colors[game.field[i][j]], [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

            if game.figure is not None:
                for i in range(4):
                    for j in range(4):
                        p = i * 4 + j
                        if p in game.figure.image():
                            pygame.draw.rect(screen, colors[game.figure.color], [game.x + game.zoom * (j + game.figure.x) + 1, game.y + game.zoom * (i + game.figure.y) + 1, game.zoom - 2, game.zoom - 2])

            score_text = small_font.render("Score: " + str(game.score), True, WHITE)
            screen.blit(score_text, [game.x, game.y - 30])      

            if game.state == "gameover":
                draw_text_center("Game Over", screen_height // 2)
                draw_text_center("Pressione ESC", screen_height // 2 + 50)
                add_score(player_name, game.score)

            pygame.display.flip()
            clock.tick(fps)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()