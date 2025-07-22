import tkinter as tk
from tkinter import messagebox, filedialog
import chess
import chess.pgn
import threading
import time
import random

PIECE_VALUES = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
}

def evaluate(board):
    score = 0
    for piece_type in PIECE_VALUES:
        score += PIECE_VALUES[piece_type] * (
            len(board.pieces(piece_type, chess.WHITE)) -
            len(board.pieces(piece_type, chess.BLACK))
        )
    return score

def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate(board), None

    best_moves = []
    best_eval = -float('inf') if is_maximizing else float('inf')

    for move in board.legal_moves:
        board.push(move)
        eval, _ = minimax(board, depth - 1, alpha, beta, not is_maximizing)
        board.pop()

        if is_maximizing:
            if eval > best_eval:
                best_eval = eval
                best_moves = [move]
            elif eval == best_eval:
                best_moves.append(move)
            alpha = max(alpha, eval)
        else:
            if eval < best_eval:
                best_eval = eval
                best_moves = [move]
            elif eval == best_eval:
                best_moves.append(move)
            beta = min(beta, eval)

        if beta <= alpha:
            break

    return best_eval, random.choice(best_moves) if best_moves else None

class ChessGUI:
    def __init__(self, root, mode):
        self.root = root
        self.root.title("Chess GUI")
        self.board = chess.Board()
        self.turn = tk.StringVar(value="White to move")
        self.mode = mode
        self.move_history = []
        self.selected_square = None
        self.highlighted = []
        self.timer_white = 300
        self.timer_black = 300
        self.game_started = True
        self.ai_playing = False
        self.create_interface()
        self.update_timers()
        self.draw_board()

        if self.mode == "pvc" and self.board.turn == chess.BLACK:
            self.root.after(500, self.start_ai_move)

    def create_interface(self):
        top = tk.Frame(self.root)
        top.pack()

        info = tk.Frame(self.root)
        tk.Label(info, textvariable=self.turn, font=("Arial", 14)).pack(side="left", padx=10)
        self.label_w = tk.Label(info, text=self.fmt_time(self.timer_white), font=("Arial", 14))
        self.label_w.pack(side="left", padx=10)
        self.label_b = tk.Label(info, text=self.fmt_time(self.timer_black), font=("Arial", 14))
        self.label_b.pack(side="left", padx=10)
        info.pack()

        self.canvas = tk.Canvas(self.root, width=640, height=660)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        ctrl = tk.Frame(self.root)
        tk.Button(ctrl, text="Undo", command=self.undo).pack(side="left", padx=5)
        tk.Button(ctrl, text="Redo", command=self.redo).pack(side="left", padx=5)
        tk.Button(ctrl, text="Save PGN", command=self.save_pgn).pack(side="left", padx=5)
        ctrl.pack(pady=5)

    def fmt_time(self, secs):
        return time.strftime("%M:%S", time.gmtime(secs))

    def update_timers(self):
        if self.board.is_game_over() or not self.game_started:
            return
        if self.board.turn == chess.WHITE:
            self.timer_white -= 1
            self.label_w.config(text=self.fmt_time(self.timer_white))
        else:
            self.timer_black -= 1
            self.label_b.config(text=self.fmt_time(self.timer_black))
        if self.timer_white == 0 or self.timer_black == 0:
            winner = "Black" if self.timer_white == 0 else "White"
            messagebox.showinfo("Time out", f"{winner} wins on time!")
            self.game_started = False
            return
        self.root.after(1000, self.update_timers)

    def draw_board(self):
        self.canvas.delete("all")
        size = 80
        colors = ["#EEEED2", "#769656"]
        for r in range(8):
            for c in range(8):
                color = colors[(r + c) % 2]
                self.canvas.create_rectangle(c * size, r * size, (c + 1) * size, (r + 1) * size, fill=color)

        # Highlight last move
        if self.move_history:
            last_move = self.move_history[-1]
            for sq in [last_move.from_square, last_move.to_square]:
                r, c = divmod(sq, 8)
                self.canvas.create_rectangle(c * size, (7 - r) * size, (c + 1) * size, (8 - r) * size,
                                             outline="red", width=3)

        self.clear_highlight()
        for sq, piece in self.board.piece_map().items():
            r, c = divmod(sq, 8)
            self.canvas.create_text(c * size + 40, (7 - r) * size + 40,
                                    text=self.piece_unicode(piece), font=("Arial", 36))

        # Add coordinate labels
        for i in range(8):
            self.canvas.create_text(i * size + 40, 645, text=chr(97 + i), font=("Arial", 12))  # a-h
            self.canvas.create_text(5, (7 - i) * size + 40, text=str(i + 1), font=("Arial", 12))  # 1-8

    def piece_unicode(self, p):
        return {"P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
                "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"}[p.symbol()]

    def on_click(self, event):
        if self.ai_playing or not self.game_started:
            return

        size = 80
        col, row = event.x // size, 7 - event.y // size
        sq = chess.square(col, row)
        if self.selected_square is None:
            piece = self.board.piece_at(sq)
            if piece and piece.color == self.board.turn:
                self.selected_square = sq
                self.highlight_moves(sq)
        else:
            moves = [m for m in self.board.legal_moves if m.from_square == self.selected_square]
            dest = None
            for m in moves:
                if m.to_square == sq:
                    dest = m
                    break
            if dest:
                self.make_move(dest)
            self.selected_square = None
            self.clear_highlight()

    def highlight_moves(self, sq):
        self.clear_highlight()
        size = 80
        for m in self.board.legal_moves:
            if m.from_square == sq:
                r, c = divmod(m.to_square, 8)
                rect = self.canvas.create_rectangle(c * size, (7 - r) * size,
                                                    (c + 1) * size, (8 - r) * size,
                                                    outline="blue", width=3)
                self.highlighted.append(rect)

    def clear_highlight(self):
        for item in self.highlighted:
            self.canvas.delete(item)
        self.highlighted.clear()

    def make_move(self, move):
        self.board.push(move)
        self.move_history.append(move)
        self.draw_board()
        self.update_game_state()

        if self.mode == "pvc" and self.game_started and not self.board.is_game_over():
            if self.board.turn == chess.BLACK:
                if not self.ai_playing:
                    self.start_ai_move()

    def start_ai_move(self):
        self.ai_playing = True
        threading.Thread(target=self.do_ai_move, daemon=True).start()

    def do_ai_move(self):
        is_maximizing = (self.board.turn == chess.WHITE)
        eval, move = minimax(self.board, 3, -99999, 99999, is_maximizing)
        time.sleep(0.5)
        self.root.after(0, lambda: self.finish_ai_move(move))

    def finish_ai_move(self, move):
        if move:
            self.make_move(move)
        self.ai_playing = False

    def update_game_state(self):
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            messagebox.showinfo("Checkmate", f"{winner} wins!")
            self.game_started = False
        elif self.board.is_stalemate():
            messagebox.showinfo("Draw", "Stalemate")
            self.game_started = False
        elif self.board.is_insufficient_material():
            messagebox.showinfo("Draw", "Insufficient material")
            self.game_started = False
        player = "White" if self.board.turn == chess.WHITE else "Black"
        self.turn.set(f"{player} to move")

    def undo(self):
        if self.move_history and not self.ai_playing:
            self.board.pop()
            self.move_history.pop()
            self.draw_board()
            self.update_game_state()

    def redo(self):
        messagebox.showinfo("Undo/Redo", "Redo not implemented (requires full history tracking).")

    def save_pgn(self):
        game = chess.pgn.Game()
        node = game
        for mv in self.move_history:
            node = node.add_variation(mv)
        pgn = str(game)
        path = filedialog.asksaveasfilename(defaultextension=".pgn", filetypes=[("PGN files", "*.pgn")])
        if path:
            with open(path, "w") as f:
                f.write(pgn)
            messagebox.showinfo("Saved", f"Game saved to {path}")

class ModeSelection:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Select Mode")
        tk.Label(self.root, text="Select Mode", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="2 Player", font=("Arial", 14),
                  width=15, command=lambda: self.select_mode("pvp")).pack(pady=10)
        tk.Button(self.root, text="Player vs AI", font=("Arial", 14),
                  width=15, command=lambda: self.select_mode("pvc")).pack(pady=10)
        self.root.mainloop()

    def select_mode(self, mode):
        self.root.destroy()
        root = tk.Tk()
        ChessGUI(root, mode)
        root.mainloop()

if __name__ == "__main__":
    ModeSelection()
