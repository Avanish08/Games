import tkinter as tk
from tkinter import messagebox
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.mode = None
        self.current_player = "X"
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.create_menu()

    def create_menu(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack()

        tk.Label(self.menu_frame, text="Choose Game Mode", font=("Arial", 20)).pack(pady=10)
        tk.Button(self.menu_frame, text="Player vs Player", font=("Arial", 14),
                  command=lambda: self.start_game("pvp")).pack(pady=5)
        tk.Button(self.menu_frame, text="Player vs Computer", font=("Arial", 14),
                  command=lambda: self.start_game("pvc")).pack(pady=5)

    def start_game(self, mode):
        self.mode = mode
        self.menu_frame.destroy()
        self.create_board()

    def create_board(self):
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        for row in range(3):
            for col in range(3):
                button = tk.Button(self.board_frame, text="", font=("Arial", 36), width=5, height=2,
                                   command=lambda r=row, c=col: self.on_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

    def on_click(self, row, col):
        button = self.buttons[row][col]
        if button["text"] == "":
            button["text"] = self.current_player

            if self.check_winner(self.current_player):
                messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
                self.reset_game()
                return
            elif self.is_draw():
                messagebox.showinfo("Game Over", "It's a draw!")
                self.reset_game()
                return

            if self.mode == "pvc":
                self.current_player = "O"  # human is X
                self.root.after(500, self.computer_move)
            else:
                self.current_player = "O" if self.current_player == "X" else "X"

    def computer_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.buttons[r][c]["text"] == ""]
        if empty:
            row, col = random.choice(empty)
            self.buttons[row][col]["text"] = "O"
            if self.check_winner("O"):
                messagebox.showinfo("Game Over", "Computer wins!")
                self.reset_game()
            elif self.is_draw():
                messagebox.showinfo("Game Over", "It's a draw!")
                self.reset_game()
            else:
                self.current_player = "X"

    def check_winner(self, player):
        for i in range(3):
            if all(self.buttons[i][j]["text"] == player for j in range(3)) or \
               all(self.buttons[j][i]["text"] == player for j in range(3)):
                return True
        if all(self.buttons[i][i]["text"] == player for i in range(3)) or \
           all(self.buttons[i][2-i]["text"] == player for i in range(3)):
            return True
        return False

    def is_draw(self):
        return all(self.buttons[row][col]["text"] != "" for row in range(3) for col in range(3))

    def reset_game(self):
        for row in self.buttons:
            for button in row:
                button["text"] = ""
        self.current_player = "X"

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
