from django.template import Context, loader
from django.http import HttpResponse
from django.core.cache import cache
from random import choice

class Computer:
    MAX = 'MAX'
    MIN = 'MIN'
    
    def make_move(self, board_instance):
        move_pos, result = self.max_move(board_instance)
        board_instance.set_mark(move_pos, Board.COMPUTER)

    def max_move(self, board_instance):
        best_result = None
        best_move = None
        
        for m in board_instance.get_open_spaces():
            board_instance.set_mark(m, Board.COMPUTER)
                
            if board_instance.is_game_over():
                result = self.get_result(board_instance)
            else:
                move_pos, result = self.min_move(board_instance)

            board_instance.revert_last_move()
            
            if best_result == None or result > best_result:
                best_result = result
                best_move = m

        return best_move, best_result
        
    def min_move(self, board_instance):
        best_result = None
        best_move = None
        
        for m in board_instance.get_open_spaces():
            board_instance.set_mark(m, Board.USER)
                
            if board_instance.is_game_over():
                result = self.get_result(board_instance)
            else:
                move_pos, result = self.max_move(board_instance)

            board_instance.revert_last_move()
            
            if best_result == None or result < best_result:
                best_result = result
                best_move = m

        return best_move, best_result        
        
    def get_result(self, board_instance):
        if board_instance.is_game_over():
            if board_instance.winner == Board.COMPUTER:
                return 1
            elif board_instance.winner == Board.USER:
                return -1
        
        return 0
        
class Board:
    EMPTY = 'not-selected'
    USER = 'user-selected'
    COMPUTER = 'computer-selected'
    
    EMPTY_BOARD = [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY]    

    def __init__(self, board = None):
        if board:
            self.board = board
        else:
            self.board = Board.EMPTY_BOARD
            
        self.moves = []
        self.winner = None

    def set_mark(self, position, user):
        self.board[position] = user
        self.moves.append(position)
        
        b = self.board
        
        if (b[0] == b[1] == b[2] and not b[0] == self.EMPTY):
            self.winner = b[0]
        elif (b[3] == b[4] == b[5] and not b[3] == self.EMPTY):
            self.winner = b[3]
        elif (b[6] == b[7] == b[8] and not b[6] == self.EMPTY):
            self.winner = b[6]            
        elif (b[0] == b[3] == b[6] and not b[0] == self.EMPTY):
             self.winner = b[0]            
        elif (b[1] == b[4] == b[7] and not b[1] == self.EMPTY):
             self.winner = b[1]            
        elif (b[2] == b[5] == b[8] and not b[2] == self.EMPTY):
             self.winner = b[2]            
        elif (b[0] == b[4] == b[8] and not b[0] == self.EMPTY):
             self.winner = b[0]            
        elif (b[2] == b[4] == b[6] and not b[2] == self.EMPTY):
             self.winner = b[2]                        
        
    def revert_last_move(self):
        self.board[self.moves.pop()] = Board.EMPTY
        self.winner = None
    
    def get_open_spaces(self):
        open_spaces = []
        
        for i in range(9):
            if self.board[i] == Board.EMPTY:
                open_spaces.append(i)
        
        return open_spaces
        
    def is_game_over(self):
        if self.winner:
            return True
        else:
            for i in range(9):
                if self.board[i] == Board.EMPTY:
                    return False
        
        return True     

def start(request):
    computer = Computer()
    selected_cell = request.GET.get('selected_cell', None)
    current_board = cache.get('board')
    
    if current_board and selected_cell:
        board_instance = Board(current_board)
    else:
        board_instance = Board()        

    if request.method == 'GET' and selected_cell:
        # ensure the value is not already set (i.e. refresh button was pressed
        # with the GET value in the URL)        
        if not board_instance.board[int(selected_cell)] in (Board.USER, Board.COMPUTER):
            #update the current board with the user's move and a follow-up move from the computer
            board_instance.set_mark(int(selected_cell), Board.USER)
            computer.make_move(board_instance)
      
    # store the board in cache
    cache.set('board', board_instance.board)
    
    t = loader.get_template('home.html')
    c = Context({
        'board': board_instance.board,
    })
    
    return HttpResponse(t.render(c))