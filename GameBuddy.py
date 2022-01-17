#!/usr/bin/python3
"""
GameBuddy - Chess AI
"""

############ Imports #############

import chess
import random 
import pygame
import chess.engine
from sys import exit

############ Settings ############

player_white = "good_moves"
player_black = "good_moves"
n_best_moves = 1
search_depth = 1
stock_depth = 4

############ Setting up variables #############

col_names = ["a","b","c","d","e","f","g","h"]
row_names = ["1","2","3","4","5","6","7","8"]  
end_result_str = ['#-0', '#+0'] # Game end states
promo_names = ["q","r","n","b"] # Possible pieces for promotion
special_moves = {"forfeit":["gg", "ggwp"]}  # Dictionary of special moves: key = outcome, value = list of possible inputs
status = 0  # possible game states: 0 = game is ongoing, 1 = regular game over, 2 = error occured


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

pieces = {} # Dictionary: piece name -> image
pieces["P"] = pygame.image.load("pieces/Chess_plt60.png")
pieces["K"] = pygame.image.load("pieces/Chess_klt60.png")
pieces["Q"] = pygame.image.load("pieces/Chess_qlt60.png")
pieces["N"] = pygame.image.load("pieces/Chess_nlt60.png")
pieces["B"] = pygame.image.load("pieces/Chess_blt60.png")
pieces["R"] = pygame.image.load("pieces/Chess_rlt60.png")

pieces["p"] = pygame.image.load("pieces/Chess_pdt60.png")
pieces["k"] = pygame.image.load("pieces/Chess_kdt60.png")
pieces["q"] = pygame.image.load("pieces/Chess_qdt60.png")
pieces["n"] = pygame.image.load("pieces/Chess_ndt60.png")
pieces["b"] = pygame.image.load("pieces/Chess_bdt60.png")
pieces["r"] = pygame.image.load("pieces/Chess_rdt60.png")


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
        return make_good_move(board, 0)
    elif player == "stockfish":
        return make_stockfish_move(board, stock_depth)
    else:
        print("Invalid player.")
        return 2


def make_random_move(board):
    """Most stupid AI possible: picks a random move from all legal moves"""
    randoMove = str(random.choice([move for move in board.legal_moves]))
    board.push_san(randoMove)
    return 0
    

def get_board_rating(board):
    """Rate the current board state using the loaded chess engine. Score given from white players perspective."""
    info = engine.analyse(board, chess.engine.Limit(depth=0))
    return info["score"].white()


def has_potential(cp_best, cp_test):
    """Check whether a given move still has potential compared to the best move in the current search."""
    if cp_test is None: # Oppenent won't choose moves that cause them to be Mated soon.
        return False
    max_dist = min(abs(cp_best) * 0.1 + 10, 80)
    return abs(cp_best-cp_test) < max_dist


def get_best_moves(board):
    """Rate all possible moves from the current board state and return the best ones."""
    move_ratings = {}
    
    for move in board.legal_moves:
        board.push_san(move.__str__())
        move_ratings[move.__str__()] = get_board_rating(board)
        board.pop()

    pot_moves = dict(sorted(move_ratings.items(), key=lambda x:x[1], reverse=board.turn)[:n_best_moves])
    best_move, best_rating = sorted(move_ratings.items(), key=lambda x:x[1], reverse=board.turn)[0]

    if best_rating.score() is None:    # Immediately return upon finding a Mate
        return {best_move: best_rating}

    for move in pot_moves.copy():
        if not has_potential(best_rating.score(), pot_moves[move].score()):
            del pot_moves[move]
    
    return pot_moves


def make_stockfish_move(board, depth_stock):
    """Make a move using Stockfish with a given search depth."""
    result = engine.play(board, chess.engine.Limit(depth=depth_stock))
    print ("Stockfish: ", result.move )
    board.push_san(result.move.__str__())
    return 0 


def make_good_move(board, current_depth):
    """Make a move using our custom tree search with depth 0 Stockfish evaluation of the nodes."""
    potential_moves = get_best_moves(board)

    # Recursively search deeper
    if current_depth+1 < search_depth:
        for move in potential_moves:
            if not (potential_moves[move].__str__() in end_result_str): 
                board.push_san(move)
                potential_moves[move] = make_good_move(board, current_depth+1)
                board.pop()
    
    best_move = sorted(potential_moves.items(), key=lambda x:x[1], reverse=board.turn)[0]

    # If a move has been found successfully at the top layer of recursion, push that move and return status code 0 
    if current_depth == 0:
        result = engine.play(board, chess.engine.Limit(depth=10))
        print ('Move: ', best_move, result, potential_moves)
        board.push_san(best_move[0])
        return 0
    # Return the Best move's rating during recursion 
    return best_move[1]

    
def get_input(board):
    """Get the player input and handle invalid UCI codes."""
    input_complete = False
    square_start = ""
    square_end = ""
    while not input_complete:
        for event in pygame.event.get(): 
            # Check for quitting
            if event.type == pygame.QUIT:
                engine.quit()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                square_start = get_square(pygame.mouse.get_pos())
                highlight_moves(board, square_start)

            # Drag and Drop movement
            if event.type == pygame.MOUSEBUTTONUP:
                square_end = get_square(pygame.mouse.get_pos())
                
                # Switch to 2-click movement, if mouse button is released on same tile as it was pressed
                if square_start == square_end:
                    while not input_complete:
                        for event in pygame.event.get(): 
                            if event.type == pygame.MOUSEBUTTONUP:
                                square_end = get_square(pygame.mouse.get_pos())
                                input_complete = True
                else:
                    input_complete = True

                if square_start == square_end:
                    # print("Invalid Input!")
                    draw_board(board)
                    return get_input(board)

    # Generate the move string from the input and check whether it is valid
    inp = (square_start+square_end)#.lower()
    print(inp)
    if len(inp) == 4:
        if inp[0] in col_names and inp[2] in col_names and inp[1] in row_names and inp[3] in row_names:
            draw_board(board)
            return inp

    # Repeat if the input was invalid
    print("Invalid Input!")
    draw_board(board)
    return get_input(board)
    
    
def make_player_move(board):
    """Get the players move input and check whether it is a valid move."""
    player_move = get_input(board)
    if player_move in special_moves["forfeit"]:
        return 1
    if chess.Move.from_uci(player_move) in board.legal_moves:
        board.push_san(player_move)
        return 0
    # Handle promotion, currently queen is automatically chosen
    elif chess.Move.from_uci(player_move+"q") in board.legal_moves:
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
            if not piece==".":
                screen.blit(pieces[piece], [50+20+100*j, 50+20+100*i])


def draw_board(board):
    """Draw the chess board + Pieces"""
    surf_w = pygame.Surface((100,100))
    surf_w.fill((225,225,225))
    surf_b = pygame.Surface((800,800))
    surf_b.fill((40,40,40))
    screen.blit(surf_b, [50,50])
    for i in range(8):
        for j in range(8):
            if (i+j) % 2 == 0:
                screen.blit(surf_w, [i*100+50,j*100+50])
        textsurface = myfont.render(col_names[i].upper(), False, (255, 255, 255))
        screen.blit(textsurface, (50+38 + i * 100, 10))
        screen.blit(textsurface, (50+38 + i * 100, 850+10))
        textsurface = myfont.render(row_names[-i-1], False, (255, 255, 255))
        screen.blit(textsurface, (15, 50+33 + i * 100))
        screen.blit(textsurface, (850+15, 50+33 + i * 100))

    draw_pieces(board.__str__())
    # Update the screen
    pygame.display.flip()


def highlight_moves(board, square_start):
    """Draw green highlights for all legal moves starting from the given square."""
    for move in board.legal_moves:
        if square_start == move.__str__()[:2]:
            target = move.__str__()[2:]
            # Get the square's position on the screen 
            pos = [(ord(target[0])-96)*100-50, (9-int(target[1]))*100-50]   # ord(char) = ascii code of char 
            # Create a surface with alpha channel for colors
            alpha_surf = pygame.Surface((100,100), pygame.SRCALPHA)
            if contains_piece(board, target):
                # Fill the target sqaure green
                alpha_surf.fill((25,150,25,150))
                # Create a circle shape and remove it from the target square's green highlight
                circle_surf = pygame.Surface((100,100), pygame.SRCALPHA)
                pygame.draw.circle(circle_surf, (0,0,0,255), (50, 50), 54)
                alpha_surf.blit(circle_surf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            else:
                # Draw a green circle on free squares
                pygame.draw.circle(alpha_surf, (25,150,25,150), (50,50), 20)
            screen.blit(alpha_surf, pos)
    
    # Mark the current selection
    pos = [(ord(square_start[0])-96)*100-50, (9-int(square_start[1]))*100-50]   # ord(char) = ascii code of char 
    # Create a surface with alpha channel for colors
    alpha_surf = pygame.Surface((100,100), pygame.SRCALPHA)
    # Fill the target sqaure green
    alpha_surf.fill((25,150,25,150))
    screen.blit(alpha_surf, pos)
    draw_pieces(board.__str__())
    pygame.display.flip()


def contains_piece(board, square):
    board_list = board.__str__().split("\n")
    board_list = [bl.split() for bl in board_list]
    return not board_list[(8-int(square[1]))][(ord(square[0])-97)] == "."


############# Setup ###############

board = chess.Board()
draw_board(board)


############# Game loop #############

while not (board.is_game_over() or status):
    status = make_move(board)
    draw_board(board)

    
############### Handle game outcome #############

if board.is_stalemate() or board.is_insufficient_material():
    print("Draw!")
elif board.is_checkmate() or status == 1:
    if (board.turn == chess.BLACK):
        print("WHITE won!")
    else:
        print("BLACK won!")
elif status == 2:
    print("An error occured. Game stopped.")

while True:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            engine.quit()
            pygame.quit()
            exit()