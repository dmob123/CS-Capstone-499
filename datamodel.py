import chess
import chess.pgn
import chess.engine
import pandas as pd
import numpy as np
import os

class ChessFeatures:
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
        return self.board.turn

    def switchp(self, player):
        return chess.WHITE if player == chess.BLACK else chess.BLACK

    def features(self, move, maxEval=10000, maxCapture=9):
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

        evalOC = teval - maxEval
        captureOC = maxCapture - material_captured
        deval = teval

        return [isCapture, isPromotion, material_captured, capturable, sacrifice, material_sacrificed, teval, evalOC, captureOC, deval]

def process_pgn_files(directory, engine_path, output_csv, max_entries=10000):
    feature_extractor = ChessFeatures(engine_path)
    all_features = []
    i = 0
    for filename in os.listdir(directory):
        if filename.endswith(".pgn"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as pgn:
                while len(all_features) < max_entries:
                    game = chess.pgn.read_game(pgn)
                    if game is None:
                        break
                    feature_extractor.board.reset()
                    for move in game.mainline_moves():
                        feature_extractor.board.push(move)
                        maxval = np.NINF
                        maxcap = 0
                        for legal_move in feature_extractor.board.legal_moves:
                                maxval = max(maxval, feature_extractor.engine.analyse(feature_extractor.board, chess.engine.Limit(time=0.1))["score"].white().score(mate_score=10000)) 
                                if feature_extractor.board.is_capture(legal_move):
                                        piece = feature_extractor.board.piece_at(legal_move.to_square)
                                        maxcap = max(maxcap, feature_extractor.piece_values[piece.piece_type])
                        for legal_move in feature_extractor.board.legal_moves:
                            features = feature_extractor.features(legal_move)
                            move_played = 1 if legal_move == move else 0
                            white_elo = game.headers.get('WhiteElo', '')
                            black_elo = game.headers.get('BlackElo', '')
                            row = features + [white_elo, black_elo, move_played]
                            all_features.append(row)
                            i += 1
                            if i % 50 == 0: print(i)
                            if len(all_features) >= max_entries:
                                break
                        if len(all_features) >= max_entries:
                            break
                if len(all_features) >= max_entries:
                    break

    # output
    columns = ['IsCapture', 'IsPromotion', 'MaterialCaptured', 'Capturable', 'Sacrifice', 'MaterialSacrificed',
               'TEval', 'EvalOC', 'CaptureOC', 'DEval', 'WhiteElo', 'BlackElo', 'MovePlayed']
    df = pd.DataFrame(all_features, columns=columns)
    df.to_csv(output_csv, index=False)
    feature_extractor.close_engine()

directory = 'filtered_games_by_elo'
engine_path = os.path.abspath('stockfish/stockfish-ubuntu-x86-64-avx2')
output_csv = 'chess_features.csv'
process_pgn_files(directory, engine_path, output_csv)
