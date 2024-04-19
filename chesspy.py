import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import chess
import chess.engine
import math
import os

class ChessGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess")
        self.board = chess.Board()
        self.engine_path = os.path.abspath('stockfish/stockfish-windows-x86-64.exe') if self.is_windows() else os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.selected_piece = None  # Track the currently selected piece
        self.current_player = chess.WHITE  # Track the current player (white starts)
        self.white_elo, self.black_elo = self.prompt_for_elo()  # NEW: Prompt for ELO scores
        self.white_win_probability, self.black_win_probability = self.calculate_initial_probabilities()
        self.create_board()
        self.place_pieces()
        self.create_evaluation_bars()
        self.display_elo_scores()  # NEW: Display ELO scores
        self.display_win_probabilities()  # NEW: Display initial winning probabilities
        self.update_evaluation()  # Initial evaluation

    def prompt_for_elo(self):
        # Prompt the user for white and black player's ELO scores
        white_elo = simpledialog.askinteger("ELO Score", "Enter White player's ELO score:", parent=self.master)
        black_elo = simpledialog.askinteger("ELO Score", "Enter Black player's ELO score:", parent=self.master)
        return white_elo, black_elo

    def calculate_initial_probabilities(self):
        # Calculate initial winning probabilities based on ELO scores
        delta_elo = self.white_elo - self.black_elo
        probability_white_wins = 1 / (1 + 10 ** (delta_elo / -400))
        probability_black_wins = 1 - probability_white_wins
        return probability_white_wins, probability_black_wins

    def display_elo_scores(self):
        # Display ELO scores on the game window
        white_elo_label = tk.Label(self.master, text=f"White ELO: {self.white_elo}", fg="black")
        white_elo_label.grid(row=9, column=0, columnspan=4, sticky="w")
        black_elo_label = tk.Label(self.master, text=f"Black ELO: {self.black_elo}", fg="blue")
        black_elo_label.grid(row=9, column=4, columnspan=4, sticky="e")

    def display_win_probabilities(self):
        # Display winning probabilities on the game window
        self.win_prob_label = tk.Label(self.master, text=f"Win Probability - White: {self.white_win_probability*100:.1f}%, Black: {self.black_win_probability*100:.1f}%", fg="green")
        self.win_prob_label.grid(row=10, column=0, columnspan=8)

    def update_win_probabilities(self, score):
        #need to adjust the logic based on how evaluation scores are produced
        score_difference = score - 0  # Assuming 0 is the starting score for an even match
        # Adjust probabilities based on score; this formula is purely illustrative
        adjustment_factor = 1 + (score_difference / 10000)  # Example adjustment logic
        if self.current_player == chess.WHITE:
            self.white_win_probability *= adjustment_factor
        else:
            self.black_win_probability *= adjustment_factor
        # Ensure total probability sums to 1 (or close to it, for simplicity)
        total_probability = self.white_win_probability + self.black_win_probability
        self.white_win_probability /= total_probability
        self.black_win_probability /= total_probability
        self.display_win_probabilities()  # Update display after adjustment

    def create_board(self):
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                button = tk.Button(self.master, bg=color, width=8, height=4,
                                   command=lambda r=row, c=col: self.on_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

    def place_pieces(self):
        piece_symbols = {
            chess.PAWN: 'P', chess.KNIGHT: 'N', chess.BISHOP: 'B',
            chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'
        }
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                symbol = piece_symbols.get(piece.piece_type, '')
                color = 'white' if piece.color == chess.WHITE else 'black'
                row, col = divmod(square, 8)
                self.buttons[row][col].config(text=symbol, fg=color)
            else:
                row, col = divmod(square, 8)
                self.buttons[row][col].config(text='', fg='black')

    def create_evaluation_bars(self):
        self.black_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal", label="Black Evaluation", fg="black")
        self.black_bar.grid(row=8, column=0, columnspan=4, sticky="ew")
        self.white_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal", label="White Evaluation", fg="black")
        self.white_bar.grid(row=8, column=4, columnspan=4, sticky="ew")

    def on_click(self, row, col):
        if not self.board.is_game_over():
            square = chess.square(col, row)
            piece = self.board.piece_at(square)
        if self.selected_piece is None and piece and piece.color == self.current_player:
            self.selected_piece = square  # Select the piece
        elif self.selected_piece is not None:
            move = chess.Move(self.selected_piece, square)
            if move in self.board.legal_moves:
                pre_move_evaluation = self.evaluate_position()  # Evaluate before making the move
                self.board.push(move)  # Make the move
                post_move_evaluation = self.evaluate_position()  # Evaluate after making the move
                move_quality = self.analyze_move_quality(pre_move_evaluation, post_move_evaluation)  # Analyze move quality
                messagebox.showinfo("Move Quality", move_quality)  # Display move quality feedback

                self.current_player = not self.current_player
                self.place_pieces()
                self.update_evaluation()
                self.check_game_end()
            self.selected_piece = None

    def evaluate_position(self):
        info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
        score = info["score"].white().score(mate_score=10000)
        return score

    def analyze_move_quality(self, pre_move_evaluation, post_move_evaluation):
        evaluation_change = post_move_evaluation - pre_move_evaluation
        # Categorize move quality based on evaluation change
        if evaluation_change > 100:
            return "Excellent move"
        elif evaluation_change > 50:
            return "Great move"
        elif evaluation_change > 20:
            return "Good move"
        elif evaluation_change > -20:
            return "Decent move"
        elif evaluation_change > -50:
            return "Questionable move"
        elif evaluation_change > -100:
            return "Bad move"
        else:
            return "Blunder"

    def update_evaluation(self):
        if not self.board.is_game_over():
            info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
            score = info["score"].white().score(mate_score=10000)
            if score is not None:
                self.white_bar.set(score)
                self.black_bar.set(-score)
                self.update_win_probabilities(score)  # Update win probabilities based on current evaluation

    def check_game_end(self):
        if self.board.is_checkmate():
            result = "Checkmate. " + ("White wins!" if self.current_player == chess.BLACK else "Black wins!")
            tk.messagebox.showinfo("Game Over", result)
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            tk.messagebox.showinfo("Game Over", "Draw due to stalemate or insufficient material.")
        elif self.board.can_claim_threefold_repetition():
            tk.messagebox.showinfo("Game Over", "Draw due to threefold repetition.")
        elif self.board.can_claim_fifty_moves():
            tk.messagebox.showinfo("Game Over", "Draw due to fifty-move rule.")


    def is_windows():
        return os.name == 'nt'

def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
