from tkinter import *
import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import chess
import chess.engine
import math
from PIL import Image, ImageTk
import os

class chessGame:
    
    
    def __init__(self):
        self.board = chess.Board()

        self.engine_path = os.path.abspath('stockfish/stockfish-windows-x86-64.exe') if self.is_windows() else os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            

    def is_windows():
        return os.name == 'nt'


    def evaluate_position(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return 0  # No legal moves implies a stalemate or checkmate scenario
        total_evaluation = 0
        for move in legal_moves:
            # Simulate the move
            self.board.push(move)
            move_evaluation = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))["score"].white().score(mate_score=10000)
            # Undo the move to restore the board
            self.board.pop()
            # probability for each move 
            p_mi = 1 / len(legal_moves)
            total_evaluation += p_mi * move_evaluation
        return total_evaluation



        
    

def main():

    check_os()

    # CG = chessGame()
    # print("Initialized!")
    # print(list(CG.board.legal_moves))
    # print(CG.board)


if __name__ == "__main__":
    main()











# class ChessGUI:
#     def __init__(self, master):
#         self.master = master
#         self.master.title("Chess")
#         self.board = chess.Board()
#         self.engine_path = os.path.abspath('stockfish/stockfish-windows-x86-64.exe')      
#         self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
#         self.selected_piece = None  # Track the currently selected piece
#         self.current_player = chess.WHITE  # Track the current player (white starts)
#         self.white_elo, self.black_elo = self.prompt_for_elo()  # Prompt for ELO scores
#         # self.color_blind = self.prompt_for_color_blind()
#         # self.white_win_probability, self.black_win_probability = self.calculate_initial_probabilities()
#         # self.display_elo_scores()  # Display ELO scores
#         # self.button_width = 32  # Initial width of the images
#         # self.button_height = 32  # Initial height of the images

# def main():
#     root = tk.Tk()
#     gui = ChessGUI(root)
#     root.mainloop()


# if __name__ == "__main__":
#     main()
