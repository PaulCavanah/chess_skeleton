class Game() :
    def __init__(self, FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        #game information:
        self.to_move = None #True = white, False = black
        self.total_moves = 0 #moves elapsed (2 ply each)
        self.FEN_record = [] #loaded in by recover_memory()
        self.current_state = 0 #the current index of game within FEN_record
        self.reset_state()
        self.recover_memory(FEN)

    def reset_state(self):
        self.total_occ = set()
        self.black_occ = set()
        self.b_occ = set()
        self.r_occ = set()
        self.q_occ = set()
        self.n_occ = set()
        self.k_occ = set()
        self.p_occ = set()
        self.white_occ = set()
        self.B_occ = set()
        self.R_occ = set()
        self.Q_occ = set()
        self.N_occ = set()
        self.K_occ = set()
        self.P_occ = set()
        self.black_castles = set()
        self.white_castles = set()
        self.en_passant = set()
        self.sq_to_str = dict() #square : piece string

    def update_game_dict(self):
        self.str_to_set = {"b": self.b_occ, "B": self.B_occ, "R": self.R_occ, "r": self.r_occ,
                           "K": self.K_occ, "k": self.k_occ, "N": self.N_occ, "n": self.n_occ,
                           "P": self.P_occ, "p": self.p_occ, "Q": self.Q_occ, "q": self.q_occ}

    def recover_memory(self, FEN): #recovers memory from game_record.txt if there is anything there
        file = open("game_record.txt", "r")
        lines = file.readlines()
        if lines :
            for line in lines : #puts all of the info into the FEN record
                i = line.index("\n")
                self.FEN_record.append(line[0:i]) #cleaned FEN (no newline accumulation)
            final_index = len(self.FEN_record) - 1
            self.parse_FEN(self.FEN_record[final_index])  # load the latest game
            self.current_state = final_index # save final index as current
            return
        else : #default new game
            self.new_game()
            return

    def write_(self, FEN, clear = False):
        if clear :
            file = open("game_record.txt", "w")
            file.write("")
            file.close()
            return
        file = open("game_record.txt", "a")
        file.write(FEN + "\n")
        file.close()

    def rewrite_file(self):
        file = open("game_record.txt", "w")
        lines = ""
        for FEN in self.FEN_record :
            lines += FEN + "\n"
        file.write(lines)
        file.close()

    def previous(self):
        if self.current_state - 1 < 0 :
            return
        else :
            self.current_state -= 1
            self.parse_FEN(self.FEN_record[self.current_state])

    def next(self):
        if self.current_state + 1 > (len(self.FEN_record) - 1) : #can't index past the length of the record
            return
        else :
            self.current_state += 1
            self.parse_FEN(self.FEN_record[self.current_state])

    def last(self):
        self.current_state = len(self.FEN_record) - 1
        self.parse_FEN(self.FEN_record[self.current_state])

    def new_game(self):
        self.write_(None, clear = True)
        self.parse_FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.FEN_record = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]
        self.current_state = 0
        self.write_("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def update(self):
        new_state = self.export_FEN()
        self.FEN_record = self.FEN_record[0 : self.current_state + 1] #chop off the back part
        self.FEN_record.append(new_state) #add on the new one
        self.current_state += 1
        self.rewrite_file()

    def parse_FEN(self, FEN): #creates the game state based off of a FEN string
        self.reset_state() #wipe the board state
        pieces = {"r" : self.r_occ, "n" : self.n_occ, "b" : self.b_occ, "q" : self.q_occ, "k" : self.k_occ, "p" : self.p_occ,
                  "R" : self.R_occ, "N" : self.N_occ, "B" : self.B_occ, "Q" : self.Q_occ, "K" : self.K_occ, "P" : self.P_occ}
        numbers = {"1", "2", "3", "4", "5", "6", "7", "8"}
        stage = 0
        square_index = 0 #sq number that the iteration is currently on
        en_passant = ""
        for char in FEN :
            if char == " " :
                stage += 1
                continue
            if stage == 0 :
                if char == "/" : #this char is just for the a e s t h e t i c s
                    continue
                elif char in numbers :
                    square_index += int(char)
                    continue
                elif char in pieces :
                    self.sq_to_str[square_index] = char
                    pieces[char].add(square_index)
                    if char.islower() :
                        self.black_occ.add(square_index)
                    else :
                        self.white_occ.add(square_index)
                    self.total_occ.add(square_index)
                    square_index += 1
                    continue
            elif stage == 1 :
                if char == "w" :
                    self.to_move = True
                else :
                    self.to_move = False
            elif stage == 2 :
                if char.islower() :
                    self.black_castles.add(char)
                else :
                    self.white_castles.add(char)
            elif stage == 3 :
                if char == "-" :
                    continue
                else :
                    en_passant += char
                    if len(en_passant) == 2 : #complete
                        en_passant = int((ord(en_passant[0]) - 97) + (8 - int(en_passant[1])) * 8) #convert str to index
                        self.en_passant.add(en_passant)
                        continue
            elif stage == 4 : #I don't care about half-moves
                continue
            elif stage == 5 :
                self.total_moves = int(char)
                stage += 1

    def export_FEN(self): #creates a FEN string based off of the game state
        new_FEN = ""
        space_counter = 0
        for sq in range(64) :
            if sq % 8 == 0 : #new rank; have to put down the space counter int and /
                if space_counter : #if not 0
                    new_FEN += str(space_counter)
                    space_counter = 0
                new_FEN += "/"
            if not sq in self.total_occ :
                space_counter += 1
            else : #square is occupied, add the space counter and then the char to the FEN
                if space_counter : #if not 0
                    new_FEN += str(space_counter)
                    space_counter = 0
                new_FEN += self.sq_to_str[sq]
        if self.to_move :
            new_FEN += " w "
        else :
            new_FEN += " b "
        for castle in self.white_castles :
            new_FEN += castle
        for castle in self.black_castles :
            new_FEN += castle
        new_FEN += " "
        if self.en_passant :
            for sq in self.en_passant : #only one index at most
                algebraic = f"{chr(97 + (sq % 8))}{8 - (sq // 8)}" #letter = horizontal position; number = vertical position
                new_FEN += algebraic
        else :
            new_FEN += "-"
        new_FEN += " 0 " #halfmove + space
        new_FEN += str(self.total_moves)

        return new_FEN
