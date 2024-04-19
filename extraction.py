import chess
import chess.pgn
import chess.engine
import pandas as pd
import numpy as np
import os

class ChessGame:
    def __init__(self, engine_path):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

    def close_engine(self):
        self.engine.quit()

    def whose_turn(self):
        return chess.WHITE if self.board.turn else chess.BLACK

    def switchp(self, player):
        return chess.WHITE if player == chess.BLACK else chess.BLACK

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

def process_pgn_file(file_path, engine_path, maxentries=70):
    game_processor = ChessGame(engine_path)
    all_data = []
    count = 0
    with open(file_path, 'r', encoding='utf-8') as pgn:
        while len(all_data) < maxentries:
            game = chess.pgn.read_game(pgn)
            # print(f"Now evaluating: {game.headers.get('White', '')}")
            if game is None:
                break
            # print(list(game.mainline_moves()))
            # quit()
            game_processor.board.reset()
            position_count = 0
            moves = list(game.mainline_moves())
            
            # advance to random position
            advancements = int(np.random.random()*len(moves))     # pick a random position
            skipped_moves = moves[:advancements]
            for move in skipped_moves:
                game_processor.board.push(move)           # advance board to chosen position
            considered_moves = moves[advancements:]
            n = len(considered_moves)

            for i, move in enumerate(considered_moves):
                game_processor.board.push(move)
                position_count += 1
                if position_count > 2:                  # max 2 positions considered per game
                    break
                # print(f"Next move = {considered_moves[i]}")
                for legal_move in game_processor.board.legal_moves:
                    features = game_processor.features(legal_move)
                    
                    if i+1 >= n or legal_move != considered_moves[i+1]: 
                        move_played = 0
                    else: move_played = 1
                    # move_played = 1 if legal_move == considered_moves[i+1] else 0
                    white_elo = game.headers.get('WhiteElo', '')
                    black_elo = game.headers.get('BlackElo', '')
                    row = features + [white_elo, black_elo, move_played]
                    all_data.append(row)
                    count += 1
                    if count % 100 == 0: print(count)
                    if len(all_data) >= maxentries:
                        break
                if len(all_data) >= maxentries:
                    break

    df = pd.DataFrame(all_data, columns=['IsCapture', 'IsPromotion', 'MaterialCaptured', 'Capturable',
                                         'Sacrifice', 'MaterialSacrificed', 'TEval', 'WhiteElo', 'BlackElo', 'MovePlayed'])
    df.to_csv('chess_features2.csv', index=False)
    game_processor.close_engine()

pgn_file_path = 'test.pgn'
stockfish_path = os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
process_pgn_file(pgn_file_path, stockfish_path, maxentries=3000)
