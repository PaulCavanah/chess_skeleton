"""
The Engine is the object that optionally updates the GUI, and communicates with the Game object and the Calculation object.
"""

from solved_newest import Solved, PathContainer
from calculation_newest import Calculation

class Engine() :
    def __init__(self, game) :
        self.game = game
        self.sv = Solved()

    def calculate_legals(self): #for the current position, calculate legal moves
        import time
        start = time.time()
        calc = Calculation(self, self.game, 0)
        print(time.time() - start)
        return calc.legal_moves

    def B_changes(self, sq): #white bishop on square sq
        att_squares = self.sv.bishop_att[sq][self.sv.bishop_rays[sq] & self.game.total_occ] - self.game.white_occ #sv_bishop_att[sq][blocker set] -> att squares for sq with blockers at sq. Minus white_occ because can't take own colored pieces
        B_scenarios = []
        for target in att_squares :
            if target in self.game.black_occ : #take black piece
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.B_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.black_occ), (self.take, "B" + self.game.sq_to_str[target])]
            else : #a move to an empty square
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.B_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "B")]
            B_scenarios.append([(sq, target)] + change_list)
        return B_scenarios #for every target that the bishop can move/take from sq, the list of changes.

    def R_changes(self, sq): #white rook on square sq
        att_squares = self.sv.rook_att[sq][self.sv.rook_rays[sq] & self.game.total_occ] - self.game.white_occ  # sv_bishop_att[sq][blocker set] -> att squares for sq with blockers at sq. Minus black_occ because can't take own colored pieces
        R_scenarios = []
        for target in att_squares:
            if target in self.game.black_occ:  # take black piece
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.R_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.black_occ), (self.take, "R" + self.game.sq_to_str[target])]
            else:  # a move to an empty square
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.R_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "R")]
            R_scenarios.append([(sq, target)] + change_list)
        return R_scenarios #for every target that the rook can move/take from sq, the list of changes.

    def Q_changes(self, sq):
        # queen attacks are bishop + rook attack squares
        att_squares = ((self.sv.bishop_att[sq][self.sv.bishop_rays[sq] & self.game.total_occ]) | (self.sv.rook_att[sq][self.sv.rook_rays[sq] & self.game.total_occ])) - self.game.white_occ
        Q_scenarios = []
        for target in att_squares:
            if target in self.game.white_occ:  # take black piece
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.Q_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.black_occ), (self.take, "Q" + self.game.sq_to_str[target])]
            else:  # a move to an empty square
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.Q_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "Q")]
            Q_scenarios.append([(sq, target)] + change_list)
        return Q_scenarios

    def K_changes(self, sq):
        att_squares = self.sv.king_att[sq] - self.game.white_occ
        K_scenarios = []
        #regular king movement
        for target in att_squares:  # generate king attack moves
            if target in self.game.black_occ:  # take white piece
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.K_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.black_occ), (self.take, "K" + self.game.sq_to_str[target])]
            else:  # a move to an empty square
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.K_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "K")]
            for castle in self.game.white_castles:
                change_list.append((self.remove_castle, castle))  # if moving the king, it removes all castles. Don't discard; only remove because they must be appropriately rolled back.
            K_scenarios.append([(sq, target)] + change_list)
        #castles
        if "K" in self.game.white_castles and not {61, 62} & self.game.total_occ:
            if not self.in_check(iterable = (60, 61, 62)) :
                K_scenarios.append([(60, 62)] + [(self.K, "placeholder")])
        if "Q" in self.game.white_castles and not {59, 58, 57} & self.game.total_occ:
            if not self.in_check(iterable = (60, 59, 58)) :
                K_scenarios.append([(60, 58)] + [(self.Q, "placeholder")])
        return K_scenarios

    def P_changes(self, sq):
        #first, the attacks. They are the -7, -9 squares intersected with the union of black occupance and en passant targets
        att_squares = self.sv.wpawn_att[sq] & (self.game.black_occ | self.game.en_passant)
        P_scenarios = []
        for target in att_squares :
            change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.P_occ), (self.remove__, self.game.total_occ),
                           (self.__remove, self.game.black_occ), (self.take, "P" + self.game.sq_to_str[target])]
            P_scenarios.append([(sq, target)] + change_list)
        #second, the pushes.
        if not sq - 8 in self.game.total_occ : #If the -8 squares is occupied, there is no push available, so fuhgeddaboudit.
            change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.P_occ), (self.remove_add, self.game.total_occ),
                           (self.move, "P")]
            P_scenarios.append([(sq, sq-8)] + change_list)
            if sq // 8 == 1 : #2nd rank start; pawn promotion
                for piece in ("Q", "N", "R", "B") :
                    change_list_ = [(self.remove_add, self.game.white_occ), (self.remove__, self.game.P_occ), (self.remove_add, self.game.total_occ),
                                   (self.promotion, piece)]
                    P_scenarios.append([(sq, sq-8)] + change_list_)
            if sq // 8 == 6 and sq - 16 not in self.game.total_occ : #double pawn move viable as well (sq // 8 == 6 means 7th rank)
                change_list.append((self.en_passant, sq-8)) #don't forget to add en_passant
                P_scenarios.append([(sq, sq-16)] + change_list)
        return P_scenarios

    def N_changes(self, sq):
        att_squares = self.sv.knight_att[sq] - self.game.white_occ
        N_scenarios = []
        for target in att_squares :
            if target in self.game.black_occ : #take black piece
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.N_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.black_occ), (self.take, "N" + self.game.sq_to_str[target])]
            else : #move to empty square
                change_list = [(self.remove_add, self.game.white_occ), (self.remove_add, self.game.N_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "N")]
            N_scenarios.append([(sq, target)] + change_list)
        return N_scenarios

    def b_changes(self, sq): #black bishop
        att_squares = self.sv.bishop_att[sq][self.sv.bishop_rays[sq] & self.game.total_occ] - self.game.black_occ  # sv_bishop_att[sq][blocker set] -> att squares for sq with blockers at sq. Minus black_occ because can't take own colored pieces
        b_scenarios = []
        for target in att_squares:
            if target in self.game.white_occ:  # take white piece
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.b_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.white_occ), (self.take, "b" + self.game.sq_to_str[target])]
            else:  # a move to an empty square
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.b_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "b")]
            b_scenarios.append([(sq, target)] + change_list)
        return b_scenarios

    def r_changes(self, sq):
        att_squares = self.sv.rook_att[sq][self.sv.rook_rays[sq] & self.game.total_occ] - self.game.black_occ  # sv_bishop_att[sq][blocker set] -> att squares for sq with blockers at sq. Minus black_occ because can't take own colored pieces
        r_scenarios = []
        for target in att_squares:
            if target in self.game.white_occ:  # take white piece
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.r_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.white_occ), (self.take, "r" + self.game.sq_to_str[target])]
            else:  # a move to an empty square
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.r_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "r")]
            r_scenarios.append([(sq, target)] + change_list)
        return r_scenarios

    def q_changes(self, sq):
        #queen attacks are bishop + rook attack squares
        att_squares = ((self.sv.bishop_att[sq][self.sv.bishop_rays[sq] & self.game.total_occ]) | (self.sv.rook_att[sq][self.sv.rook_rays[sq] & self.game.total_occ])) - self.game.black_occ
        q_scenarios = []
        for target in att_squares:
            if target in self.game.white_occ:  # take white piece
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.q_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.white_occ), (self.take, "q" + self.game.sq_to_str[target])]
            else:  # a move to an empty square
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.q_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "q")]
            q_scenarios.append([(sq, target)] + change_list)
        return q_scenarios

    def k_changes(self, sq):
        att_squares = self.sv.king_att[sq] - self.game.black_occ
        k_scenarios = []
        #regular king movement
        for target in att_squares: #generate king attack moves
            if target in self.game.white_occ:  # take white piece
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.k_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.white_occ), (self.take, "k" + self.game.sq_to_str[target])]
            else:  # a move to an empty square
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.k_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "k")]
            for castle in self.game.black_castles :
                change_list.append((self.remove_castle, castle)) #if moving the king, it removes all castles. Don't discard; only remove because they must be appropriately rolled back.
            k_scenarios.append([(sq, target)] + change_list)
        #castles
        if "k" in self.game.black_castles and not {5, 6} & self.game.total_occ : #generate changes for kingside castle black
            if not self.in_check(iterable = (4, 5, 6)) :
                k_scenarios.append([(4, 6)] + [(self.k, "placeholder")])
        if "q" in self.game.black_castles and not {1, 2, 3} & self.game.total_occ :
            if not self.in_check(iterable = (4, 3, 2)) :
                k_scenarios.append([(4, 2)] + ([self.q, "placeholder"]))
        return k_scenarios

    def p_changes(self, sq):
        # first, the attacks. They are the +7, +9 squares intersected with white occupance and en passant targets
        att_squares = self.sv.bpawn_att[sq] & (self.game.white_occ | self.game.en_passant)
        p_scenarios = []
        for target in att_squares:
            change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.p_occ), (self.remove__, self.game.total_occ),
                           (self.__remove, self.game.white_occ), (self.take, "p" + self.game.sq_to_str[target])]
            p_scenarios.append([(sq, target)] + change_list)
        # second, the pushes.
        if not sq + 8 in self.game.total_occ:  # If the +8 square is occupied, there is no push available, so fuhgeddaboudit.
            change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.p_occ), (self.remove_add, self.game.total_occ),
                           (self.move, "p")]
            p_scenarios.append([(sq, sq + 8)] + change_list)
            if sq // 8 == 6:  # 7th rank start; pawn promotion
                for piece in ("q", "n", "b", "r") :
                    change_list_ = [(self.remove_add, self.game.black_occ), (self.remove__, self.game.p_occ), (self.remove_add, self.game.total_occ),
                                   (self.promotion, piece)]
                    p_scenarios.append([(sq, sq + 8)] + change_list)
            if sq // 8 == 1 and sq + 16 not in self.game.total_occ:  # double pawn move viable as well (sq // 8 == 1 means 2nd rank)
                change_list.append((self.en_passant, sq + 8))  # don't forget to add en_passant
                p_scenarios.append([(sq, sq + 16)] + change_list)
        return p_scenarios

    def n_changes(self, sq):
        att_squares = self.sv.knight_att[sq] - self.game.black_occ
        n_scenarios = []
        for target in att_squares:
            if target in self.game.white_occ:  # take white piece
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.n_occ), (self.remove__, self.game.total_occ),
                               (self.__remove, self.game.white_occ), (self.take, "n" + self.game.sq_to_str[target])]
            else:  # move to empty square
                change_list = [(self.remove_add, self.game.black_occ), (self.remove_add, self.game.n_occ), (self.remove_add, self.game.total_occ),
                               (self.move, "n")]
            n_scenarios.append([(sq, target)] + change_list)
        return n_scenarios

    def remove_add(self, move_tuple, target_set, rollback = False):
        if not rollback : #forward change
            target_set.remove(move_tuple[0])
            target_set.add(move_tuple[1])
        else : #reverse the change
            target_set.add(move_tuple[0])
            target_set.remove(move_tuple[1])

    def __remove(self, move_tuple, target_set, rollback = False):
        if not rollback : #forward change
            target_set.remove(move_tuple[1])
        else :
            target_set.add(move_tuple[1])

    def remove__(self, move_tuple, target_set, rollback = False):
        if not rollback :
            target_set.remove(move_tuple[0])
        else :
            target_set.add(move_tuple[0])

    def en_passant(self, x, target_square, rollback = False):
        """if not rollback :
            self.game.en_passant.add(target_square)
        else :
            self.game.en_passant.remove(target_square)"""
        return

    def promotion(self, move_tuple, piece_str, rollback = False):
        if not rollback :
            self.str_to_set[piece_str].add(move_tuple[1]) #add to the piece-specific set
            self.sq_to_str[move_tuple[1]] = piece_str #update the square-id dictionary
        else : #rollback the above changes
            self.str_to_set[piece_str].remove(move_tuple[1])
            del self.sq_to_str[move_tuple[1]]

    def remove_castle(self, x, castle, rollback = False):
        if not rollback :
            if self.game.to_move : #white
                self.game.white_castles.discard(castle)
            else :
                self.game.black_castles.discard(castle)
        else :
            if self.game.to_move : #black
                self.game.white_castles.add(castle)
            else :
                self.game.black_castles.add(castle)

    def take(self, move_tuple, two_string, rollback = False):
        self.game.update_game_dict()
        if not rollback :
            del self.game.sq_to_str[move_tuple[0]] #first, remove the piece doing the taking from its initial square
            self.game.str_to_set[two_string[1]].remove(move_tuple[1]) #then, remove the piece being taken from the second square
            self.game.sq_to_str[move_tuple[1]] = two_string[0] #finally, set the second square to the piece doing the taking.
        else : #reverse everything
            self.game.sq_to_str[move_tuple[0]] = two_string[0]
            self.game.str_to_set[two_string[1]].add(move_tuple[1])
            self.game.sq_to_str[move_tuple[1]] = two_string[1]

    def move(self, move_tuple, one_string, rollback = False):
        if not rollback :
            del self.game.sq_to_str[move_tuple[0]] #remove the piece from the initial square
            self.game.sq_to_str[move_tuple[1]] = one_string
        else :
            self.game.sq_to_str[move_tuple[0]] = one_string
            del self.game.sq_to_str[move_tuple[1]]

    def K(self, x, y, rollback = False):
        if not rollback :
            self.game.white_occ.add(61)
            self.game.white_occ.add(62)
            self.game.total_occ.add(61)
            self.game.total_occ.add(62)
            self.game.white_occ.remove(60)
            self.game.white_occ.remove(63)
            self.game.total_occ.remove(60)
            self.game.total_occ.remove(63)
            self.game.R_occ.add(61)
            self.game.R_occ.remove(63) #rook displaced from 63 -> 61
            self.game.K_occ.add(62)
            self.game.K_occ.remove(60) #king displaced from 62 -> 60
            del self.game.sq_to_str[60] #60 is empty square
            del self.game.sq_to_str[63] #63 is empty square
            self.game.sq_to_str[61] = "R" #61 is "R"
            self.game.sq_to_str[62] = "K" #62 is "K"
        else : #reverse of everything above - back to before castling
            self.game.white_occ.add(60)
            self.game.white_occ.add(63)
            self.game.total_occ.add(60)
            self.game.total_occ.add(63)
            self.game.white_occ.remove(61)
            self.game.white_occ.remove(62)
            self.game.total_occ.remove(61)
            self.game.total_occ.remove(62)
            self.game.R_occ.add(63)
            self.game.R_occ.remove(61)
            self.game.K_occ.add(60)
            self.game.K_occ.remove(62)
            del self.game.sq_to_str[62]
            del self.game.sq_to_str[61]
            self.game.sq_to_str[63] = "R"
            self.game.sq_to_str[60] = "K"

    def Q(self, x, y, rollback = False):
        if not rollback :
            self.game.white_occ.add(59)
            self.game.white_occ.add(58)
            self.game.total_occ.add(59)
            self.game.total_occ.add(58)
            self.game.white_occ.remove(60)
            self.game.white_occ.remove(56)
            self.game.total_occ.remove(60)
            self.game.total_occ.remove(56)
            self.game.R_occ.add(59)
            self.game.R_occ.remove(56)
            self.game.K_occ.add(58)
            self.game.K_occ.remove(60)
            del self.game.sq_to_str[60]
            del self.game.sq_to_str[56]
            self.game.sq_to_str[59] = "R"
            self.game.sq_to_str[58] = "K"
        else :
            self.game.white_occ.add(60)
            self.game.white_occ.add(56)
            self.game.total_occ.add(60)
            self.game.total_occ.add(56)
            self.game.white_occ.remove(59)
            self.game.white_occ.remove(58)
            self.game.total_occ.remove(58)
            self.game.total_occ.remove(59)
            self.game.R_occ.add(56)
            self.game.R_occ.remove(59)
            self.game.K_occ.add(60)
            self.game.K_occ.remove(58)
            del self.game.sq_to_str[59]
            del self.game.sq_to_str[58]
            self.game.sq_to_str[60] = "K"
            self.game.sq_to_str[56] = "R"

    def k(self, x, y, rollback = False):
        if not rollback :
            self.game.black_occ.add(5)
            self.game.black_occ.add(6)
            self.game.total_occ.add(5)
            self.game.total_occ.add(6)
            self.game.black_occ.remove(4)
            self.game.black_occ.remove(7)
            self.game.total_occ.remove(4)
            self.game.total_occ.remove(7)
            self.game.r_occ.add(5)
            self.game.r_occ.remove(7)
            self.game.k_occ.add(6)
            self.game.k_occ.remove(4)
            del self.game.sq_to_str[4]
            del self.game.sq_to_str[7]
            self.game.sq_to_str[5] = "r"
            self.game.sq_to_str[6] = "k"
        else :
            self.game.black_occ.add(4)
            self.game.black_occ.add(7)
            self.game.total_occ.add(4)
            self.game.total_occ.add(7)
            self.game.black_occ.remove(5)
            self.game.black_occ.remove(6)
            self.game.total_occ.remove(5)
            self.game.total_occ.remove(6)
            self.game.r_occ.add(7)
            self.game.r_occ.remove(5)
            self.game.k_occ.add(4)
            self.game.k_occ.remove(6)
            del self.game.sq_to_str[6]
            del self.game.sq_to_str[5]
            self.game.sq_to_str[7] = "r"
            self.game.sq_to_str[4] = "k"

    def q(self, x, y, rollback = False):
        if not rollback :
            self.game.black_occ.add(2)
            self.game.black_occ.add(3)
            self.game.total_occ.add(2)
            self.game.total_occ.add(3)
            self.game.black_occ.remove(0)
            self.game.black_occ.remove(4)
            self.game.total_occ.remove(0)
            self.game.total_occ.remove(4)
            self.game.r_occ.add(3)
            self.game.r_occ.remove(0)
            self.game.k_occ.add(2)
            self.game.k_occ.remove(4)
            del self.game.sq_to_str[4]
            del self.game.sq_to_str[0]
            self.game.sq_to_str[3] = "r"
            self.game.sq_to_str[2] = "k"
        else :
            self.game.black_occ.add(0)
            self.game.black_occ.add(4)
            self.game.total_occ.add(0)
            self.game.total_occ.add(4)
            self.game.black_occ.remove(2)
            self.game.black_occ.remove(3)
            self.game.total_occ.remove(2)
            self.game.total_occ.remove(3)
            self.game.r_occ.add(0)
            self.game.r_occ.remove(3)
            self.game.k_occ.add(4)
            self.game.k_occ.remove(2)
            del self.game.sq_to_str[3]
            del self.game.sq_to_str[2]
            self.game.sq_to_str[0] = "r"
            self.game.sq_to_str[4] = "k"

    def in_check(self, iterable = None):
        if self.game.to_move : #white king
            if not iterable: #usually, the iterable is checking for whether a castle is valid on a set of squares (e.g. 60, 61, 62 for K) but it may have other uses.
                iterable = self.game.K_occ #single member set
            for pos in iterable:
                total_checks = set()
                total_checks |= (self.sv.knight_att[pos] & self.game.n_occ) #attacks by black knights on the king square
                total_checks |= (self.sv.rook_att[pos][self.sv.rook_rays[pos] & self.game.total_occ] & (self.game.r_occ | self.game.q_occ)) #both black queen and rook attacks on rook attack squares
                total_checks |= (self.sv.bishop_att[pos][self.sv.bishop_rays[pos] & self.game.total_occ] & (self.game.b_occ | self.game.q_occ)) #both black queen and bishop attacks on bishop attack squares
                total_checks |= (self.sv.wpawn_att[pos] & self.game.p_occ) #if black pawns occupy the spaces of a white pawn attack from the king square, they have the ability to attack the king.
                total_checks |= (self.sv.king_att[pos] & self.game.k_occ) #this is only possible if the king itself moves next to another king.
                if total_checks : #if there any at all squares possessing attacking pieces threatening the white king
                    return True
            return None #no checks -> good
        else : #black king
            if not iterable :
                iterable = self.game.k_occ
            for pos in iterable:
                total_checks = set()
                total_checks |= (self.sv.knight_att[pos] & self.game.N_occ)
                total_checks |= (self.sv.rook_att[pos][self.sv.rook_rays[pos] & self.game.total_occ] & (self.game.R_occ | self.game.Q_occ))
                total_checks |= (self.sv.bishop_att[pos][self.sv.bishop_rays[pos] & self.game.total_occ] & (self.game.B_occ | self.game.Q_occ))
                total_checks |= (self.sv.bpawn_att[pos] & self.game.P_occ)
                total_checks |= (self.sv.king_att[pos] & self.game.K_occ)
                if total_checks :
                    return True
            return None

    def make_move(self, move_tuple):
        legals = self.calculate_legals()
        if move_tuple in legals :
            print(f"{move_tuple} is a legal move")
            self.change_maker(move_tuple, legals[move_tuple])
            self.game.to_move = not self.game.to_move  # flip whose turn it is
            self.game.update() #updates .txt file and FEN_record / current state variables
            if self.in_check() :
                if self.to_move : #white
                    print("White is in check")
                else :
                    print("Black is in check")
        else :
            print(f"{move_tuple} is not a legal move")
            return

    def change_maker(self, move_tuple, change_list):
        for function, set_ in change_list : #Applies changes to the game state (according to the move that is being made)
            function(move_tuple, set_, rollback = False)


"""
In order to make sensible moves, the bot has to have a sense of value that determines which move is the best.  

My personal goal for this program is to have an "understanding" of the game inspired by the memory-recall
framework of the neocortex. The way this might be accomplished, put simply, is an "evolved" set of "dimensions" of the game that
are called upon in any position to collectively assess the SEARCH PRIORITY for a sequence of moves. Each dimension is merely 
a scalar variable whose magnitude is assessed either in dependence or independence (haven't determined yet) of other dimensions.
A dimension's goal is to assess (regarding a position) the presence of a singular abstract pattern that contributes or detriments
the choice of legal moves available in a position. It's all about finding the variation that predicts SEARCH PRIORITY and
arranging that variation to select for the moves. 

I don't want to tailor this AI or even this specific architecture for chess, but rather for parsing information that flows into it.
And evolving its structure to solve a problem. So despite being a narrow AI, it will be applicable perhaps to other games. 
This is like how the brain has evolved to learn faster for certain problems relevant to humans, but is still capable of learning
pretty much anything because it statistically takes apart and groups together information that can be pulled from to create stepping
stones to solving the problem. 
"""