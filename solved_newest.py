class Solved() :
    def __init__(self):
        self.path_container = PathContainer()

        #pregame bitboard solving stuff
        self.universe = set(range(64)) #all the squares
        self.bishop_rays = {} #square : attack set
        self.rook_rays = {} #square : attack set
        self.bishop_att = {} #square : {blocker_set : result set}
        self.rook_att = {} #square : {blocker_set : result set}
        self.bpawn_att = {} #square : attack set
        self.wpawn_att = {} #square : attack set
        self.king_att = {} #square : move set
        self.knight_att = {} #square : move set

        self.initialize(solve_mode = "load") #generate all the pregame bitboard stuff above

    def initialize(self, solve_mode = None) : #generates solved dictionaries
        if solve_mode == "save" :
            #only do the bitboard side of things first
            total_bishop_blockers_obj = {}
            total_rook_blockers_obj = {}
            total_bishop_att_obj = {}
            total_rook_att_obj = {}

            for square in range(64) : #bishops solved for any combination of blockers on its attack set
                bishop_attacks_set, solved_bishop_attacks_sets, bishop_bb_attacks, solved_bishop_bbs = self.solve_slider(square, "b")
                self.bishop_att[square] = total_bishop_blockers_obj[square] = solved_bishop_attacks_sets
                self.bishop_rays[square] = total_bishop_att_obj[square] = bishop_attacks_set

            for square in range(64) : #rooks solved for any combination of blockers on its attack set
                rook_attack_set, solved_rook_attacks_sets, rook_bb_attacks, solved_rook_bbs = self.solve_slider(square, "r")
                self.rook_att[square] = total_rook_blockers_obj[square] = solved_rook_attacks_sets
                self.rook_rays[square] = total_rook_att_obj[square] = rook_attack_set

            self.save_object(total_bishop_blockers_obj, "solved_bishops")
            self.save_object(total_bishop_att_obj, "bishop_attacks")
            self.save_object(total_rook_blockers_obj, "solved_rooks")
            self.save_object(total_rook_att_obj, "rook_attacks")

        elif solve_mode == "load" :
            self.bishop_att = self.load_object("solved_bishops")
            self.bishop_rays = self.load_object("bishop_attacks")
            self.rook_att = self.load_object("solved_rooks")
            self.rook_rays = self.load_object("rook_attacks")

        for square in range(64) : #knights solved
            self.knight_att[square] = self.solve_knight(square)

        for square in range(64) : #kings solved
            self.king_att[square] = self.solve_king_attacks(square)

        for square in range(64) : #pawns attacks
            self.bpawn_att[square] = self.solve_pawn_attacks(square, "black")
            self.wpawn_att[square] = self.solve_pawn_attacks(square, "white")

    def save_object(self, obj, filename):
        import pickle
        try:
            with open(f"results/{filename}.pickle", "wb") as f:
                pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as ex:
            print("Error during pickling object (Possibly unsupported):", ex)

    def load_object(self, filename):
        import pickle
        try:
            with open(f"results/{filename}.pickle", "rb") as f:
                return pickle.load(f)
        except Exception as ex:
            print("Error during unpickling object (Possibly unsupported):", ex)

    def bitscan(self, integer):
        return_set = set()
        for i in range(64):
            comparator = 1 << i
            if integer & comparator:
                return_set.add(i)
        return frozenset(return_set)

    def to_bitboard(self, occ_set):
        return_integer = int()
        for occ in occ_set :
            return_integer += 2 ** occ
        return return_integer

    def solve_slider(self, square, piece) :
        # generate_bitboards(square, piece) does three things in sequential order:
        # 1. generates attack bitboard for square, slider piece combination
        # 2. generates blocker bitboards for attack bitboard
        # 3. generates result bitboards for each blocker bitboards

        #1. generate attack bitboard and attack set:
        if piece == "b" : #bishop
            increments = {7, -7, 9, -9} #directions of bishop
        elif piece == "r" : #rook
            increments = {8, -8, 1, -1} #directions of rook
        attack_bitboard = int()
        attack_squares = set() #needed for blocker bitboards
        relevant_paths = [] #needed for result bitboards
        for direction in increments :
            step = direction + square #the step in any direction allows the path to be found
            path = self.path_container.path_finder.get((square, step))
            if path and path.index(step) - path.index(square) == 1: #prevents abnormal path recognition
                piece_index = path.index(square)
                for sq in path[piece_index + 1:] : #excludes first square of the path (the piece)
                    attack_squares.add(sq)
                    attack_bitboard += 2**sq #2 to the power of the square's position is the bit that corresponds to that square in a 64-bit int.
                relevant_paths.append(path)
        attack_squares = frozenset(attack_squares) #freeze the set so it is immutable for later

        #2. generate all combos of blocker bitboards given the attack set from step 1 (and lists of blocked squares per blocker board for step 3):
        from itertools import chain, combinations
        blocker_boards = {} #blocker bitboard : set of squares that it blocks
        blockers_list = []
        #use itertools to generate all of the square combinations required to create the blocker boards through bit exponentiation
        square_combinations = chain.from_iterable(combinations(attack_squares, sq) for sq in range(1, len(attack_squares)))
        for combination in square_combinations :
            blocked_squares = []
            blocker_bitboard = int()
            for sq in combination :
                blocked_squares.append(sq)
                blocker_bitboard += 2 ** sq
            blocker_boards[blocker_bitboard] = blocked_squares
            blockers_list.append(blocker_bitboard)

        #3. Generate all result bitboards for each blocker bitboard:
        #use paths
        solved_blockers = {} #blocker_board : result_bitboard
        solved_blocker_squares = {} #blocker_squares : result_squares (the path version)

        #find result for each blocker_board:
        for blocker_board, squares_list in blocker_boards.items() : #for each blocker board and its blocked squares
            #for each path, find the first blocker (lowest index in the path) if there is one.
            result_board = int()
            result_squares = set()
            for path in relevant_paths :
                path_slice = path[path.index(square) + 1 : ] #only take the slice of the path beyond the square of the piece (that is where the relevant blockers will be)
                #create tuple of square indexes that are in path, then choose the minimum one
                squares_in_path = tuple(path.index(sq) for sq in squares_list if sq in path_slice)
                if not squares_in_path : #empty - no blockers
                    for sq in path[path.index(square) + 1 :] : #for all the squares beyond the piece in this path
                        result_board += 2 ** sq
                        result_squares.add(sq)
                else :
                    for sq in path[path.index(square) + 1 : min(squares_in_path) + 1] :
                        result_board += 2 ** sq
                        result_squares.add(sq)
            solved_blockers[blocker_board] = result_board
            solved_blocker_squares[frozenset(squares_list)] = result_squares
        solved_blocker_squares[frozenset()] = attack_squares #no blockers = attack_squares are the attack set
        solved_blockers[0] = attack_bitboard

        return attack_squares, solved_blocker_squares, attack_bitboard, solved_blockers

    def solve_knight(self, square):
        solved = set()
        for inc in (17, -17, 15, -15, 10, -10, 6, -6) : #directions that knights can move
            target = square + inc
            if target > 63 or target < 0 or abs(square % 8 - target % 8) > 2 : #if the target exceeds the board or the difference in horizontal position is > 2
                continue
            else :
                solved.add(target)
        return solved

    def solve_king_attacks(self, square):
        solved = set()
        for inc in (1, -1, -7, 7, -9, 9, 8, -8) :
            target = square + inc
            if target > 63 or target < 0 or abs(square % 8 - target % 8) > 1 : #if the target exceeds the board or the difference in horizontal position is > 1
                continue
            solved.add(target)
        return solved

    def solve_pawn_attacks(self, square, color):
        solved = set()
        incs = (7, 9) #black = default
        if color == "white" :
            incs = (-i for i in incs)
        for inc in incs :
            target = inc + square
            if target > 63 or target < 0 or abs(target % 8 - square % 8) > 1 : #if the target is out of bounds or more than 1 horizontal distance apart.
                continue
            else :
                solved.add(target)
        return solved

class PathContainer() :
    def __init__(self):
        self.gpc = [] #Generic path container (gpc); all of the paths are located here
        self.spawn_generic_paths()
        self.path_finder = {} #(point_1, point_2) : the path that connects them, if any.
        #Creating path_finder
        for i in range(64):  # start square
            for x in range(64):  # end square
                if i != x:  # start can't be end square
                    for path_tuple in self.gpc :
                        if x in path_tuple and i in path_tuple: #both need to be in the path
                            if i < x and path_tuple[0] < path_tuple[1] :  # If start (i) -> finish (x) is increasing, the path must also be increasing.
                                self.path_finder[(i, x)] = path_tuple
                            elif i > x and path_tuple[0] > path_tuple[1] :  # decreasing from i -> x ; path must also be decreasing
                                self.path_finder[(i, x)] = path_tuple

    def spawn_generic_paths(self): #Spawn all possible generic paths for an 8x8 board into the gpc dict.
        #First, generate N (north) paths:
        for i in range(56, 64) :
            path = tuple(range(i, -1, -8))
            self.gpc.append(path) #e.g. start = 58: (58, 50, 42, 34, 26, 18, 10, 2)
        #Then, generate S (south) paths :
        for i in range(0, 8) :
            path = tuple(range(i, 64, 8))
            self.gpc.append(path) #e.g. path starting at 6: (6, 14, 22, 30, 38, 46, 54, 62)
        #W (west) paths :
        for i in range(7, 64, 8) :
            path = tuple(range(i, i-8, -1))
            self.gpc.append(path) #e.g. path starting at 39: (39, 38, 37, 36, 35, 34, 33, 32)
        #E (east) paths :
        for i in range(0, 64, 8) :
            path = tuple(range(i, i+8, 1))
            self.gpc.append(path) #e.g. path starting at 24: (24, 25, 26, 27, 28, 29, 30, 31)
        #A (northwest diagonal) paths :
        for i in (57, 58, 59, 60, 61, 62, 63, 55, 47, 39, 31, 23, 15) :
            if i >= 57 : #bottom rank A paths
                path = tuple(range(i, (i - ((i % 8) * 9)) - 1, -9)) #it just works; e.g. 62: (62, 53, 44, 35, 26, 17, 8) (range 62, 7, -9)
            else : #right file A paths
                path = tuple(range(i, (i - (int(i/8) * 9)) - 1, -9))#this works too; e.g. 31: (31, 22, 13, 4) (range 31, 3, -9)
            self.gpc.append(path)
        #B (northeast diagonal) paths :
        for i in (8, 16, 24, 32, 40, 48, 56, 57, 58, 59, 60, 61, 62) :
            if i >= 57 : #bottom rank B paths
                path = tuple(range(i, (i - ((63-i) % 8) * 7) - 1 , -7)) #e.g. 59: (59, 52, 45, 38, 31) (range 59, 30, -7)
            else : #left file B paths
                path = tuple(range(i, i - (int(i / 8) * 7) - 1, -7)) #e.g. 32: (32, 25, 18, 11, 4) (range 32, 3, -7)
            self.gpc.append(path)
        #C (southeast diagonal) paths :
        for i in (48, 40, 32, 24, 16, 8, 0, 1, 2, 3, 4, 5, 6) :
            if i < 8 : #top rank C paths
                path = tuple(range(i, i + (63 - i * 9) + 1, 9)) #e.g. 4: (4, 13, 22, 31) (range 4, 32, 9)
            else : #left file C paths
                path = tuple(range(i, i + ((int((63 - i) / 8)) * 9) + 1, 9)) #e.g. 40: (40, 49, 58) (range 40, 59, 9)
            self.gpc.append(path)
        #D (southwest diagonal) paths :
        for i in (1, 2, 3, 4, 5, 6, 7, 15, 23, 31, 39, 47, 55) :
            if i < 7 : #Top rank D paths
                path = tuple(range(i, i + ((i % 7) * 7) + 1, 7)) #e.g. 4: (4, 11, 18, 25, 32) (range 4, 33, 7)
            else : #right file D paths
                path = tuple(range(i, i + (int((63 - i) / 8) * 7) + 1, 7)) #e.g. 31: (31, 38, 45, 52, 59) (range 31, 60, 7)
            self.gpc.append(path)
        #n - knight paths: (I am not too sure if these are entirely necessary)
        for i in range(64) : #for all the squares
            for x in (17, 15, 10, 6, -17, -15, -10, -6): #increment/decrement for knight moves
                if abs((i % 8) - ((i+x) % 8)) > 2 or i+x < 0 or i+x > 63 : #if the increment/decrement of the starting position creates a distance from the knight greater than 2 or i + x is out of bounds.
                    continue
                path = (i, i+x)
                self.gpc.append(path)

