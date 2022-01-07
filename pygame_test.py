"""
GameBuddy - Chess AI
"""

############ Imports #############

import chess
import random 
import pygame
import chess.engine

############ Settings ############

player_white = "good_moves"
player_black = "good_moves"



############ Setting up variables #############

col_names = ["a","b","c","d","e","f","g","h"]
row_names = ["1","2","3","4","5","6","7","8"]
promo_names = ["q","r","n","b"] # possible pieces for promotion
special_moves = {"forfeit":["gg", "ggwp"]}  # dictionary of special moves: key = outcome, value = list of possible inputs
count = 0   # counter for number of turns played
status = 0  # possible game states: 0 = game is ongoing, 1 = player forfeited the match, 2 = error occured

n_best_moves = 4
search_depth = 4


########### Setting up pygame #############

pygame.init()
size = width, height = 900, 900
black = 70, 70, 70
screen = pygame.display.set_mode(size)
screen.fill(black)
pygame.font.init()
myfont = pygame.font.SysFont('Arial', 34)
engine = chess.engine.SimpleEngine.popen_uci("stockfish_14.1_linux_x64/stockfish_14.1_linux_x64")



########### Loading piece images #############

pw = pygame.image.load("pieces/Chess_plt60.png")
pwrect = pw.get_rect()
kw = pygame.image.load("pieces/Chess_klt60.png")
kwrect = kw.get_rect()
qw = pygame.image.load("pieces/Chess_qlt60.png")
qwrect = qw.get_rect()
nw = pygame.image.load("pieces/Chess_nlt60.png")
nwrect = nw.get_rect()
bw = pygame.image.load("pieces/Chess_blt60.png")
bwrect = bw.get_rect()
rw = pygame.image.load("pieces/Chess_rlt60.png")
rwrect = rw.get_rect()

pb = pygame.image.load("pieces/Chess_pdt60.png")
pbrect = pb.get_rect()
kb = pygame.image.load("pieces/Chess_kdt60.png")
kbrect = kb.get_rect()
qb = pygame.image.load("pieces/Chess_qdt60.png")
qbrect = qb.get_rect()
nb = pygame.image.load("pieces/Chess_ndt60.png")
nbrect = nb.get_rect()
bb = pygame.image.load("pieces/Chess_bdt60.png")
bbrect = bb.get_rect()
rb = pygame.image.load("pieces/Chess_rdt60.png")
rbrect = rb.get_rect()



########### Functions ###############

def get_square(position):
    """Get the chess board square from the mouse coordinates"""
    x = position[0]
    y = position[1]
    if x <50 or x>850 or y >850 or y <50:
        return "inv"
    x = col_names[int((x-50) // 100)]
    y = row_names[-int((y-50) // 100)-1]
    
    return x+y

def make_move(board):
    """Wrapper for make_X_move, where X can be player or some AI"""
    if board.turn == chess.WHITE:
        player = player_white
    else:
        player = player_black
    if player == "human":
        return make_player_move(board)
    elif player == "random":
        return make_random_move(board)
    elif player == "good_moves":
        return make_good_move(board, 0, n_best_moves, board.turn)
    else:
        print("Invalid player.")
        return 2

def make_random_move(board):
    """Most stupid AI possible: picks a random move from all legal moves"""
    randoMove = str(random.choice
                    ([move for move in board.legal_moves]))
    board.push_san(randoMove)
    return 0
    

def get_board_rating(board, color):
    info = engine.analyse(board, chess.engine.Limit(depth=0))
    if color == chess.WHITE:
        return info["score"].white()
    else:
        return info["score"].black()

def make_good_move(board, current_depth, n_best_movesLocal, color):
    move_ratings = {}
    
    for move in board.legal_moves:
        board.push_san(move.__str__())
        move_ratings[move.__str__()] = get_board_rating(board, color)
        board.pop()

    max_moves = min(n_best_movesLocal, len(move_ratings))

    potential_moves = sorted(move_ratings.items(), key=lambda x:x[1], reverse=bool((current_depth)%2))[:max_moves]
    
    if current_depth+1 < search_depth:
        for move in potential_moves:
            board.push_san(move[0])
            move_ratings[move[0]] = make_good_move(board, current_depth+1, max(1, n_best_movesLocal-1), color)
            board.pop()
    #print(current_depth, move_ratings)
    best_move = sorted(move_ratings.items(), key=lambda x:x[1], reverse=bool((current_depth)%2))[-1]
    if current_depth == 0:
        print(best_move)
        result = engine.play(board, chess.engine.Limit(time=0.1))
        print (result)
        board.push_san(best_move[0])
        return 0
    return best_move[1]
    
    
def get_input():
    """Get the player input and handle invalid UCI codes."""
    input_complete = False
    while not input_complete:
        for event in pygame.event.get(): 
            if event.type == pygame.MOUSEBUTTONDOWN:
                square_down = get_square(pygame.mouse.get_pos())
                print(square_down)
                #highligt_possible_moves(square_down)
            if event.type == pygame.MOUSEBUTTONUP:
                square_up = get_square(pygame.mouse.get_pos())
                print(square_up)
                input_complete = True

    if square_down == square_up:
        input_complete = False
        print("Invalid Input!")
        return get_input()

    inp = (square_down+square_up).lower()
    print(inp)
    
    if len(inp) == 4:
        if inp[0] in col_names and inp[2] in col_names and inp[1] in row_names and inp[3] in row_names:
            return inp
    elif len(inp) == 5:
        if inp[0] in col_names and inp[2] in col_names and inp[1] in row_names and inp[3] in row_names and inp[4] in promo_names:
            return inp
    if inp in special_moves["forfeit"]:
        return inp
    print("Invalid Input!")
    return get_input()
    
    
def make_player_move(board):
    """Perform a player turn"""
    player_move = get_input()
    if player_move in special_moves["forfeit"]:
        return 1
    if chess.Move.from_uci(player_move) in board.legal_moves:
        board.push_san(player_move)
        return 0
    if chess.Move.from_uci(player_move+"q") in board.legal_moves:
        board.push_san(player_move+"q")
        return 0
    else: 
        print("Illegal Move!")
        return make_player_move(board)

def draw_pieces(board_string):
    """Take the current board state and draw all pieces accondingly"""
    board_list = board_string.split("\n")
    board_list = [bl.split() for bl in board_list]
    for i, bl in enumerate(board_list):
        for j, piece in enumerate(bl):
            if piece==".":
                pass
            elif piece=="p":
                screen.blit(pb, [50+20+100*j, 50+20+100*i])
            elif piece=="r":
                screen.blit(rb, [50+20+100*j, 50+20+100*i])
            elif piece=="q":
                screen.blit(qb, [50+20+100*j, 50+20+100*i])
            elif piece=="b":
                screen.blit(bb, [50+20+100*j, 50+20+100*i])
            elif piece=="k":
                screen.blit(kb, [50+20+100*j, 50+20+100*i])
            elif piece=="n":
                screen.blit(nb, [50+20+100*j, 50+20+100*i])
            elif piece=="P":
                screen.blit(pw, [50+20+100*j, 50+20+100*i])
            elif piece=="R":
                screen.blit(rw, [50+20+100*j, 50+20+100*i])
            elif piece=="Q":
                screen.blit(qw, [50+20+100*j, 50+20+100*i])
            elif piece=="B":
                screen.blit(bw, [50+20+100*j, 50+20+100*i])
            elif piece=="K":
                screen.blit(kw, [50+20+100*j, 50+20+100*i])
            elif piece=="N":
                screen.blit(nw, [50+20+100*j, 50+20+100*i])

def draw_board():
    """Draw the chess board"""
    surf_w = pygame.Surface((100,100))
    surf_w.fill((225,225,225))
    surf_b = pygame.Surface((800,800))
    surf_b.fill((40,40,40))
    screen.blit(surf_b, [50,50])
    for i in range(8):
        for j in range(8):
            if (i+j) % 2 == 0:
                screen.blit(surf_w, [i*100+50,j*100+50])
        textsurface = myfont.render(col_names[i], False, (255, 255, 255))
        screen.blit(textsurface, (50+38 + i * 100, 10))
        screen.blit(textsurface, (50+38 + i * 100, 850+10))
        textsurface = myfont.render(row_names[-i-1], False, (255, 255, 255))
        screen.blit(textsurface, (15, 50+33 + i * 100))
        screen.blit(textsurface, (850+15, 50+33 + i * 100))
        


############# Setup ###############

board = chess.Board()
draw_board()
draw_pieces(board.__str__())
pygame.display.flip()



############# Game loop #############

while not (board.is_game_over() or status):
    status = make_move(board)
    draw_board()
    draw_pieces(board.__str__())
    pygame.display.flip()

    

############### Handle game outcome #############

if board.is_stalemate() or board.is_insufficient_material():
    print("Draw after " + str(count) + " turns!")
elif board.is_checkmate() or status == 1:
    if (board.turn == chess.BLACK):
        print("WHITE won!")
    else:
        print("BLACK won!")
elif status == 2:
    print("An error occured. Game stopped.")