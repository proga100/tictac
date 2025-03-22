import tkinter as tk
from tkinter import messagebox, ttk
import sys
import random
import time

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Крестики-Нолики")
        self.root.resizable(False, False)
        
        # Set window icon (optional)
        try:
            self.root.iconbitmap("tictactoe.ico")
        except:
            pass  # Icon file not found, continue without icon
            
        # Game state variables
        self.current_player = 'X'
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.game_over = False
        self.vs_ai = True  # Default mode is vs AI
        self.ai_difficulty = "Medium"  # Default difficulty
        self.current_level = 1
        self.grid_size = 3  # Initial grid size
        
        # Create main frame
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack()
        
        # Create settings frame
        self.settings_frame = tk.Frame(self.main_frame, padx=5, pady=5)
        self.settings_frame.pack(fill='x', pady=5)
        
        # Game mode selection
        self.mode_label = tk.Label(self.settings_frame, text="Режим игры:", font=('Arial', 10))
        self.mode_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.mode_var = tk.StringVar(value="1 Игрок (против ИИ)")
        self.mode_options = ["1 Игрок (против ИИ)", "2 Игрока"]
        self.mode_menu = ttk.Combobox(self.settings_frame, textvariable=self.mode_var, 
                                     values=self.mode_options, width=18, state="readonly")
        self.mode_menu.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.mode_menu.bind("<<ComboboxSelected>>", self.change_game_mode)
        
        # AI difficulty selection
        self.difficulty_label = tk.Label(self.settings_frame, text="Сложность ИИ:", font=('Arial', 10))
        self.difficulty_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.difficulty_var = tk.StringVar(value="Medium")
        self.difficulty_options = ["Easy", "Medium", "Hard"]
        self.difficulty_menu = ttk.Combobox(self.settings_frame, textvariable=self.difficulty_var, 
                                           values=self.difficulty_options, width=18, state="readonly")
        self.difficulty_menu.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.difficulty_menu.bind("<<ComboboxSelected>>", self.change_difficulty)
        
        # Level display
        self.level_label = tk.Label(self.settings_frame, text="Уровень:", font=('Arial', 10))
        self.level_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.level_display = tk.Label(self.settings_frame, text=f"{self.current_level} (сетка {self.grid_size}x{self.grid_size})", 
                                     font=('Arial', 10, 'bold'))
        self.level_display.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Create game board frame
        self.game_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.game_frame.pack()
        
        # Create the buttons for the game board
        self.buttons = []
        self.create_game_board()
        
        # Create control frame
        self.control_frame = tk.Frame(self.main_frame, padx=10, pady=5)
        self.control_frame.pack(fill='x')
        
        # Create status label
        self.status_label = tk.Label(self.control_frame, text=f"Ход игрока: {self.current_player}", 
                                     font=('Arial', 12), pady=10)
        self.status_label.pack()
        
        # Create buttons frame
        self.button_frame = tk.Frame(self.control_frame)
        self.button_frame.pack(pady=5)
        
        # Create restart button
        restart_button = tk.Button(self.button_frame, text="Новая игра", 
                                  command=self.reset_game, padx=10, pady=5)
        restart_button.pack(side=tk.LEFT, padx=5)
        
        # Create exit button
        exit_button = tk.Button(self.button_frame, text="Выход", 
                               command=self.root.destroy, padx=10, pady=5)
        exit_button.pack(side=tk.LEFT, padx=5)
    
    def create_game_board(self):
        # Clear existing buttons if any
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        # Reset buttons list
        self.buttons = []
        
        # Create new board based on current grid size
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                button = tk.Button(self.game_frame, text='', font=('Arial', 24, 'bold'), 
                                  width=5, height=2,
                                  command=lambda row=i, col=j: self.make_move(row, col))
                button.grid(row=i, column=j, padx=5, pady=5)
                row.append(button)
            self.buttons.append(row)
    
    def change_game_mode(self, event=None):
        mode = self.mode_var.get()
        self.vs_ai = mode == "1 Игрок (против ИИ)"
        # Update difficulty selection visibility
        if self.vs_ai:
            self.difficulty_label.grid(row=1, column=0)
            self.difficulty_menu.grid(row=1, column=1)
        else:
            self.difficulty_label.grid_remove()
            self.difficulty_menu.grid_remove()
        # Reset the game with new settings
        self.reset_level()
    
    def change_difficulty(self, event=None):
        self.ai_difficulty = self.difficulty_var.get()
        # Reset the game with new difficulty
        self.reset_game()
    
    def make_move(self, row, col):
        # Check if the game is over or the cell is not empty
        if self.game_over or self.board[row][col] != '':
            return
            
        # Update board data structure
        self.board[row][col] = self.current_player
        
        # Update button text
        self.buttons[row][col].config(text=self.current_player)
        
        # Apply different colors for X and O
        if self.current_player == 'X':
            self.buttons[row][col].config(fg='blue')
        else:
            self.buttons[row][col].config(fg='red')
        
        # Check for winner
        winner = self.check_winner()
        if winner:
            self.game_over = True
            if winner == 'X':  # Player wins
                self.status_label.config(text=f"Игрок {winner} победил!")
                messagebox.showinfo("Уровень пройден!", f"Поздравляем! Вы переходите на следующий уровень.")
                self.root.after(1000, self.advance_level)  # Advance to next level after delay
            else:  # AI wins
                self.status_label.config(text=f"Игрок {winner} победил!")
                messagebox.showinfo("Игра окончена", f"Игрок {winner} победил!")
            return
        
        # Check for draw
        if self.is_board_full():
            self.game_over = True
            self.status_label.config(text="Ничья!")
            messagebox.showinfo("Игра окончена", "Ничья!")
            return
        
        # Switch player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        
        # Update status label
        self.status_label.config(text=f"Ход игрока: {self.current_player}")
        
        # If playing against AI and it's AI's turn (O), make AI move
        if self.vs_ai and self.current_player == 'O' and not self.game_over:
            self.root.after(500, self.make_ai_move)  # Slight delay for better UX
    
    def advance_level(self):
        self.current_level += 1
        
        # Define level progression
        if self.current_level == 2:
            self.grid_size = 4  # Level 2: 4x4 grid
            self.ai_difficulty = "Medium" if self.ai_difficulty == "Easy" else "Hard"
        elif self.current_level == 3:
            self.grid_size = 5  # Level 3: 5x5 grid
            self.ai_difficulty = "Hard"  # Force hard difficulty
        
        # Update level display
        self.level_display.config(text=f"{self.current_level} (сетка {self.grid_size}x{self.grid_size})")
        
        # Update AI difficulty display
        self.difficulty_var.set(self.ai_difficulty)
        
        # Reset the game with new grid size
        self.board = [[''] * self.grid_size for _ in range(self.grid_size)]
        self.game_over = False
        self.current_player = 'X'
        
        # Recreate the game board with new size
        self.create_game_board()
        
        # Reset status label
        self.status_label.config(text=f"Ход игрока: {self.current_player}")
    
    def reset_level(self):
        # Reset to level 1
        self.current_level = 1
        self.grid_size = 3
        self.level_display.config(text=f"{self.current_level} (сетка {self.grid_size}x{self.grid_size})")
        self.reset_game()
    
    def make_ai_move(self):
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
        self.make_move(row, col)
    
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
        win_length = 3  # Number needed in a row to win
        
        # If grid size is larger, adjust win condition
        if self.grid_size > 3:
            win_length = 4 if self.grid_size == 4 else 5
        
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
    
    def reset_game(self):
        # Reset game state variables
        self.game_over = False
        self.current_player = 'X'
        self.board = [[''] * self.grid_size for _ in range(self.grid_size)]
        
        # Reset UI
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.buttons[i][j].config(text='', fg='black')
        
        # Reset status label
        self.status_label.config(text=f"Ход игрока: {self.current_player}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToe(root)
    root.mainloop() 