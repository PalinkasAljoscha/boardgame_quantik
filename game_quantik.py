import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from itertools import product, chain
import random
import math 

class QuantikBoard():
    name = "quantik"

    def __init__(self, verbose_output=True):
        self.verbose = verbose_output
        self.tokens = ["C", "H", "S", "T"]
        self.placed = {"w": {s: [] for s in self.tokens},
                  "b": {s: [] for s in self.tokens},   
                 }
        self.fields = tuple(product(range(4), range(4)))
        self.spaces = ([[(x,y) for x in range(4)] for y in range(4)]
                        + [[(y,x) for x in range(4)] for y in range(4)]
                        + [[(y,x) for x in range(0,2) for y in range(0,2)]]
                        + [[(y,x) for x in range(2,4) for y in range(0,2)]]
                        + [[(y,x) for x in range(2,4) for y in range(2,4)]]
                        + [[(y,x) for x in range(0,2) for y in range(2,4)]]
                        )
        self.field_spaceindex_map = {f: self._get_spaces_of_field_as_index(f) for f in self.fields}
        
        self.free_fields = list(product(range(4), range(4)))
        self.forbidden = {"w": {s: [] for s in self.tokens},
                        "b": {s: [] for s in self.tokens},   
                        }
        self.left_pieces = {"w": self.tokens*2,
                       "b": self.tokens*2,   
                       }
        self.player = "w"
        
        self.move_sequence = []

        # self.winning_moves = []

        self.tokens_in_spaces = [['_','_','_','_'] for x in range(12)]
         
        self.winner = None
    
        self.pairwise_space_overlap = self._get_pairwise_space_overlap()

    def _get_pairwise_space_overlap(self):
        overlap_matrix = [[-1 for i in range(16)] for j in range(16)]
        for i,j in product(range(16), range(16)):
            spaces_i = self.field_spaceindex_map[self.fields[i]]
            spaces_j = self.field_spaceindex_map[self.fields[j]]
            overlap_matrix[i][j] = len(set(spaces_i).intersection(spaces_j))
        return overlap_matrix

    def new_field_signature(self, new_field):
        field_idx_seq = [self.fields.index(f) for f, _ in self.move_sequence]
        signature = [self.pairwise_space_overlap[f][self.fields.index(new_field)] for f in field_idx_seq]
        return signature

    def reduce_possible_moves(self, pos_moves):
        pos_moves_signatures = [(self.new_field_signature(f), t) for f, t in pos_moves]
        reduced_pos_moves = [pos_moves[pos_moves_signatures.index(s)] for s in pos_moves_signatures]
        return list(set(reduced_pos_moves))


    def print_board(self, show_filed_enumeration=False):
        """ print with matplotlib """
        N = 4
        plot = np.zeros((N, N))
        annotations = []
        for s, places in self.placed['w'].items():
            for p in places:
                plot[p[0]][p[1]] = 1
                annotations.append((p[1]+0.4,3-p[0]+0.4, s))
        for s, places in self.placed['b'].items():
            for p in places:
                plot[p[0]][p[1]] = 2
                annotations.append((p[1]+0.4,3-p[0]+0.4, s))
        # make a figure + axes
        fig, ax = plt.subplots(1, 1, tight_layout=True)
        # make color map
        my_cmap = colors.ListedColormap(['grey', 'w', 'brown'])
        # draw the grid
        for x in range(N + 1):
            ax.axhline(x, lw=2, color='k', zorder=5)
            ax.axvline(x, lw=2, color='k', zorder=5)
        # draw the boxes
        ax.imshow(plot, interpolation='none', cmap=my_cmap, extent=[0, N, 0, N], zorder=0)
        for a in annotations:
            ax.text(*a, fontsize=22)
        if show_filed_enumeration:
            field_number_annotation = [(y+0.06,3-x+0.06, i) for i, (x,y) in enumerate(product(range(4),range(4)))]
            for a in field_number_annotation:
                ax.text(*a, fontsize=10)   
        # turn off the axis labels
        ax.axis('off')
    
    def get_possible_moves(self, current_player=True, shuffle=False):
        possible_moves = []
        if current_player:
            player = self.player
        else:
            player = self._switch_player(self.player)
        for token in self.left_pieces[player]:
            fields_possible_for_token = set(self.free_fields) - set(self.forbidden[player][token])
            possible_moves += [(field, token) for field in fields_possible_for_token]
        if shuffle:
            random.shuffle(possible_moves)
        return possible_moves

    def make_move(self, move):
        field, token = move
        self.placed[self.player][token].append(field)
        self._update_forbidden(self.player, token, field)
        self.free_fields.remove(field)
        self.left_pieces[self.player].remove(token)
        self._update_tokens_in_spaces(field, token)
        # self._update_winning_moves(field, token)
        self.move_sequence.append(move)
        if self.game_is_won():
            self.winner = self.player
        self.player = self._switch_player(self.player)
        return self
     
    def revert_last_move(self):
        self.player = self._switch_player(self.player)
        self.winner = None
        revert_move = self.move_sequence.pop()
        field, token = revert_move
        self._update_tokens_in_spaces(field, token, revert=True)
        # self._update_winning_moves(field, token)
        self.left_pieces[self.player].append(token)
        self.free_fields.append(field)
        self.placed[self.player][token].remove(field)
        self._update_forbidden(self.player, token, field, revert=True)
        return self

    def game_is_won(self):
        for tokens in self.tokens_in_spaces:
            if sorted(tokens) == self.tokens:
                return True
        return False 

    def _get_spaces_of_field_as_index(self, field):
        spaces_of_field = []
        for i, s in enumerate(self.spaces):
            if field in s:
                spaces_of_field .append(i)
        return spaces_of_field
            
           
    def _switch_player(self, player):  
        return {"w": "b", "b": "w"}[player] 
        
    def _update_forbidden(self, player, token, field, revert=False):
        opponent = self._switch_player(player)
        new_forbidden_fields = self._influence_field_map(field)
        if not revert:
            self.forbidden[opponent][token] = self.forbidden[opponent][token]+new_forbidden_fields
        else:
            for f in new_forbidden_fields:
                self.forbidden[opponent][token].remove(f)
        return self
    
    def _update_tokens_in_spaces(self, field, token, revert=False):
        for i, space in enumerate(self.spaces):
            for j, p in enumerate(space):
                if field == p:
                    if not revert:
                        self.tokens_in_spaces[i][j] = token
                    else:
                        self.tokens_in_spaces[i][j] = '_'
        return self

    def _influence_field_map(self, field):
        x, y = field
        line = [(i, y) for i in range(4) if i != x]
        column = [(x, i) for i in range(4) if i != y]
        a = x + (1 - (x%2)*2)
        b = y + (1 - (y%2)*2)
        square = [(x,b), (a,y), (a,b)]
        return line+column+square

    
class QuantikAI(QuantikBoard):
    def __init__(self):
        super().__init__()

    def play_one_round(self, method_w, method_b, print_out=True):
        method_map = {"w": method_w,"b": method_b}
        while not self.winner:
            self = self.make_AI_move(method=method_map[self.player])
        if print_out:
            print("winner:", self.winner)
            self.print_board()
        return self
        
    def make_AI_move(self, method):
        if self.winner and (self.winner != "draw"):
            print("player", self.winner, "won")
            return self
        elif (len(self.get_possible_moves()) == 0) or (self.winner == "draw"):
            self.winner = "draw"
            print("draw, player", self.player, "cannot move")
            return self
        elif method == "minimax":
            return self.minimax_move()    
        elif method == "random":
            return self.random_move()        
    
    def random_move(self):
        possible_moves = self.get_possible_moves()
        random_move = possible_moves[random.randint(0,len(possible_moves)-1)]
        self.make_move(random_move)
        return self

    def minimax_move(self):
        # first few moves are almost all equivalent, but long to minimax
        if len(self.move_sequence)<3:
            return self.random_move()
        minimax_value = -math.inf
        minimax_move = None
        player = self.player
        pos_moves = self.get_possible_moves(shuffle=True)
        pos_moves_reduced = self.reduce_possible_moves(pos_moves)
        for move in pos_moves_reduced:
            self.make_move(move)
            value = self.alphabeta_minimax(maximizing_player=player, 
                            is_max_turn=False, alpha=-1, beta=+1, depth=0, file=None)
            self.revert_last_move()
            # print(value, end=', ')
            if value >= 1:
                minimax_move = move
                break
            elif (value >= minimax_value):
                minimax_value = value
                minimax_move = move
        self.make_move(minimax_move)
        return self 


    def alphabeta_minimax(self, maximizing_player, is_max_turn, alpha, beta, depth, file):
        # limit child nodes to explore in each depths
        n_explore_per_depth = {0: 18, 1:14, 2:10, 3:7, 4:5, 5:3, 6:2, 7:1, 8:1, 9:1, 10:1, 11:1, 12:1, 13:1, 14:1, 15:1, 16:1}
        if len(self.get_possible_moves()) == 0:
            # print("terminal draw, depth", depth, end="|")
            return 0
        elif (self.winner == maximizing_player):
            # print("terminal win, depth", depth, end="|")
            return 1
        elif (self.winner == self._switch_player(maximizing_player)):
            # print("terminal lose, depth", depth, end="|")
            return -1
        elif depth >= 5:
            return 0
        elif is_max_turn:   
            value = -1
            pos_moves = self.get_possible_moves(shuffle=True)
            pos_moves_reduced = self.reduce_possible_moves(pos_moves)
            for move in pos_moves_reduced:
                self.make_move(move)
                value = max(value, self.alphabeta_minimax(maximizing_player, False, alpha, beta, depth+1, file))
                self.revert_last_move()
                if value >= beta:
                    break
                alpha = max(alpha, value)
            return value
        else:
            #print("|",end="")
            value = +1
            pos_moves = self.get_possible_moves(shuffle=True)
            pos_moves_reduced = self.reduce_possible_moves(pos_moves)
            for move in pos_moves_reduced: 
                self.make_move(move)
                value = min(value, self.alphabeta_minimax(maximizing_player, True, alpha, beta, depth+1, file))
                self.revert_last_move()
                if value <= alpha:
                    break
                beta = min(beta, value)
            return value

        
