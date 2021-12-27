"""
The GUI is downstream of the engine; the engine should change the GUI, but the GUI should not change the engine.
Engine -> GUI
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from engine_newest import Engine
from game_newest import Game

class GUI() :
    def __init__(self, main_window) :
        self.game = Game()
        self.engine = Engine(self.game)

        self.setup_attributes() #setup attributes required for setup
        self.setup_main_squares(main_window) #setup the GUI widgets

    def setup_attributes(self):
        self.display_keys = {"R": "images/Chess_rlt60.png", "N": "images/Chess_nlt60.png",
                             "B": "images/Chess_blt60.png",
                             "Q": "images/Chess_qlt60.png", "K": "images/Chess_klt60.png",
                             "P": "images/Chess_plt60.png",
                             "r": "images/Chess_rdt60.png", "n": "images/Chess_ndt60.png",
                             "b": "images/Chess_bdt60.png",
                             "q": "images/Chess_qdt60.png", "k": "images/Chess_kdt60.png",
                             "p": "images/Chess_pdt60.png"}
        self.piece_set = {"R", "r", "B", "b", "P", "p", "N", "n", "Q", "q", "K", "k"}
        self.game.update_game_dict()

    def setup_main_squares(self, MainWindow):
        from clickable_label import ClickableLabel #for potential future use of clickable labels

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1220, 509)
        font = QtGui.QFont()
        font.setPointSize(13)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        left_top = (10, 10)

        self.rank_labels = []
        self.file_labels = []
        self.squares = {i : None for i in range(64)}

        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)

        alphabet = ("A", "B", "C", "D", "E", "F", "G", "H")
        numbers = (8, 7, 6, 5, 4, 3, 2, 1)
        # setup rank labels
        for i in range(8):
            new_label_object = QtWidgets.QLabel(self.centralwidget)
            new_label_object.setGeometry(QtCore.QRect(left_top[0], (left_top[1] + i * 50), 50, 50))
            new_label_object.setFont(font)
            new_label_object.setAlignment(QtCore.Qt.AlignCenter)
            new_label_object.setObjectName(f"label_rank_{numbers[i]}_extra")
            self.rank_labels.append(new_label_object)
        # setup file labels
        for i in range(8):
            new_label_object = QtWidgets.QLabel(self.centralwidget)
            new_label_object.setGeometry(QtCore.QRect((left_top[0] + i * 50) + 50, left_top[1] + 400, 50, 50))
            new_label_object.setFont(font)
            new_label_object.setAlignment(QtCore.Qt.AlignCenter)
            new_label_object.setObjectName(f"label_file_{alphabet[i]}_extra")
            self.file_labels.append(new_label_object)
        # setup square labels
        for i in range(64):
            new_label_object = ClickableLabel(self.centralwidget)
            horizontal_index = i % 8
            vertical_index = i // 8
            left = (left_top[0] + horizontal_index * 50) + 50
            top = (left_top[1] + vertical_index * 50)
            new_label_object.setGeometry(QtCore.QRect(left, top, 50, 50))
            new_label_object.setAlignment(QtCore.Qt.AlignCenter)
            new_label_object.setObjectName(f"label_{alphabet[horizontal_index]}{numbers[vertical_index]}")
            self.squares[i] = new_label_object

        for square, label in self.squares.items() :
            if ((int(square / 8) + square % 8) % 2) == 0 : #determines white/black squares
                label.color("white", init = True)
            else :
                label.color("black", init = True)
            label.setText("")

        self.setup_other()
        self.setup_extra_squares((640, 10))

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.display_board()

    def setup_other(self):
        self.label_to_move = QtWidgets.QLabel(self.centralwidget)
        self.label_to_move.setGeometry(QtCore.QRect(500, 400, 50, 30))
        self.label_to_move.setAlignment(QtCore.Qt.AlignCenter)
        self.label_to_move.setObjectName("to_move")

        self.button_legals = QtWidgets.QPushButton(self.centralwidget)
        self.button_legals.setGeometry(QtCore.QRect(450, 450, 70, 30))
        self.button_legals.setObjectName("button_legals")
        self.button_legals.clicked.connect(lambda : print(self.engine.calculate_legals().keys()))

        self.button_submit = QtWidgets.QPushButton(self.centralwidget)
        self.button_submit.setGeometry(QtCore.QRect(500, 150, 70, 30))
        self.button_submit.setObjectName("button_submit")
        self.button_submit.clicked.connect(self.test_submit)

        self.button_display = QtWidgets.QPushButton(self.centralwidget)
        self.button_display.setGeometry(QtCore.QRect(1100, 150, 70, 30))
        self.button_display.setObjectName("button_display")
        self.button_display.clicked.connect(self.test_display)

        self.input_display_input = QtWidgets.QLineEdit(self.centralwidget)
        self.input_display_input.setGeometry(QtCore.QRect(1100, 200, 100, 30))
        self.input_display_input.setAlignment(QtCore.Qt.AlignCenter)
        self.input_display_input.setObjectName("input_position_input_from")

        self.label_piece_input = QtWidgets.QLabel(self.centralwidget)
        self.label_piece_input.setGeometry(QtCore.QRect(470, 200, 50, 30))
        self.label_piece_input.setAlignment(QtCore.Qt.AlignCenter)
        self.label_piece_input.setObjectName("label_piece_input")

        self.input_piece_input = QtWidgets.QLineEdit(self.centralwidget)
        self.input_piece_input.setGeometry(QtCore.QRect(520, 200, 50, 30))
        self.input_piece_input.setAlignment(QtCore.Qt.AlignCenter)
        self.input_piece_input.setObjectName("input_piece_input")

        self.label_position_input_from = QtWidgets.QLabel(self.centralwidget)
        self.label_position_input_from.setGeometry(QtCore.QRect(470, 250, 50, 30))
        self.label_position_input_from.setAlignment(QtCore.Qt.AlignCenter)
        self.label_position_input_from.setObjectName("label_position_input_from")

        self.input_position_input_from = QtWidgets.QLineEdit(self.centralwidget)
        self.input_position_input_from.setGeometry(QtCore.QRect(520, 250, 50, 30))
        self.input_position_input_from.setAlignment(QtCore.Qt.AlignCenter)
        self.input_position_input_from.setObjectName("input_position_input_from")

        self.label_position_input = QtWidgets.QLabel(self.centralwidget)
        self.label_position_input.setGeometry(QtCore.QRect(470, 300, 50, 30))
        self.label_position_input.setAlignment(QtCore.Qt.AlignCenter)
        self.label_position_input.setObjectName("label_position_input")

        self.input_position_input = QtWidgets.QLineEdit(self.centralwidget)
        self.input_position_input.setGeometry(QtCore.QRect(520, 300, 50, 30))
        self.input_position_input.setAlignment(QtCore.Qt.AlignCenter)
        self.input_position_input.setObjectName("input_position_input")

        self.button_clear = QtWidgets.QPushButton(self.centralwidget)
        self.button_clear.setGeometry(QtCore.QRect(570, 150, 70, 30))
        self.button_clear.setObjectName("button_clear")
        self.button_clear.clicked.connect(lambda : self.clear_board(self.squares))

        self.button_newgame = QtWidgets.QPushButton(self.centralwidget)
        self.button_newgame.setGeometry(QtCore.QRect(20, 450, 120, 30))
        self.button_newgame.setObjectName("button_newgame")
        self.button_newgame.clicked.connect(self.new_game)

        self.button_prev = QtWidgets.QPushButton(self.centralwidget)
        self.button_prev.setGeometry(QtCore.QRect(150, 450, 70, 30))
        self.button_prev.setObjectName("button_prev")
        self.button_prev.clicked.connect(self.prev_state)

        self.button_next = QtWidgets.QPushButton(self.centralwidget)
        self.button_next.setGeometry(QtCore.QRect(250, 450, 70, 30))
        self.button_next.setObjectName("button_prev")
        self.button_next.clicked.connect(self.next_state)

        self.button_last = QtWidgets.QPushButton(self.centralwidget)
        self.button_last.setGeometry(QtCore.QRect(350, 450, 70, 30))
        self.button_last.setObjectName("button_prev")
        self.button_last.clicked.connect(self.last_state)

    def setup_extra_squares(self, left_top):
        from clickable_label import ClickableLabel #for potential future use of clickable labels

        self.extra_rank_labels = []
        self.extra_file_labels = []
        self.extra_squares = {i : None for i in range(64)}

        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)

        alphabet = ("A", "B", "C", "D", "E", "F", "G", "H")
        numbers = (8, 7, 6, 5, 4, 3, 2, 1)
        #setup rank labels
        for i in range(8) :
            new_label_object = QtWidgets.QLabel(self.centralwidget)
            new_label_object.setGeometry(QtCore.QRect(left_top[0], (left_top[1] + i * 50), 50, 50))
            new_label_object.setFont(font)
            new_label_object.setAlignment(QtCore.Qt.AlignCenter)
            new_label_object.setObjectName(f"label_rank_{numbers[i]}_extra")
            self.extra_rank_labels.append(new_label_object)
        #setup file labels
        for i in range(8) :
            new_label_object = QtWidgets.QLabel(self.centralwidget)
            new_label_object.setGeometry(QtCore.QRect((left_top[0] + i * 50) + 50, left_top[1] + 400, 50, 50))
            new_label_object.setFont(font)
            new_label_object.setAlignment(QtCore.Qt.AlignCenter)
            new_label_object.setObjectName(f"label_file_{alphabet[i]}_extra")
            self.extra_file_labels.append(new_label_object)
        #setup square labels
        for i in range(64) :
            new_label_object = ClickableLabel(self.centralwidget)
            horizontal_index = i % 8
            vertical_index = i // 8
            left = (left_top[0] + horizontal_index * 50) + 50
            top = (left_top[1] + vertical_index * 50)
            new_label_object.setGeometry(QtCore.QRect(left, top, 50, 50))
            new_label_object.setAlignment(QtCore.Qt.AlignCenter)
            new_label_object.setObjectName(f"label_{alphabet[horizontal_index]}{numbers[vertical_index]}")
            self.extra_squares[i] = new_label_object

        for square, label in self.extra_squares.items() :
            if ((int(square / 8) + square % 8) % 2) == 0 : #determines white/black squares
                label.color("white", init = True)
            else :
                label.color("black", init = True)
            label.setText("")

    def display_on_square(self, id_str, square, board): #displays a particular graphic on a square on one of the boards.
        if id_str in self.piece_set : #piece display on square
            board[square].setPixmap(QtGui.QPixmap(self.display_keys.get(id_str)))
        elif not id_str : #clear display on square (e.g. id_str == None)
            board[square].setPixmap(QtGui.QPixmap(None))
        else : #other display on square
            board[square].setPixmap(QtGui.QPixmap(f"images/{id_str}.png"))
        board[square].setScaledContents(True)  # scales down the image to the label

    def display_set(self, input_set, display, board): #displays a whole set of squares on the board with a particular graphic
        for sq in input_set :
            self.display_on_square(display, sq, board)

    def bitscan(self, integer): #convert bitboard to set
        return_set = set()
        for i in range(64):
            comparator = 1 << i
            if integer & comparator:
                return_set.add(i)
        return frozenset(return_set)

    def reform_int(self, set_):  # convert set to bitboard
        return_integer = int()
        for bit in set_:
            return_integer += 2 ** bit
        return return_integer

    def display_board(self): #displays all of the sets in the game_state from the main game onto the main board with the piece graphics.
        self.game.update_game_dict()
        self.clear_board(self.squares)
        for piece in self.piece_set:
            self.display_set(self.game.str_to_set[piece], piece, self.squares)

    def algebraic_to_FEN(self, input_string):
        if 96 < ord(input_string[0]) < 105:  # if the first char is a-h, meaning algebraic notation.
            # convert to one-dimensional representation:
            final = int((ord(input_string[0]) - 97) + (8 - int(input_string[1])) * 8)
        elif 47 < ord(input_string[0]) < 58:  # if the first char is a number, means FEN.
            final = int(input_string)
        return final

    def test_submit(self):
        from_square = self.algebraic_to_FEN(self.input_position_input_from.text().lower())
        to_square = self.algebraic_to_FEN(self.input_position_input.text().lower())
        attempted_move = (from_square, to_square)
        self.make_move(attempted_move)
        return

    def test_display(self):
        self.clear_board(self.extra_squares)
        set_keys = {"total_occ" : self.game.total_occ, "white_occ" : self.game.white_occ,
                "black_occ" : self.game.black_occ, "R_occ" : self.game.R_occ,
                "r_occ" : self.game.r_occ, "B_occ" : self.game.B_occ, "b_occ" : self.game.b_occ,
                "N_occ" : self.game.N_occ, "n_occ" : self.game.n_occ, "K_occ" : self.game.K_occ,
                "k_occ" : self.game.k_occ, "Q_occ" : self.game.Q_occ, "q_occ" : self.game.q_occ,
                "P_occ" : self.game.P_occ, "p_occ" : self.game.p_occ, "to_move" : self.game.to_move,
                "white_castles" : self.game.white_castles, "black_castles" : self.game.black_castles}
        king_keys = {True : self.game.K_occ, False : self.game.k_occ}


        #viable bishop attacks = access bishop_att with bitboard of attack rays crossed with
        kinetic_keys = {"B" : lambda sq : self.engine.sv.bishop_att[sq][self.engine.sv.bishop_rays[sq] & self.reform_int(self.game.total_occ)] & ~self.reform_int(self.game.white_occ),
                        "R" : lambda sq : self.engine.sv.rook_att[sq][self.engine.sv.rook_rays[sq] & self.reform_int(self.game.total_occ)] & ~self.reform_int(self.game.white_occ),
                        "P" : lambda sq : (self.reform_int(self.engine.sv.wpawn_att[sq]) & self.reform_int(self.game.black_occ)) | (2**(sq - 8) & ~self.reform_int(self.game.total_occ)),
                        "N" : lambda sq : self.reform_int(self.engine.sv.knight_att[sq]) & ~self.reform_int(self.game.white_occ),
                        "K" : lambda sq : self.reform_int(self.engine.sv.king_att[sq]) & ~self.reform_int(self.game.white_occ),
                        "Q" : lambda sq : (self.engine.sv.bishop_att[sq][self.engine.sv.bishop_rays[sq] & self.reform_int(self.game.total_occ)] | self.engine.sv.rook_att[sq][self.engine.sv.rook_rays[sq] & self.reform_int(self.game.total_occ)]) & ~self.reform_int(self.game.white_occ),
                        "b": lambda sq: self.engine.sv.bishop_att[sq][self.engine.sv.bishop_rays[sq] & self.reform_int(self.game.total_occ)] & ~self.reform_int(self.game.black_occ),
                        "r": lambda sq: self.engine.sv.rook_att[sq][self.engine.sv.rook_rays[sq] & self.reform_int(self.game.total_occ)] & ~self.reform_int(self.game.black_occ),
                        "p": lambda sq: (self.reform_int(self.engine.sv.wpawn_att[sq]) & self.reform_int(self.game.white_occ)) | (2**(sq - 8) & ~self.reform_int(self.game.total_occ)),
                        "n": lambda sq: self.reform_int(self.engine.sv.knight_att[sq]) & ~self.reform_int(self.game.black_occ),
                        "k": lambda sq: self.reform_int(self.engine.sv.king_att[sq]) & ~self.reform_int(self.game.black_occ),
                        "q": lambda sq: (self.engine.sv.bishop_att[sq][self.engine.sv.bishop_rays[sq] & self.reform_int(self.game.total_occ)] | self.engine.sv.rook_att[sq][self.engine.sv.rook_rays[sq] & self.reform_int(self.game.total_occ)]) & ~self.reform_int(self.game.black_occ),
                        }

        #check set membership
        output = self.input_display_input.text()
        set_to_display = set_keys.get(output) #test if the output is a game-state set
        if not set_to_display : #if not, then it should be a square to test the relevant attack squares
            starting_square = self.algebraic_to_FEN(output)
            piece_str = self.game.sq_to_str[starting_square]
            #need to do different things with different piece strings, therefore need a lambda expression (accessed via kinetic keys) that does a unique thing depending on the piece.
            lambda_expression = kinetic_keys[piece_str]
            bitboard_to_display = lambda_expression(starting_square) #then, use the variable (starting square) as the lambda argument
            set_to_display = self.bitscan(bitboard_to_display)

        self.display_set(set_to_display, "red_x", self.extra_squares)

    def clear_board(self, board): #wipes the board of everything
        for sq in range(64) :
            self.display_on_square(None, sq, board)

    def make_move(self, move_tuple):
        self.engine.make_move(move_tuple)
        self.display_board()

    def new_game(self): #create new game
        self.game.new_game()
        self.display_board()

    def next_state(self): #go to the next game state
        self.game.next()
        self.display_board()

    def prev_state(self):
        self.game.previous()
        self.display_board()

    def last_state(self): #go to the last game state
        self.game.last()
        self.display_board()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_legals.setText(_translate("MainWindow", "legals"))
        self.button_submit.setText(_translate("MainWindow", "Submit"))
        self.label_piece_input.setText(_translate("MainWindow", "----: "))
        self.label_position_input_from.setText(_translate("MainWindow", "From: "))
        self.label_position_input.setText(_translate("MainWindow", "To: "))
        self.button_clear.setText(_translate("MainWindow", "Clear"))
        self.button_newgame.setText(_translate("MainWindow", "New Game"))
        self.button_next.setText(_translate("MainWindow", ">next"))
        self.button_prev.setText(_translate("MainWindow", "prev<"))
        self.button_last.setText(_translate("MainWindow", ">>last"))
        self.button_display.setText(_translate("MainWindow", "Display"))

        alphabet = ("A", "B", "C", "D", "E", "F", "G", "H")
        numbers = (8, 7, 6, 5, 4, 3, 2, 1)
        
        #file labels going horizontally ascending, so letters)
        for count, label_object in enumerate(self.file_labels) : 
            label_object.setText(_translate("MainWindow", f"{alphabet[count]}"))
        #rank labels (going vertically descending, so numbers)
        for count, label_object in enumerate(self.rank_labels):
            label_object.setText(_translate("MainWindow", f"{numbers[count]}"))
        
        #extra file labels (going horizontally ascending, so letters)
        for count, label_object in enumerate(self.extra_file_labels) :
            label_object.setText(_translate("MainWindow", f"{alphabet[count]}"))
        #extra rank labels (going vertically descending, so numbers)
        for count, label_object in enumerate(self.extra_rank_labels) :
            label_object.setText(_translate("MainWindow", f"{numbers[count]}"))
        #extra squares (going horizontally ascending % 8 and vertically descending // 8)
        for i in range(64) :
            label_object = self.extra_squares[i]
            horizontal_index = i % 8
            vertical_index = i // 8
            label_object.setText(_translate("MainWindow", str(i)))

