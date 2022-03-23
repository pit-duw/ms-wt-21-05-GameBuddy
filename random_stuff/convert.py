from hashlib import new
import chess
import random 
import pygame
import chess.engine
import os
import csv

def to_bitboard(csv_fen):
    board = chess.Board(fen = csv_fen)

    pw = ["0"]*64
    pb = ["0"]*64
    rw = ["0"]*64
    rb = ["0"]*64
    bw = ["0"]*64
    bb = ["0"]*64
    nw = ["0"]*64
    nb = ["0"]*64
    qw = ["0"]*64
    qb = ["0"]*64
    kw = ["0"]*64
    kb = ["0"]*64

    for i, piece in enumerate(board.__str__().replace(" ", "").replace("\n", "")):
        if piece == "P":
            pw[i] = "1"
        if piece == "p":
            pb[i] = "1"
        if piece == "R":
            rw[i] = "1"
        if piece == "r":
            rb[i] = "1"
        if piece == "B":
            bw[i] = "1"
        if piece == "b":
            bb[i] = "1"
        if piece == "N":
            nw[i] = "1"
        if piece == "n":
            nb[i] = "1"
        if piece == "Q":
            qw[i] = "1"
        if piece == "q":
            qb[i] = "1"
        if piece == "K":
            kw[i] = "1"
        if piece == "k":
            kb[i] = "1"
        
    add1 = str(int(board.turn))
    add2 = str(int(bool(board.castling_rights & chess.BB_H1)))
    add3 = str(int(bool(board.castling_rights & chess.BB_H8)))
    add4 = str(int(bool(board.castling_rights & chess.BB_A1)))
    add5 = str(int(bool(board.castling_rights & chess.BB_A8)))

    bitboard = "".join(pw + bb + rw + rb + bw + bb + nw + nb + qw + qb + kw + kb) + add1 + add2 + add3 + add4 + add5 
    return bitboard

def get_piece(board_string, move):
    board_list = board_string.split("\n")
    board_list = [bl.split() for bl in board_list]
    # print(move, int(move[1])-1, ord(move[0])-97, board_list[7-(int(move[1])-1)][(ord(move[0])-97)])
    return board_list[7-(int(move[1])-1)][(ord(move[0])-97)]

def get_index(piece):
    #print(piece)
    if piece == "P":
        return 0
    if piece == "p":
        return 1
    if piece == "R":
        return 2
    if piece == "r":
        return 3
    if piece == "B":
        return 4
    if piece == "b":
        return 5
    if piece == "N":
        return 6
    if piece == "n":
        return 7
    if piece == "Q":
        return 8
    if piece == "q":
        return 9
    if piece == "K":
        return 10
    if piece == "k":
        return 11


def to_input_layer(csv_fen):
    board = chess.Board(fen = csv_fen)
    
    numpieces12 = [0]*12
    nummotility12 = [0]*12
    numattack144 = [0]*144
    for i, piece in enumerate(board.__str__().replace(" ", "").replace("\n", "")):
        if piece == ".":
            continue
        numpieces12[get_index(piece)] +=1
            
    for move in board.legal_moves:
        start_piece = get_piece(board.__str__(), move.__str__()[0:2])
        target_piece = get_piece(board.__str__(), move.__str__()[2:4])
        start_index = get_index(start_piece)
        #print(start_piece, start_index, move, move.__str__()[0:2], move.__str__()[2:4])
        nummotility12[start_index] += 1
        #print(target_piece)
        if target_piece == ".":
            continue
        else:
            #print(start_index, target_piece, get_index(target_piece))
            numattack144[start_index*12 + get_index(target_piece)] += 1


    return [numpieces12 + nummotility12 + numattack144]
    

def new_score(sc):
    if sc[0] == "#":
        if sc[1] == "+":
            score = "1420"
        else:
            score = "-1420"
        return score
    else:
        return sc[:-1]
new_csv = []

i= 0
with open("../../Downloads/chessData.csv") as file:
    fen_list = file.readlines()[1:]
    for line in fen_list[:10000]:
        i+=1 
        fen, score = line.split(",")
        #score = score[:-1]
        bitboard = to_input_layer(fen)
        score = [(new_score(score))]
        #print(bitboard + score)
        if score[0] in ["1420", "-1420"]:
            continue
        else:
            new_csv.append(bitboard + score)
        if i%1000:
            print(i/1000, r"% done")

textfile = open("AI_data_10k_noCM2.csv", "w")

write = csv.writer(textfile)
write.writerows(new_csv)
textfile.close()