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

        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0 
            }
        
        self.board = chess.Board()

        self.engine_path = os.path.abspath('stockfish/stockfish-windows-x86-64.exe') if self.is_windows() else os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.white_material = 39
        self.black_material = 39
            
    
    def features(self, move: chess.Move, maxEval, maxCapture):
        player = self.whose_turn()
        moves = self.board.legal_moves
        piece = self.board.piece_at(move.from_square).piece_type
        piece_moves = len([mi for mi in moves if mi.from_square == move.from_square])
        target_square = move.to_square
        isCapture = self.board.is_capture(move)
        isPromotion = move.promotion
        material_captured = 0
        attackers = self.board.attackers(self.switchp(player), target_square)
        defenders = self.board.attackers(player, target_square)
        if isCapture:
                captured_piece = self.board.piece_at(target_square)
                material_captured = self.piece_values[captured_piece.piece_type]
        capturable = len(attackers) > 0
        sacrifice = len(attackers) > len(defenders)
        material_sacrificed = self.piece_values[piece] if capturable else 0
        eval = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))["score"].white().score(mate_score=10000)


        tboard = self.board.copy()
        tboard.push(move)
        teval = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))["score"].white().score(mate_score=10000)
        evalOC = teval-maxEval
        captureOC = maxCapture-material_captured
        deval = teval-eval
        check = tboard.is_check()
        tboard.turn = player # pretend player can move twice to evaluate his position
        tmoves = tboard.legal_moves 
        dactivity = len(tboard.legal_moves) - len(moves)     # change in total activity
        dpiece_activity = piece_moves - len([mi for mi in tboard.legal_moves if mi.from_square == move.to_square]) # change in piece activity
        tboard.pop()

        return [isCapture, isPromotion, material_captured, capturable, sacrifice, material_sacrificed, teval, evalOC, captureOC, deval, check, dactivity, dpiece_activity]

    def gives_check(self, move: chess.Move) -> bool:
        """ Determines whether the move is a check"""
        tboard = self.board.copy()
        tboard.push(move)
        return tboard.is_check()


    def whose_turn(self):
        """Determines whose turn it is"""
        return chess.WHITE if self.board.turn else chess.BLACK


    def switchp(self, player):
        """switches the player"""
        return chess.WHITE if player == chess.BLACK else chess.BLACK


    def is_windows(self):
        """Determines whether the system is running windows or linux/unix"""
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

    CG = chessGame()
    print("Initialized!")
    print( list(map(CG.board.is_capture, list(CG.board.legal_moves))) )
    # print(list(map(chess.Move.from_uci, CG.board.legal_moves)))
    CG.engine.quit()


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
