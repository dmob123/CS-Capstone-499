from tkinter import *
import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import chess
import chess.engine
import math
from PIL import Image, ImageTk
import os
import pickle
import numpy as np
import pandas as pd

class ChessGUI:
    def __init__(self, master):
        with open('RF_model.pkl', 'rb') as file:
            self.model = pickle.load(file)
        self.piece_images = {
            chess.PAWN: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/pawn.png")),   # User must update path for image
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/pawn.png"))    # User must update path for image
            },
            chess.ROOK: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/rook.png")),   # User must update path for image
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/rook.png"))    # User must update path for image
            },
            chess.KNIGHT: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/knight.png")), # User must update path for image
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/knight.png"))  # User must update path for image
            },
            chess.BISHOP: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/bishop.png")), # User must update path for image
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/bishop.png"))  # User must update path for image
            },
            chess.QUEEN: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/queen.png")),  # User must update path for image
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/queen.png"))   # User must update path for image
            },
            chess.KING: {
                chess.WHITE: Image.open(os.path.abspath("chess_pieces/white/king.png")),   # User must update path for image
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/king.png"))    # User must update path for image
            },
        }
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }
        self.master = master
        self.master.title("Chess")
        self.board = chess.Board()
        self.engine_path = os.path.abspath('stockfish/stockfish-windows-x86-64.exe') if self.is_windows() else os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.selected_piece = None  
        self.current_player = chess.WHITE  
        self.white_elo, self.black_elo = self.prompt_for_elo() 
        self.create_board()
        self.place_pieces()   
        self.create_evaluation_bars()     
        self.display_elo_scores()  
        self.update_evaluation()  
        self.button_width = 32  
        self.button_height = 32  

        


    def prompt_for_elo(self):   # Prompt the user for white and black player's ELO scores 
        white_elo = simpledialog.askinteger("ELO Score", "Enter White player's ELO score:", parent=self.master)
        black_elo = simpledialog.askinteger("ELO Score", "Enter Black player's ELO score:", parent=self.master)
        return white_elo, black_elo
    
    def display_elo_scores(self):
        # Display ELO scores on the game window
        white_elo_label = tk.Label(self.master, text=f"White ELO: {self.white_elo}", fg="black")
        white_elo_label.grid(row=9, column=0, columnspan=4, sticky="w")
        black_elo_label = tk.Label(self.master, text=f"Black ELO: {self.black_elo}", fg="blue")
        black_elo_label.grid(row=9, column=4, columnspan=4, sticky="e")



    def create_board(self):
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                button = tk.Button(self.master, bg=color, width=8, height=4,
                                   command=lambda r=row, c=col: self.on_click(r, c))
                button.grid(row=row, column=col, sticky="nsew") 
                self.buttons[row][col] = button

        for i in range(8):
            self.master.grid_rowconfigure(i, minsize=50)  
            self.master.grid_columnconfigure(i, minsize=50)  

    def place_pieces(self):
        button_width = 50 
        button_height = 50  
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # color = 'white' if piece.color == chess.WHITE else 'black'
                row, col = divmod(square, 8)
                image = self.piece_images[piece.piece_type][piece.color].resize((button_width, button_height))
                photo_image = ImageTk.PhotoImage(image)
                button = self.buttons[row][col]
                button.config(image=photo_image)
                button.image = photo_image  
            else:
                row, col = divmod(square, 8)
                button = self.buttons[row][col]
                button.config(image='')  


    def create_evaluation_bars(self): # Create evaluation bars for each player
        stockfish_eval = tk.Label(self.master, text=f"Engine Evaluation", fg="black")
        stockfish_eval.grid(row=10, column=1, columnspan=2, sticky="")
        human_eval = tk.Label(self.master, text=f"Human Evaluation", fg="black")
        human_eval.grid(row=10, column=5, columnspan=2, sticky="")


        self.engine_bar = tk.Scale(self.master, from_=-100, to=100, orient="horizontal", resolution=0.1)
        self.engine_bar.grid(row=11, column=0, columnspan=4, sticky="ew")
        self.human_bar = tk.Scale(self.master, from_=-100, to=100, orient="horizontal", resolution=0.1)
        self.human_bar.grid(row=11, column=4, columnspan=4, sticky="ew")

    def on_click(self, row, col):
        if not self.board.is_game_over():
            square = chess.square(col, row)
            piece = self.board.piece_at(square)
        if self.selected_piece is None and piece and piece.color == self.current_player:
            self.selected_piece = square  # Select the piece
        elif self.selected_piece is not None:
            move = chess.Move(self.selected_piece, square)
            if move in self.board.legal_moves:
                # pre_move_evaluation = self.evaluate_position()  # Evaluate before making the move
                self.board.push(move)  # Make the move
                # post_move_evaluation = self.evaluate_position()  # Evaluate after making the move
                # move_quality = self.analyze_move_quality(pre_move_evaluation, post_move_evaluation)  # Analyze move quality
                # messagebox.showinfo("Move Quality", move_quality)  # Display move quality feedback

                self.current_player = not self.current_player
                self.place_pieces()
                self.update_evaluation()
                self.check_game_end()
            self.selected_piece = None

    def explain_fen(self, fen):
        parts = fen.split(' ')  # Split the FEN string into its components
        board, turn, castling, en_passant, halfmove, fullmove = parts
        board_rows = board.split('/')   # Translate the board part of FEN to a more understandable format
        board_explanation = "Board setup:\n"
        for row in board_rows:
            readable_row = row.replace('1', '.').replace('2', '..').replace('3', '...').replace('4', '....').replace('5', '.....').replace('6', '......').replace('7', '.......').replace('8', '........')
            board_explanation += f"{readable_row}\n"
        turn_explanation = "White's turn" if turn == 'w' else "Black's turn"    # Explain whose turn it is
        castling_explanation = "Castling rights: " + (castling if castling != '-' else 'None')  # Explain castling rights
        en_passant_explanation = "En passant target square: " + (en_passant if en_passant != '-' else 'None')   # Explain en passant target square
        halfmove_explanation = f"Halfmove clock (for 50-move rule): {halfmove}" # Explain halfmove clock (steps since last capture or pawn move)
        fullmove_explanation = f"Fullmove number: {fullmove}"   # Explain fullmove number (incremented after Black's turn)
        explanation = f"{board_explanation}\n{turn_explanation}\n{castling_explanation}\n{en_passant_explanation}\n{halfmove_explanation}\n{fullmove_explanation}"  # Combine all explanations into one string
        return explanation

    def provide_in_depth_analysis(self):
        info = self.engine.analyse(self.board, chess.engine.Limit(depth=20))
        score = info.get("score", None)
        message = "In-depth Analysis: "
        if score is not None:
            cp = score.white().score(mate_score=10000)
            mate = score.white().mate()
            if mate is not None:
                message += f"Checkmate in {mate} moves by {'White' if mate > 0 else 'Black'}.\n"
            elif cp is not None:
                adv = abs(cp) / 100.0
                message += f"{'White' if cp > 0 else 'Black'} has a {adv:.2f} point advantage. "
                '''
                as of right now i am giving simplistic general analysis of the game on side as the evaluation bars are 
                being updated during the game if we can adjust these but it is not a must
                '''
            # General Analysis based on score
            if abs(cp) < 100:
                message += "The game is relatively balanced. "
            elif abs(cp) < 300:
                message += "Slight advantage, consider developing pieces or controlling the center. "
            else:
                message += "Significant advantage, look for tactical opportunities or increase pressure. "
            pawns = self.board.pieces(chess.PAWN, chess.WHITE) | self.board.pieces(chess.PAWN, chess.BLACK) # Pawn Structure Analysis (Simplistic)
            if len(pawns) < 12:
                message += "Open pawn structure, consider piece mobility and king safety. "
            else:
                message += "Closed pawn structure, consider pawn breaks and space advantage. "
            # King Safety (Very Simplistic)
            if self.board.is_checkmate():
                message += "One of the kings is in checkmate. "
            elif self.board.is_check():
                message += "Active check, consider defensive moves. "
            else:
                message += "No immediate threats, but always consider king safety. "
            # Piece Mobility (Simplistic)
            # Considering the number of legal moves as a proxy for mobility
            num_legal_moves = len(list(self.board.legal_moves))
            if num_legal_moves < 20:
                message += "Limited mobility, consider improving the positioning of your pieces. "
            else:
                message += "Good mobility, look for opportunities to exploit. "
        else:
            message += "Unable to provide an in-depth analysis at this time."
        return message

    def evaluate_position(self):
        print("Evaluation Started")
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return 0  # No legal moves implies a stalemate or checkmate scenario
        total_evaluation = 0


        evals = []

        column_names = ['IsCapture', 'IsPromotion', 'MaterialCaptured', 'Capturable',
                'Sacrifice', 'MaterialSacrificed', 'TEval', 'WhiteElo', 'BlackElo']
        df = pd.DataFrame(columns=column_names)
        print("pre-calculating")
        for move in legal_moves:
            # Simulate the move
            self.board.push(move)
            move_evaluation = self.engine.analyse(self.board, chess.engine.Limit(time=0.01))["score"].white().score(mate_score=10000)
            # Undo the move to restore the board
            self.board.pop()


            # probability for each move 
            # p_mi = 1 / len(legal_moves)

            features = self.features(move)
                    
            # move_played = 1 if legal_move == considered_moves[i+1] else 0
            row = features + [self.white_elo, self.black_elo]
            df.loc[len(df)] = row




            evals.append(move_evaluation)
        print("Calc probabilities")
        scaling_factor = 5
        probabilities = np.array(self.model.predict_proba(df))*scaling_factor 
        pVec = np.array(self.softmax(probabilities[:,1])) 
        npEvals = np.array(evals)
        print("Evaluation finished:")
        return np.dot(pVec, npEvals)
    
    def update_evaluation(self):    # Updates evaluation
        if not self.board.is_game_over():
            current_evaluation = self.evaluate_position()
            print(current_evaluation)
            seval = self.engine.analyse(self.board, chess.engine.Limit(time=0.5))["score"].white().score(mate_score=10000)
            if current_evaluation is not None:
                self.human_bar.set(current_evaluation/100)
                self.engine_bar.set(seval/100)

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

    def is_windows(self):
        return os.name == 'nt'

    def whose_turn(self):
        return chess.WHITE if self.board.turn else chess.BLACK


    def switchp(self, player):
        return chess.WHITE if player == chess.BLACK else chess.BLACK


    def softmax(self, x):
        """Adjust values of x such that sum(x)=1, allowing interpretation as probability"""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)

    def features(self, move):
        player = self.whose_turn()
        moves = list(self.board.legal_moves)
        piece = self.board.piece_at(move.from_square).piece_type
        piece_moves = len([mi for mi in moves if mi.from_square == move.from_square])
        target_square = move.to_square
        isCapture = self.board.is_capture(move)
        isPromotion = move.promotion is not None
        material_captured = 0
        attackers = self.board.attackers(self.switchp(player), target_square)
        defenders = self.board.attackers(player, target_square)
        if isCapture:
            captured_piece = self.board.piece_at(target_square)
            material_captured = self.piece_values[captured_piece.piece_type]
        capturable = len(attackers) > 0
        sacrifice = len(attackers) > len(defenders)
        material_sacrificed = self.piece_values[piece] if capturable else 0

        self.board.push(move)
        teval = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))["score"].white().score(mate_score=10000)
        self.board.pop()

        return [isCapture, isPromotion, material_captured, capturable, sacrifice, material_sacrificed, teval]


def main():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
