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
        self.master = master
        self.master.title("Chess")
        self.board = chess.Board()
        self.engine_path = os.path.abspath('stockfish_win/stockfish-windows-x86-64.exe') if self.is_windows() else os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.selected_piece = None  # Track the currently selected piece
        self.current_player = chess.WHITE  # Track the current player (white starts)
        self.white_elo, self.black_elo = self.prompt_for_elo()  # Prompt for ELO scores
        self.create_board()
        self.place_pieces()   
        self.create_evaluation_bars()     
        self.display_elo_scores()  # Display ELO scores
        self.update_evaluation()  # Initial evaluation
        self.button_width = 32  # Initial width of the images
        self.button_height = 32  # Initial height of the images
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }


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
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

 
    def side_labels(self):  # Place labels on the side of the chessboard
        labela = tk.Label(self.master, text=f"a", fg="black")
        labela.grid(row=9, column=0, columnspan=1, sticky="")
        labelb = tk.Label(self.master, text=f"b", fg="black")
        labelb.grid(row=9, column=1, columnspan=1, sticky="")
        labelc = tk.Label(self.master, text=f"c", fg="black")
        labelc.grid(row=9, column=2, columnspan=1, sticky="")
        labeld = tk.Label(self.master, text=f"d", fg="black")
        labeld.grid(row=9, column=3, columnspan=1, sticky="")
        labele = tk.Label(self.master, text=f"e", fg="black")
        labele.grid(row=9, column=4, columnspan=1, sticky="")
        labelf = tk.Label(self.master, text=f"f", fg="black")
        labelf.grid(row=9, column=5, columnspan=1, sticky="")
        labelg = tk.Label(self.master, text=f"g", fg="black")
        labelg.grid(row=9, column=6, columnspan=1, sticky="")
        labelh = tk.Label(self.master, text=f"h", fg="black")
        labelh.grid(row=9, column=7, columnspan=1, sticky="")
        label1 = tk.Label(self.master, text=f"8", fg="black")
        label1.grid(row=0, column=8, columnspan=1, sticky="")
        label2 = tk.Label(self.master, text=f"7", fg="black")
        label2.grid(row=1, column=8, columnspan=1, sticky="")
        label3 = tk.Label(self.master, text=f"6", fg="black")
        label3.grid(row=2, column=8, columnspan=1, sticky="")
        label4 = tk.Label(self.master, text=f"5", fg="black")
        label4.grid(row=3, column=8, columnspan=1, sticky="")
        label5 = tk.Label(self.master, text=f"4", fg="black")
        label5.grid(row=4, column=8, columnspan=1, sticky="")
        label6 = tk.Label(self.master, text=f"3", fg="black")
        label6.grid(row=5, column=8, columnspan=1, sticky="")
        label7 = tk.Label(self.master, text=f"2", fg="black")
        label7.grid(row=6, column=8, columnspan=1, sticky="")
        label8 = tk.Label(self.master, text=f"1", fg="black")
        label8.grid(row=7, column=8, columnspan=1, sticky="")
    
    def place_pieces(self): # Place the pieces along with their images on the board
        piece_images = {
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
        button_width = 32  # Default width of the button
        button_height = 32  # Default height of the button
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                color = 'white' if piece.color == chess.WHITE else 'black'
                row, col = divmod(square, 8)
                image = piece_images[piece.piece_type][piece.color].resize((button_width, button_height))
                photo_image = ImageTk.PhotoImage(image)
                button = self.buttons[7 - row][col]
                button.config(image=photo_image)
                button.image = photo_image  
            else:
                row, col = divmod(square, 8)
                button = self.buttons[7 - row][col]
                button.config(image='')  
    

    # def place_pieces(self):
    #     piece_symbols = {
    #         chess.PAWN: 'P', chess.KNIGHT: 'N', chess.BISHOP: 'B',
    #         chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'
    #     }
    #     for square in chess.SQUARES:
    #         piece = self.board.piece_at(square)
    #         if piece:
    #             symbol = piece_symbols.get(piece.piece_type, '')
    #             color = 'white' if piece.color == chess.WHITE else 'black'
    #             row, col = divmod(square, 8)
    #             self.buttons[row][col].config(text=symbol, fg=color)
    #         else:
    #             row, col = divmod(square, 8)
    #             self.buttons[row][col].config(text='', fg='black')



    def create_increase_image_size_button(self): # Create an "increase image size" button
        self.increase_image_size_button = tk.Button(self.master, text="Increase Image Size", command=self.increase_image_size)
        self.increase_image_size_button.grid(row=13, column=9, columnspan=1, pady=5)

    def increase_image_size(self):
        if self.button_width < 64:  # Set a max width for the images
            self.button_width += 8  # Increase the width of the images
        if self.button_height < 64:  # Set a max height for the image
            self.button_height += 8  # Increase the height of the images
        self.update_image_size()    # Update the image sizes of the pieces

    def create_decrease_image_size_button(self): # Create a "decrease image size" button
        self.increase_image_size_button = tk.Button(self.master, text="Decrease Image Size", command=self.decrease_image_size)
        self.increase_image_size_button.grid(row=14, column=9, columnspan=8, pady=5) 

    def decrease_image_size(self):
        if self.button_width > 16 :  # Set a min width for the images
            self.button_width -= 8  # Decrease the width of the images
        if self.button_height > 16:  # Set a min height for the images
            self.button_height -= 8  # Decrease the height of the images
        self.update_image_size()   # Update the image sizes of the pieces

    def update_image_size(self): # Update image size based on the increasement or decreasement of the images
        piece_images = {
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
                chess.BLACK: Image.open(os.path.abspath("chess_pieces/black/bishop.png"))
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
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                color = 'white' if piece.color == chess.WHITE else 'black'
                row, col = divmod(square, 8)
                image = piece_images[piece.piece_type][piece.color].resize((self.button_width, self.button_height))
                photo_image = ImageTk.PhotoImage(image)
                button = self.buttons[7 - row][col]
                button.config(image=photo_image)
                button.image = photo_image
    
    def create_evaluation_bars(self): # Create evaluation bars for each player
        white_elo_label1 = tk.Label(self.master, text=f"White Evaluation", fg="black")
        white_elo_label1.grid(row=10, column=1, columnspan=2, sticky="")
        black_elo_label1 = tk.Label(self.master, text=f"Black Evaluation", fg="black")
        black_elo_label1.grid(row=10, column=5, columnspan=2, sticky="")
        self.black_bar = tk.Scale(self.master, from_=-100, to=100, orient="horizontal", resolution=0.1)
        self.black_bar.grid(row=11, column=0, columnspan=4, sticky="ew")
        self.white_bar = tk.Scale(self.master, from_=-100, to=100, orient="horizontal", resolution=0.1)
        self.white_bar.grid(row=11, column=4, columnspan=4, sticky="ew")


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
        print("Evaluation finished")
        return np.dot(pVec, npEvals)
    
    def update_evaluation(self):    # Updates evaluation
        if not self.board.is_game_over():
            current_evaluation = self.evaluate_position()
            print(current_evaluation)
            if current_evaluation is not None:
                self.white_bar.set(current_evaluation)
                self.black_bar.set(-current_evaluation)

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
