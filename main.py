from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
import random

class TicTacToeGame(BoxLayout):
    def __init__(self, **kwargs):
        super(TicTacToeGame, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Game state variables
        self.current_player = 'X'
        self.grid_size = 3
        self.win_length = 3
        self.current_level = 1
        self.vs_ai = True
        self.ai_difficulty = "Medium"
        self.game_over = False
        
        # Create the settings area
        self.settings_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        
        # Game mode selection
        mode_layout = BoxLayout(size_hint=(1, 0.33))
        mode_layout.add_widget(Label(text="Режим игры:"))
        self.mode_button = Button(text="1 Игрок (против ИИ)")
        self.mode_button.bind(on_release=self.toggle_game_mode)
        mode_layout.add_widget(self.mode_button)
        self.settings_layout.add_widget(mode_layout)
        
        # AI difficulty selection
        difficulty_layout = BoxLayout(size_hint=(1, 0.33))
        difficulty_layout.add_widget(Label(text="Сложность ИИ:"))
        self.difficulty_button = Button(text=self.ai_difficulty)
        self.difficulty_button.bind(on_release=self.toggle_difficulty)
        difficulty_layout.add_widget(self.difficulty_button)
        self.settings_layout.add_widget(difficulty_layout)
        
        # Level display
        level_layout = BoxLayout(size_hint=(1, 0.33))
        level_layout.add_widget(Label(text="Уровень:"))
        self.level_label = Label(text=f"{self.current_level} (сетка {self.grid_size}x{self.grid_size})")
        level_layout.add_widget(self.level_label)
        self.settings_layout.add_widget(level_layout)
        
        self.add_widget(self.settings_layout)
        
        # Create game board
        self.game_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        self.add_widget(self.game_layout)
        self.create_game_board()
        
        # Status and controls
        self.controls_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        
        # Status label
        self.status_label = Label(text=f"Ход игрока: {self.current_player}", size_hint=(1, 0.5))
        self.controls_layout.add_widget(self.status_label)
        
        # Buttons
        buttons_layout = BoxLayout(size_hint=(1, 0.5))
        restart_button = Button(text="Новая игра")
        restart_button.bind(on_release=self.reset_game)
        buttons_layout.add_widget(restart_button)
        
        self.controls_layout.add_widget(buttons_layout)
        self.add_widget(self.controls_layout)
        
        # Initialize board data structure
        self.board = [[''] * self.grid_size for _ in range(self.grid_size)]
    
    def create_game_board(self):
        # Clear existing game board
        self.game_layout.clear_widgets()
        
        # Create the grid
        self.grid = GridLayout(cols=self.grid_size)
        self.buttons = []
        
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                btn = Button(text='', font_size=40)
                btn.bind(on_release=lambda btn=btn, row=i, col=j: self.make_move(btn, row, col))
                self.grid.add_widget(btn)
                row.append(btn)
            self.buttons.append(row)
        
        self.game_layout.add_widget(self.grid)
    
    def toggle_game_mode(self, instance):
        if self.vs_ai:
            self.vs_ai = False
            instance.text = "2 Игрока"
        else:
            self.vs_ai = True
            instance.text = "1 Игрок (против ИИ)"
        self.reset_level()
    
    def toggle_difficulty(self, instance):
        if self.ai_difficulty == "Easy":
            self.ai_difficulty = "Medium"
        elif self.ai_difficulty == "Medium":
            self.ai_difficulty = "Hard"
        else:
            self.ai_difficulty = "Easy"
        
        instance.text = self.ai_difficulty
        self.reset_game(None)
    
    def make_move(self, button, row, col):
        # Check if the game is over or the cell is not empty
        if self.game_over or self.board[row][col] != '':
            return
            
        # Update board data structure
        self.board[row][col] = self.current_player
        
        # Update button text
        button.text = self.current_player
        
        # Apply different colors for X and O
        if self.current_player == 'X':
            button.color = (0, 0, 1, 1)  # Blue
        else:
            button.color = (1, 0, 0, 1)  # Red
        
        # Check for winner
        winner = self.check_winner()
        if winner:
            self.game_over = True
            if winner == 'X':  # Player wins
                self.status_label.text = f"Игрок {winner} победил!"
                self.show_popup("Уровень пройден!", "Поздравляем! Вы переходите на следующий уровень.")
                Clock.schedule_once(self.advance_level, 1)  # Advance to next level after delay
            else:  # AI wins
                self.status_label.text = f"Игрок {winner} победил!"
                self.show_popup("Игра окончена", f"Игрок {winner} победил!")
            return
        
        # Check for draw
        if self.is_board_full():
            self.game_over = True
            self.status_label.text = "Ничья!"
            self.show_popup("Игра окончена", "Ничья!")
            return
        
        # Switch player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        
        # Update status label
        self.status_label.text = f"Ход игрока: {self.current_player}"
        
        # If playing against AI and it's AI's turn (O), make AI move
        if self.vs_ai and self.current_player == 'O' and not self.game_over:
            Clock.schedule_once(self.make_ai_move, 0.5)  # Slight delay for better UX
    
    def make_ai_move(self, dt):
        if self.game_over:
            return
            
        # Choose move based on difficulty
        if self.ai_difficulty == "Easy":
            row, col = self.get_easy_ai_move()
        elif self.ai_difficulty == "Medium":
            row, col = self.get_medium_ai_move()
        else:  # Hard
            row, col = self.get_hard_ai_move()
            
        # Make the move
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            self.make_move(self.buttons[row][col], row, col)
    
    def get_easy_ai_move(self):
        # Random move
        empty_cells = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == '':
                    empty_cells.append((i, j))
        
        return random.choice(empty_cells) if empty_cells else (0, 0)
    
    def get_medium_ai_move(self):
        # 50% chance for smart move, 50% for random
        if random.random() < 0.5:
            return self.get_easy_ai_move()
        else:
            return self.get_hard_ai_move()
    
    def get_hard_ai_move(self):
        # First, check if AI can win in the next move
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == '':
                    self.board[i][j] = 'O'  # Try placing O
                    if self.check_winner() == 'O':
                        self.board[i][j] = ''  # Undo move
                        return (i, j)
                    self.board[i][j] = ''  # Undo move
        
        # Second, check if player can win in the next move and block
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == '':
                    self.board[i][j] = 'X'  # Try placing X
                    if self.check_winner() == 'X':
                        self.board[i][j] = ''  # Undo move
                        return (i, j)
                    self.board[i][j] = ''  # Undo move
        
        # Take center if available
        center = self.grid_size // 2
        if self.board[center][center] == '':
            return (center, center)
        
        # Take corners if available
        corners = [(0, 0), (0, self.grid_size-1), 
                  (self.grid_size-1, 0), (self.grid_size-1, self.grid_size-1)]
        empty_corners = [corner for corner in corners if self.board[corner[0]][corner[1]] == '']
        if empty_corners:
            return random.choice(empty_corners)
        
        # Take any empty cell
        return self.get_easy_ai_move()
    
    def check_winner(self):
        win_length = self.win_length
        
        # Check rows
        for i in range(self.grid_size):
            for j in range(self.grid_size - win_length + 1):
                if self.board[i][j] != '' and all(self.board[i][j+k] == self.board[i][j] for k in range(win_length)):
                    return self.board[i][j]
        
        # Check columns
        for i in range(self.grid_size - win_length + 1):
            for j in range(self.grid_size):
                if self.board[i][j] != '' and all(self.board[i+k][j] == self.board[i][j] for k in range(win_length)):
                    return self.board[i][j]
        
        # Check diagonals (top-left to bottom-right)
        for i in range(self.grid_size - win_length + 1):
            for j in range(self.grid_size - win_length + 1):
                if self.board[i][j] != '' and all(self.board[i+k][j+k] == self.board[i][j] for k in range(win_length)):
                    return self.board[i][j]
        
        # Check diagonals (top-right to bottom-left)
        for i in range(self.grid_size - win_length + 1):
            for j in range(win_length - 1, self.grid_size):
                if self.board[i][j] != '' and all(self.board[i+k][j-k] == self.board[i][j] for k in range(win_length)):
                    return self.board[i][j]
        
        return None
    
    def is_board_full(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == '':
                    return False
        return True
    
    def advance_level(self, dt):
        self.current_level += 1
        
        # Define level progression
        if self.current_level == 2:
            self.grid_size = 4  # Level 2: 4x4 grid
            self.win_length = 4  # Need 4 in a row to win
            self.ai_difficulty = "Medium" if self.ai_difficulty == "Easy" else "Hard"
        elif self.current_level == 3:
            self.grid_size = 5  # Level 3: 5x5 grid
            self.win_length = 5  # Need 5 in a row to win
            self.ai_difficulty = "Hard"  # Force hard difficulty
        else:
            # Max level reached, restart at level 1 but keep difficulty at hard
            self.current_level = 1
            self.grid_size = 3
            self.win_length = 3
        
        # Update level display
        self.level_label.text = f"{self.current_level} (сетка {self.grid_size}x{self.grid_size})"
        
        # Update AI difficulty display
        self.difficulty_button.text = self.ai_difficulty
        
        # Reset the game with new grid size
        self.board = [[''] * self.grid_size for _ in range(self.grid_size)]
        self.game_over = False
        self.current_player = 'X'
        
        # Recreate the game board with new size
        self.create_game_board()
        
        # Reset status label
        self.status_label.text = f"Ход игрока: {self.current_player}"
    
    def reset_level(self, *args):
        # Reset to level 1
        self.current_level = 1
        self.grid_size = 3
        self.win_length = 3
        self.level_label.text = f"{self.current_level} (сетка {self.grid_size}x{self.grid_size})"
        self.reset_game(None)
    
    def reset_game(self, instance):
        # Reset game state variables
        self.game_over = False
        self.current_player = 'X'
        self.board = [[''] * self.grid_size for _ in range(self.grid_size)]
        
        # Reset UI
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.buttons[i][j].text = ''
                self.buttons[i][j].color = (1, 1, 1, 1)  # Reset to default color
        
        # Reset status label
        self.status_label.text = f"Ход игрока: {self.current_player}"
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), 
                     size_hint=(0.7, 0.3))
        popup.open()
        Clock.schedule_once(popup.dismiss, 2)  # Auto dismiss after 2 seconds

class TicTacToeApp(App):
    def build(self):
        return TicTacToeGame()

if __name__ == '__main__':
    TicTacToeApp().run() 