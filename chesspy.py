# import tkinter as tk
# import tkinter.simpledialog as simpledialog
# import tkinter.messagebox as messagebox
# import chess
# import chess.engine
# import math
# import os

# class ChessGUI:
#     def __init__(self, master):
#         self.master = master
#         self.master.title("Chess")
#         self.board = chess.Board()
#         self.engine_path = os.path.abspath('stockfish/stockfish-windows-x86-64.exe') if self.is_windows() else os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
#         self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
#         self.selected_piece = None  # Track the currently selected piece
#         self.current_player = chess.WHITE  # Track the current player (white starts)
#         self.white_elo, self.black_elo = self.prompt_for_elo()  # NEW: Prompt for ELO scores
#         # self.white_win_probability, self.black_win_probability = self.calculate_initial_probabilities()
#         self.create_board()
#         self.place_pieces()
#         self.create_evaluation_bars()
#         self.display_elo_scores()  # NEW: Display ELO scores
#         # self.display_win_probabilities()  # NEW: Display initial winning probabilities
#         self.update_evaluation()  # Initial evaluation

#     # def calculate_initial_probabilities(self):
#     #     # Calculate initial winning probabilities based on ELO scores
#     #     delta_elo = self.white_elo - self.black_elo
#     #     probability_white_wins = 1 / (1 + 10 ** (delta_elo / -400))
#     #     probability_black_wins = 1 - probability_white_wins
#     #     return probability_white_wins, probability_black_wins


#     # def update_win_probabilities(self, score):
#     #     #need to adjust the logic based on how evaluation scores are produced
#     #     score_difference = score - 0  # Assuming 0 is the starting score for an even match
#     #     # Adjust probabilities based on score; this formula is purely illustrative
#     #     adjustment_factor = 1 + (score_difference / 10000)  # Example adjustment logic
#     #     if self.current_player == chess.WHITE:
#     #         self.white_win_probability *= adjustment_factor
#     #     else:
#     #         self.black_win_probability *= adjustment_factor
#     #     # Ensure total probability sums to 1 (or close to it, for simplicity)
#     #     total_probability = self.white_win_probability + self.black_win_probability
#     #     self.white_win_probability /= total_probability
#     #     self.black_win_probability /= total_probability
#     #     self.display_win_probabilities()  # Update display after adjustment


#     def place_pieces(self):
#         piece_symbols = {
#             chess.PAWN: 'P', chess.KNIGHT: 'N', chess.BISHOP: 'B',
#             chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'
#         }
#         for square in chess.SQUARES:
#             piece = self.board.piece_at(square)
#             if piece:
#                 symbol = piece_symbols.get(piece.piece_type, '')
#                 color = 'white' if piece.color == chess.WHITE else 'black'
#                 row, col = divmod(square, 8)
#                 self.buttons[row][col].config(text=symbol, fg=color)
#             else:
#                 row, col = divmod(square, 8)
#                 self.buttons[row][col].config(text='', fg='black')

#     def create_evaluation_bars(self):
#         self.black_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal", label="Black Evaluation", fg="black")
#         self.black_bar.grid(row=8, column=0, columnspan=4, sticky="ew")
#         self.white_bar = tk.Scale(self.master, from_=-10000, to=10000, orient="horizontal", label="White Evaluation", fg="black")
#         self.white_bar.grid(row=8, column=4, columnspan=4, sticky="ew")

#     def evaluate_position(self):
#         info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
#         score = info["score"].white().score(mate_score=10000)
#         return score

#     def update_evaluation(self):
#         if not self.board.is_game_over():
#             info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
#             score = info["score"].white().score(mate_score=10000)
#             if score is not None:
#                 self.white_bar.set(score/100)
#                 self.black_bar.set(-score/100)
#                 self.update_win_probabilities(score)  # Update win probabilities based on current evaluation

#     def check_game_end(self):
#         if self.board.is_checkmate():
#             result = "Checkmate. " + ("White wins!" if self.current_player == chess.BLACK else "Black wins!")
#             tk.messagebox.showinfo("Game Over", result)
#         elif self.board.is_stalemate() or self.board.is_insufficient_material():
#             tk.messagebox.showinfo("Game Over", "Draw due to stalemate or insufficient material.")
#         elif self.board.can_claim_threefold_repetition():
#             tk.messagebox.showinfo("Game Over", "Draw due to threefold repetition.")
#         elif self.board.can_claim_fifty_moves():
#             tk.messagebox.showinfo("Game Over", "Draw due to fifty-move rule.")


#     def is_windows(self):
#         return os.name == 'nt'

# def main():
#     root = tk.Tk()
#     gui = ChessGUI(root)
#     root.mainloop()

# if __name__ == "__main__":
#     main()
