"""
The Calculation object is purely responsible for hypothesizing which moves are legal and in the future, the value of these moves.
Through its methods, it recursively alters the game. Every move forward means certain changes in the game
state that will lead to a new collection of legal moves that need to be determined. However, every move forward needs to be matched with
a move backwards and a rollback of the game state to where it was at the previous step in the iteration of moves.

"""

class Calculation() :
    def __init__(self, engine, game, depth_limit):
        self.engine = engine
        self.game = game
        self.legal_moves = {}

        self.setup_attributes()

        self.changes(0, depth_limit) #begin calculation

    def setup_attributes(self):
        self.to_move_sets = {
            True : [(self.game.B_occ, self.engine.B_changes, "B"), (self.game.K_occ, self.engine.K_changes, "K"), (self.game.R_occ, self.engine.R_changes, "R"),
                    (self.game.P_occ, self.engine.P_changes, "P"), (self.game.N_occ, self.engine.N_changes, "N"), (self.game.Q_occ, self.engine.Q_changes, "Q")],
            False : [(self.game.b_occ, self.engine.b_changes, "b"), (self.game.k_occ, self.engine.k_changes, "k"), (self.game.r_occ, self.engine.r_changes, "r"),
                     (self.game.p_occ, self.engine.p_changes, "p"), (self.game.n_occ, self.engine.n_changes, "n"), (self.game.q_occ, self.engine.q_changes, "q")]
        } #true = white; false = black

    def changes(self, current_depth, depth_limit): #generate all the changes and then create variations from each.
        pseudolegal_change_lists = {}
        for piece_set, function, piece_str in self.to_move_sets[self.game.to_move] : #for white or black to move, iterate over the sets for each piece type
            pseudolegal_change_lists[piece_str] = [] #set the dictionary to be able to accept change lists for the piece type
            for piece_position in piece_set : #iterate over the positions within each piece set
                changes = function(piece_position) #return the changes for the piece at each position moving to wherever it is pseudolegally able.
                pseudolegal_change_lists[piece_str].append(changes) #append the changes

        for piece_str, change_bundle in pseudolegal_change_lists.items() : #all changes for a piece type
            for change_package in change_bundle : #all changes for each piece of a type
                for change_list in change_package : #all changes for a particular move for a piece
                    self.variation(change_list, current_depth, depth_limit) #create variation for each change
        return

    def variation(self, change_list, current_depth, depth_limit): #this is where changes are applied and rolled back, and are checked for validity.
        self.change_maker(change_list, rollback = False) #apply all the changes to the game state
        if self.engine.in_check() : #if the king (of the side to move) is in check after all changes are applied, roll them back and return (it's an illegal move)
            self.change_maker(change_list, rollback = True)
            return False
        self.game.to_move = not self.game.to_move #flip whose turn it is now that the move is legitimate.
        if current_depth == 0 :
            self.legal_moves[change_list[0]] = change_list[1:] #legal_moves format = move tuple : changes
        if current_depth == depth_limit :
            self.change_maker(change_list, rollback = True)
            self.game.to_move = not self.game.to_move #flip back to whose move it was before
            return True
        else :
            self.setup_attributes()  #reset the data for self.changes to access the now current game state
            self.changes(current_depth + 1, depth_limit) #continue branching
            #when finished with the above branching (returns back to this call) :
            self.game.to_move = not self.game.to_move #flip turn
            self.change_maker(change_list, rollback = True)
            return True

    def change_maker(self, change_list, rollback):
        move_tuple = change_list[0] #always the case
        for function, set_ in change_list[1: ] : #Applies changes to the game state
            function(move_tuple, set_, rollback = rollback) #changes the game state at the set_ according to the move_tuple and the function logic