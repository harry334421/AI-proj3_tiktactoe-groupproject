import math
import copy
import random
import time
import numpy as np
from multiprocessing import Manager, Queue, Pool, cpu_count
TIMEOUT=30
cpu=cpu_count()-1

def check_winner(board, target):
    rows = len(board)
    cols = len(board[0])
    # Check rows
    for row in range(rows):
        for col in range(cols - target + 1):
            window = board[row][col:col + target]
            if all(val == 1 for val in window):
                return 1
            elif all(val == -1 for val in window):
                return -1
    # Check columns
    for row in range(rows - target + 1):
        for col in range(cols):
            window = [board[row + i][col] for i in range(target)]
            if all(val == 1 for val in window):
                return 1
            elif all(val == -1 for val in window):
                return -1
    # Check diagonals (top-left to bottom-right)
    for row in range(rows - target + 1):
        for col in range(cols - target + 1):
            window = [board[row + i][col + i] for i in range(target)]
            if all(val == 1 for val in window):
                return 1
            elif all(val == -1 for val in window):
                return -1
    # Check diagonals (top-right to bottom-left)
    for row in range(rows - target + 1):
        for col in range(target - 1, cols):
            window = [board[row + i][col - i] for i in range(target)]
            if all(val == 1 for val in window):
                return 1
            elif all(val == -1 for val in window):
                return -1
    return 0

def is_full(board):
    for row in board:
        if 0 in row:
            return False
    return True

#Check Immediate Winning Move
def is_winning_move(board, target, row, col):
    player = board[row][col]
    #Check Winner
    if check_winner(board, target)==player:
        return True
    return False

#Check Winning Moves in Two Steps using Known Patterns
def intermediate_winning_pattern(board, target, row, col, player):
    player=1 if player else -1
    #Board Conversion
    board=np.array(board)
    #results holder
    immediate_winning_move={1:[], 2:[], 3:[], 4:[]}
    #One T-1 Sequence Two-Way Unblocked
    count_2w_tm1, count_2w_tm1_seq=find_2way_unblocked_sequences(board, target, target-1, player, max_gap=0)
    for seq in count_2w_tm1_seq:
        if (row, col) in seq:
            immediate_winning_move[1].append((row,col))
            break
    #Two T-1 Sequence One-Way Unblocked
    count_1w_tm1, count_1w_tm1_seq=find_1way_unblocked_sequences(board, target, target-1, player)
    counter=0
    for seq in count_1w_tm1_seq:
        if (row, col) in seq: counter+=1
        if counter==2:
            immediate_winning_move[1].append((row,col))
    #One T-1 Sequence One-Way Blocked and one T-2 Sequence Two-way Unblocked
    count_2w_tm2, count_2w_tm2_seq=find_1way_unblocked_sequences(board, target, target-1, player)
    for seq1 in count_1w_tm1_seq:
        if (row, col) in seq:
            for seq2 in count_2w_tm2_seq:
                if (row, col) in seq2:
                    immediate_winning_move[2].append((row,col))
    #Two T-2 Sequence Two-Way Unblocked
    counter=0
    for seq in count_2w_tm2_seq:
        if (row, col) in seq: counter+=1
        if counter==2:
            immediate_winning_move[3].append((row,col))
    #One T-2 Sequence Two-Way Unblocked and One T-2 Sequence One-Way Unblocked
    count_1w_tm2, count_1w_tm2_seq=find_1way_unblocked_sequences(board, target, target-2, player)
    for seq in count_2w_tm2_seq:
        if (row, col) in seq:
            for seq2 in count_1w_tm2_seq:
                    if (row, col) in seq2:
                        immediate_winning_move[4].append((row,col))
    return immediate_winning_move

##Ancillary Function to Check Unblocked Sequences
def find_2way_unblocked_sequences(board, target, required_length, player, max_gap=1):
    #Window Length
    window_lengths=[]
    for gap in range(max_gap+1):
        window_lengths.append(min(max(required_length+gap+2, target),len(board)))
    window_lengths=list(set(window_lengths))
    #Player
    unblocked_count=0
    unblocked_list=[]
    #Check Row
    for row in range(len(board)):
        array=board[row]
        for window_length in window_lengths:
            for idx1 in range(len(array)-window_length+1):
                window=array[idx1:idx1+window_length]
                if all(val != -player for val in window) and sum(val == player for val in window)==required_length:
                    min_idx=list(window).index(player)
                    max_idx=len(window) -1 - list(window)[::-1].index(player)
                    gaps=max_idx-min_idx+1-required_length
                    if gaps<=1 and min_idx!=0 and max_idx!=len(window)-1:
                        seq=[]
                        for idx2, role in enumerate(window):
                            if role==player:
                                seq.append((row, idx1+idx2))
                        if seq not in unblocked_list:
                            unblocked_list.append(seq)
                            unblocked_count+=1
    #Check Column
    for col in range(len(board)):
        array=board.transpose()[col]
        for window_length in window_lengths:
            for idx1 in range(len(array)-window_length+1):
                window=array[idx1:idx1+window_length]
                if all(val != -player for val in window) and sum(val == player for val in window)==required_length:
                    min_idx=list(window).index(player)
                    max_idx=len(window) -1 - list(window)[::-1].index(player)
                    gaps=max_idx-min_idx+1-required_length
                    if gaps<=1 and min_idx!=0 and max_idx!=len(window)-1:
                        seq=[]
                        for idx2, role in enumerate(window):
                            if role==player:
                                seq.append((idx1+idx2, col))
                        if seq not in unblocked_list:
                            unblocked_list.append(seq)
                            unblocked_count+=1
    #Diagonal
    for idx0 in range(len(board)):
        for dr in [-1,1]:
            array=board.diagonal(idx0*dr)
            for window_length in window_lengths:
                if len(array)>=window_length:
                    for idx1 in range(len(array)-window_length+1):
                        window=array[idx1:idx1+window_length]
                        if all(val != -player for val in window) and sum(val == player for val in window)==required_length:
                            min_idx=list(window).index(player)
                            max_idx=len(window) -1 - list(window)[::-1].index(player)
                            gaps=max_idx-min_idx+1-required_length
                            if gaps<=1 and min_idx!=0 and max_idx!=len(window)-1:
                                seq=[]
                                for idx2, role in enumerate(window):
                                    if role==player and dr==1:
                                        seq.append((idx1+idx2, idx0+idx1+idx2))
                                    elif role==player and dr==-1:
                                        seq.append((idx0+idx1+idx2, idx1+idx2))
                                if seq not in unblocked_list:
                                    unblocked_list.append(seq)
                                    unblocked_count+=1
    #Anti-Diagonal
    for idx0 in range(len(board)):
        for dr in [-1,1]:
            array=np.fliplr(board).diagonal(idx0*dr)
            for window_length in window_lengths:
                if len(array)>=window_length:
                    for idx1 in range(len(array)-window_length+1):
                        window=array[idx1:idx1+window_length]
                        if all(val != -player for val in window) and sum(val == player for val in window)==required_length:
                            min_idx=list(window).index(player)
                            max_idx=len(window) -1 - required_length
                            gaps=max_idx-min_idx+1-sum(window)
                            if gaps<=1 and min_idx!=0 and max_idx!=len(window)-1:
                                seq=[]
                                for idx2, role in enumerate(window):
                                    if role==player and dr==1:
                                        seq.append((len(board)-1-(idx1+idx2), idx0+idx1+idx2))
                                    elif role==player and dr==-1:
                                        seq.append((len(board)-1-(idx0+idx1+idx2), idx1+idx2))
                                if seq not in unblocked_list:
                                    unblocked_list.append(seq)
                                    unblocked_count+=1
    return unblocked_count, unblocked_list

def find_1way_unblocked_sequences(board, target, required_length, player, max_gap=1):
    #Window Length
    window_lengths=[]
    for gap in range(max_gap+1):
        window_lengths.append(min(max(required_length+gap+2, target),len(board)))
    window_lengths=list(set(window_lengths))
    #Player
    unblocked_count=0
    unblocked_list=[]
    #Check Row
    for row in range(len(board)):
        #print(f"Row: {row}")
        array=board[row]
        for window_length in window_lengths:
            for idx1 in range(len(array)-window_length+2):
                window=array[idx1:idx1+window_length]
                #print(window)
                if (sum(val == -player for val in window)==1 and (window[0]==-player or window[-1]==-player)) and sum(val == player for val in window)==required_length:
                    flag_idx=list(window).index(-player)
                    min_idx=list(window).index(player)
                    max_idx=len(window) -1 - list(window)[::-1].index(player)
                    gaps=max_idx-min_idx+1-required_length
                    #print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                    if gaps<=1 and (min_idx==flag_idx+1 or max_idx==flag_idx-1):
                        seq=[]
                        for idx2, role in enumerate(window):
                            if role==player:
                                seq.append((row, idx1+idx2))
                        if seq not in unblocked_list:
                            unblocked_list.append(seq)
                            unblocked_count+=1
                elif (sum(val == -player for val in window)==0 and (idx1==0 or idx1+window_length==len(board))) and sum(val == player for val in window)==required_length:
                    min_idx=list(window).index(player)
                    max_idx=len(window) -1 - list(window)[::-1].index(player)
                    gaps=max_idx-min_idx+1-required_length
                    #print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                    if gaps<=1 and (min_idx==0 or max_idx==len(window)-1):
                        seq=[]
                        for idx2, role in enumerate(window):
                            if role==player:
                                seq.append((row, idx1+idx2))
                        if seq not in unblocked_list:
                            unblocked_list.append(seq)
                            unblocked_count+=1
    #Check Column
    for col in range(len(board)):
        array=board.transpose()[col]
        for window_length in window_lengths:
            for idx1 in range(len(array)-window_length+2):
                window=array[idx1:idx1+window_length]
                if (sum(val == -player for val in window)==1 and (window[0]==-player or window[-1]==-player)) and sum(val == player for val in window)==required_length:
                    flag_idx=list(window).index(-player)
                    min_idx=list(window).index(player)
                    max_idx=len(window) -1 - list(window)[::-1].index(player)
                    gaps=max_idx-min_idx+1-required_length
                    #print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                    if gaps<=1 and (min_idx==flag_idx+1 or max_idx==flag_idx-1):
                        seq=[]
                        for idx2, role in enumerate(window):
                            if role==player:
                                seq.append((row, idx1+idx2))
                        if seq not in unblocked_list:
                            unblocked_list.append(seq)
                            unblocked_count+=1
                elif (sum(val == -player for val in window)==0 and (idx1==0 or idx1+window_length==len(board))) and sum(val == player for val in window)==required_length:
                    min_idx=list(window).index(player)
                    max_idx=len(window) -1 - list(window)[::-1].index(player)
                    gaps=max_idx-min_idx+1-required_length
                    #print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                    if gaps<=1 and (min_idx==0 or max_idx==len(window)-1):
                        seq=[]
                        for idx2, role in enumerate(window):
                            if role==player:
                                seq.append((idx1+idx2, col))
                        if seq not in unblocked_list:
                            unblocked_list.append(seq)
                            unblocked_count+=1
    #Diagonal
    for idx0 in range(len(board)):
        for dr in [-1,1]:
            array=board.diagonal(idx0*dr)
            for window_length in window_lengths:
                if len(array)>=window_length:
                    for idx1 in range(len(array)-window_length+2):
                        window=array[idx1:idx1+window_length]
                        if (sum(val == -player for val in window)==1 and (window[0]==-player or window[-1]==-player)) and sum(val == player for val in window)==required_length:
                            flag_idx=list(window).index(-player)
                            min_idx=list(window).index(player)
                            max_idx=len(window) -1 - list(window)[::-1].index(player)
                            gaps=max_idx-min_idx+1-required_length
                            #print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                            if gaps<=1 and (min_idx==flag_idx+1 or max_idx==flag_idx-1):
                                seq=[]
                                for idx2, role in enumerate(window):
                                    if role==player and dr==1:
                                        seq.append((idx1+idx2, idx0+idx1+idx2))
                                    elif role==player and dr==-1:
                                        seq.append((idx0+idx1+idx2, idx1+idx2))
                                if seq not in unblocked_list:
                                    unblocked_list.append(seq)
                                    unblocked_count+=1
                        elif (sum(val == -player for val in window)==0 and (idx1==0 or idx1+window_length==len(board))) and sum(val == player for val in window)==required_length:
                            min_idx=list(window).index(player)
                            max_idx=len(window) -1 - list(window)[::-1].index(player)
                            gaps=max_idx-min_idx+1-required_length
                            #print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                            if gaps<=1 and (min_idx==0 or max_idx==len(window)-1):
                                seq=[]
                                for idx2, role in enumerate(window):
                                    if role==player and dr==1:
                                        seq.append((idx1+idx2, idx0+idx1+idx2))
                                    elif role==player and dr==-1:
                                        seq.append((idx0+idx1+idx2, idx1+idx2))
                                if seq not in unblocked_list:
                                    unblocked_list.append(seq)
                                    unblocked_count+=1
    #Anti-Diagonal
    for idx0 in range(len(board)):
        for dr in [-1,1]:
            array=np.fliplr(board).diagonal(idx0*dr)
            for window_length in window_lengths:
                if len(array)>=window_length:
                    for idx1 in range(len(array)-window_length+1):
                        window=array[idx1:idx1+window_length]
                        if (sum(val == -player for val in window)==1 and (window[0]==-player or window[-1]==-player)) and sum(val == player for val in window)==required_length:
                            flag_idx=list(window).index(-player)
                            min_idx=list(window).index(player)
                            max_idx=len(window) -1 - list(window)[::-1].index(player)
                            gaps=max_idx-min_idx+1-required_length
                            #print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                            if gaps<=1 and (min_idx==flag_idx+1 or max_idx==flag_idx-1):
                                seq=[]
                                for idx2, role in enumerate(window):
                                    if role==player and dr==1:
                                        seq.append((len(board)-1-(idx1+idx2), idx0+idx1+idx2))
                                    elif role==player and dr==-1:
                                        seq.append((len(board)-1-(idx0+idx1+idx2), idx1+idx2))
                                if seq not in unblocked_list:
                                    unblocked_list.append(seq)
                                    unblocked_count+=1
                        elif (sum(val == -player for val in window)==0 and (idx1==0 or idx1+window_length==len(board))) and sum(val == player for val in window)==required_length:
                            min_idx=list(window).index(player)
                            max_idx=len(window) -1 - list(window)[::-1].index(player)
                            gaps=max_idx-min_idx+1-required_length
                            #print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                            if gaps<=1 and (min_idx==0 or max_idx==len(window)-1):
                                seq=[]
                                for idx2, role in enumerate(window):
                                    if role==player and dr==1:
                                        seq.append((len(board)-1-(idx1+idx2), idx0+idx1+idx2))
                                    elif role==player and dr==-1:
                                        seq.append((len(board)-1-(idx0+idx1+idx2), idx1+idx2))
                                if seq not in unblocked_list:
                                    unblocked_list.append(seq)
                                    unblocked_count+=1
    return unblocked_count, unblocked_list


#Board Evaluator Functions
def evaluate1(board, target):
    score = 0
    base = target**2+1
    # Score rows
    for row in range(len(board)):
        for col in range(len(board[row]) - target + 1):
            window = board[row][col:col + target]
            if all(val != -1 for val in window):
                score += base**(sum([val == 1 for val in window])-1)
            if all(val != 1 for val in window):
                score -= base**(sum([val == -1 for val in window])-1)
    # Score columns
    for row in range(len(board) - target + 1):
        for col in range(len(board[row])):
            window = [board[row + i][col] for i in range(target)]
            if all(val != -1 for val in window):
                score += base**(sum([val == 1 for val in window])-1)
            if all(val != 1 for val in window):
                score -= base**(sum([val == -1 for val in window])-1)
    # Score diagonals (top-left to bottom-right)
    for row in range(len(board) - target + 1):
        for col in range(len(board[row]) - target + 1):
            window = [board[row + i][col + i] for i in range(target)]
            if all(val != -1 for val in window):
                score += base**(sum([val == 1 for val in window])-1)
            if all(val != 1 for val in window):
                score -= base**(sum([val == -1 for val in window])-1)
    # Score diagonals (top-right to bottom-left)
    for row in range(len(board) - target + 1):
        for col in range(target - 1, len(board[row])):
            window = [board[row + i][col - i] for i in range(target)]
            if all(val != -1 for val in window):
                score += base**(sum([val == 1 for val in window])-1)
            if all(val != 1 for val in window):
                score -= base**(sum([val == -1 for val in window])-1)
    return score

def evaluate2(board, target):
    score = 0
    base = target**2+1
    # Score rows
    for row in range(len(board)):
        for col in range(len(board[row]) - target + 1):
            window = board[row][col:col + target]
            if all(val != -1 for val in window):
                score += 1
            if all(val != 1 for val in window):
                score -= 1
    # Score columns
    for row in range(len(board) - target + 1):
        for col in range(len(board[row])):
            window = [board[row + i][col] for i in range(target)]
            if all(val != -1 for val in window):
                score += 1
            if all(val != 1 for val in window):
                score -= 1
    # Score diagonals (top-left to bottom-right)
    for row in range(len(board) - target + 1):
        for col in range(len(board[row]) - target + 1):
            window = [board[row + i][col + i] for i in range(target)]
            if all(val != -1 for val in window):
                score += 1
            if all(val != 1 for val in window):
                score -= 1
    # Score diagonals (top-right to bottom-left)
    for row in range(len(board) - target + 1):
        for col in range(target - 1, len(board[row])):
            window = [board[row + i][col - i] for i in range(target)]
            if all(val != -1 for val in window):
                score += 1
            if all(val != 1 for val in window):
                score -= 1
    return score

def evaluate3(board, target):
    score = 0
    base = target
    # Score rows
    for row in range(len(board)):
        for col in range(len(board[row]) - target + 1):
            window = board[row][col:col + target]
            if all(val != -1 for val in window):
                score += base**(sum([val == 1 for val in window])-1)
            if all(val != 1 for val in window):
                score -= base**(sum([val == -1 for val in window])-1)
    # Score columns
    for row in range(len(board) - target + 1):
        for col in range(len(board[row])):
            window = [board[row + i][col] for i in range(target)]
            if all(val != -1 for val in window):
                score += base**(sum([val == 1 for val in window])-1)
            if all(val != 1 for val in window):
                score -= base**(sum([val == -1 for val in window])-1)
    # Score diagonals (top-left to bottom-right)
    for row in range(len(board) - target + 1):
        for col in range(len(board[row]) - target + 1):
            window = [board[row + i][col + i] for i in range(target)]
            if all(val != -1 for val in window):
                score += base**(sum([val == 1 for val in window])-1)
            if all(val != 1 for val in window):
                score -= base**(sum([val == -1 for val in window])-1)
    # Score diagonals (top-right to bottom-left)
    for row in range(len(board) - target + 1):
        for col in range(target - 1, len(board[row])):
            window = [board[row + i][col - i] for i in range(target)]
            if all(val != -1 for val in window):
                score += base**(sum([val == 1 for val in window])-1)
            if all(val != 1 for val in window):
                score -= base**(sum([val == -1 for val in window])-1)
    return score

def evaluate4(board, target):
    score = 0
    base = target**2+1
    # Score rows
    for row in range(len(board)):
        for col in range(len(board[row]) - target + 1):
            window = list(board[row][col:col + target])
            if all(val != -1 for val in window):
                min_idx=window.index(1) if 1 in window else 0
                max_idx=len(window) - 1 - window[::-1].index(1) if 1 in window else len(window)-1
                score += base**(sum([val == 1 for val in window])-1)*math.exp((sum([val == 1 for val in window]))/(max_idx-min_idx+1))
            if all(val != 1 for val in window):
                min_idx=window.index(-1) if -1 in window else 0
                max_idx=len(window) - 1 - window[::-1].index(-1) if -1 in window else len(window)-1
                score -= base**(sum([val == -1 for val in window])-1)*math.exp((sum([val == -1 for val in window]))/(max_idx-min_idx+1))
    # Score columns
    for row in range(len(board) - target + 1):
        for col in range(len(board[row])):
            window = [board[row + i][col] for i in range(target)]
            if all(val != -1 for val in window):
                min_idx=window.index(1) if 1 in window else 0
                max_idx=len(window) - 1 - window[::-1].index(1) if 1 in window else len(window)-1
                score += base**(sum([val == 1 for val in window])-1)*math.exp((sum([val == 1 for val in window]))/(max_idx-min_idx+1))
            if all(val != 1 for val in window):
                min_idx=window.index(-1) if -1 in window else 0
                max_idx=len(window) - 1 - window[::-1].index(-1) if -1 in window else len(window)-1
                score -= base**(sum([val == -1 for val in window])-1)*math.exp((sum([val == -1 for val in window]))/(max_idx-min_idx+1))
    # Score diagonals (top-left to bottom-right)
    for row in range(len(board) - target + 1):
        for col in range(len(board[row]) - target + 1):
            window = [board[row + i][col + i] for i in range(target)]
            if all(val != -1 for val in window):
                min_idx=window.index(1) if 1 in window else 0
                max_idx=len(window) - 1 - window[::-1].index(1) if 1 in window else len(window)-1
                score += base**(sum([val == 1 for val in window])-1)*math.exp((sum([val == 1 for val in window]))/(max_idx-min_idx+1))
            if all(val != 1 for val in window):
                min_idx=window.index(-1) if -1 in window else 0
                max_idx=len(window) - 1 - window[::-1].index(-1) if -1 in window else len(window)-1
                score -= base**(sum([val == -1 for val in window])-1)*math.exp((sum([val == -1 for val in window]))/(max_idx-min_idx+1))
    # Score diagonals (top-right to bottom-left)
    for row in range(len(board) - target + 1):
        for col in range(target - 1, len(board[row])):
            window = [board[row + i][col - i] for i in range(target)]
            if all(val != -1 for val in window):
                min_idx=window.index(1) if 1 in window else 0
                max_idx=len(window) - 1 - window[::-1].index(1) if 1 in window else len(window)-1
                score += base**(sum([val == 1 for val in window])-1)*math.exp((sum([val == 1 for val in window]))/(max_idx-min_idx+1))
            if all(val != 1 for val in window):
                min_idx=window.index(-1) if -1 in window else 0
                max_idx=len(window) - 1 - window[::-1].index(-1) if -1 in window else len(window)-1
                score -= base**(sum([val == -1 for val in window])-1)*math.exp((sum([val == -1 for val in window]))/(max_idx-min_idx+1))
    return score

def evaluate(board, target, player):
    if not player:
        return evaluate4(board,target)
    else:
        return evaluate1(board,target)

def minimax(board, depth, is_maximizing, target, alpha, beta, max_depth, player):
    score = check_winner(board, target)
    if score == 1:
        return math.inf
    elif score == -1:
        return -math.inf
    elif is_full(board):
        return 0
    elif depth >= max_depth:
        return evaluate(board, target, player)
    if is_maximizing:
        best_score = -float('inf')
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 0:
                    board[i][j] = 1
                    score = minimax(board, depth + 1, False, target, alpha, beta, max_depth, player)
                    board[i][j] = 0
                    best_score = max(score, best_score)
                    alpha = max(alpha, best_score)
                    if best_score >= beta:
                        break
        return best_score
    else:
        best_score = float('inf')
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 0:
                    board[i][j] = -1
                    new_board=copy.deepcopy(board)
                    score = minimax(new_board, depth + 1, True, target, alpha, beta, max_depth, player)
                    board[i][j] = 0
                    best_score = min(score, best_score)
                    beta = min(beta, best_score)
                    if best_score <= alpha:
                        break
        return best_score

def move_worker(input_queue, result_queue):
    while True:
        i, j, board, is_maximizing, target, max_depth, alpha, beta, player =input_queue.get()
        #print(f"Get Data for Move @ ({i,j} @ Depth {max_depth})")
        board[i][j] = 1 if is_maximizing else -1
        score = minimax(board, 0, not is_maximizing, target, alpha, beta, max_depth, player)
        board[i][j] = 0
        #print(f"Scoring: {(i, j, max_depth, score)}")
        result_queue.put((i, j, max_depth, score))

def make_move(board, is_maximizing, target, player):
    start_time = time.time()
    best_score={}
    best_move={}
    alpha={}
    beta={}
    immediate_winning_move = (-1, -1)
    intermediate_winning_move = {1:[], 2:[], 3:[], 4:[]}
    opponent_winning_move = {0: (-1,-1), 1:[], 2:[], 3:[], 4:[]}
    #Check Winning and Blocking Moves
    possible_moves=[]
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 0:
                board[i][j] = 1 if is_maximizing else -1
                #S0 (Immediate Winning): Take the winning move if available
                if is_winning_move(board, target, i, j):
                    immediate_winning_move = (i, j)
                    delta=time.time() - start_time
                    print(f"Move time: {'{:.2f}s'.format(delta)}")
                    print("Winning Move.")
                    return immediate_winning_move
                board[i][j] = 0
                #S0 (Immediate Winning) Check if the opponent has a winning move
                # Block opponent's winning move if needed
                board[i][j] = -1 if is_maximizing else 1
                if is_winning_move(board, target, i, j):
                    opponent_winning_move[0] = (i, j)
                    board[i][j] = 0
                    continue
                board[i][j] = 0
                possible_moves.append((i,j))
                if target>=len(board)-1:
                    continue
                #Chek for Additional Patterns for Player
                board[i][j] = 1 if is_maximizing else -1
                tmp_immediate_winning_move=intermediate_winning_pattern(board, target, i, j, player)
                for idx in range(1, 5):
                    intermediate_winning_move[idx]+=tmp_immediate_winning_move[idx]
                board[i][j] = 0
                #Chek for Additional Patterns for Opponent
                board[i][j] = -1 if is_maximizing else 1
                tmp_immediate_winning_move=intermediate_winning_pattern(board, target, i, j, not player)
                for idx in range(1, 5):
                    opponent_winning_move[idx]+=tmp_immediate_winning_move[idx]
                board[i][j] = 0
    #First Move
    if len(possible_moves)==len(board)**2:
        if len(board)%2==0:
            i=random.choice([len(board)//2,len(board)//2-1])
            j=random.choice([len(board)//2,len(board)//2-1])
        else:
            i=len(board)//2
            j=len(board)//2
        return (i,j)
    #Iterate Through Player and Opponent's winning move down the list
    # Block opponent's winning move if needed:
    if opponent_winning_move[0]!=(-1,-1):
        delta=time.time() - start_time
        print(f"Move time: {'{:.2f}s'.format(delta)}")
        print("Blocking Move.")
        return opponent_winning_move[0]
    for idx in range(1,5):
        if intermediate_winning_move[idx]!=[]:
            delta=time.time() - start_time
            print(f"Move time: {'{:.2f}s'.format(delta)}")
            print(f"Intermediate Winning Move @ Scenario{idx}.")
            return random.choice(intermediate_winning_move[idx])
        elif opponent_winning_move[idx]!=[]:
            delta=time.time() - start_time
            print(f"Move time: {'{:.2f}s'.format(delta)}")
            print(f"Intermediate Blocking Move @ Scenario {idx}.")
            return random.choice(opponent_winning_move[idx])
    #MinMax with Iterative Deepenining
    max_depth=0
    depth_res_count={0:0}
    best_move[max_depth]=[]
    alpha[max_depth]=-float('inf')
    beta[max_depth]=float('inf')
    score_map={0:[[None]*len(board) for _ in range(len(board))]}
    counter=0
    beta_cutoff=None
    #Queue Setup
    m=Manager()
    iqueue=m.Queue(maxsize=2)
    rqueue=m.Queue()
    #Dispatch Workers
    pool=Pool(cpu)
    pool_tuple=[(iqueue, rqueue) for _ in range(cpu)]
    pool.starmap_async(move_worker, pool_tuple)
    #Start the IDS Process
    idx=0
    skip=False
    #print(possible_moves)
    while True:
        if time.time()-start_time>TIMEOUT:
            pool.terminate()
            pool.join()
            break
        try:
            if skip==False:
                iqueue.put_nowait((possible_moves[idx][0], possible_moves[idx][1], board, is_maximizing, target, max_depth, alpha[max_depth], beta[max_depth], player))
                #print(f"Input Data {possible_moves[idx]}")
                if idx==len(possible_moves)-1:
                    max_depth=int(max_depth+1)
                    depth_res_count[max_depth]=0
                    best_move[max_depth]=[]
                    alpha[max_depth]=-float('inf')
                    beta[max_depth]=float('inf')
                    score_map[max_depth]=[[None]*len(board) for _ in range(len(board))]
                    if max_depth==len(possible_moves):
                        #print("Max Depth Reached")
                        skip=True
                        max_depth-=1
                idx= idx+1 if idx!=len(possible_moves)-1 else 0
                #print(f"Index {idx}")
        except:
            pass
        try:
            i, j, depth, score=rqueue.get_nowait()
            score_map[depth][i][j]=score
            depth_res_count[depth]+=1
            if is_maximizing and score > alpha[depth]:
                alpha[depth] = score
                best_move[depth] = [(i, j)]
            elif is_maximizing and score == alpha[depth]:
                best_move[depth].append((i, j))
            elif not is_maximizing and score < beta[depth]:
                #print(f"Update Beta: Current {beta[depth]} New {score}")
                #print(f"Move added: {(i, j)}")
                beta[depth] = score
                best_move[depth] = [(i, j)]
            elif not is_maximizing and score == beta[depth]:
                #print(f"Move {(i,j)} added to best_move[depth]")
                best_move[depth].append((i, j))
            if beta[depth]<=alpha[depth]:
                pool.terminate()
                pool.join()
                beta_cutoff=depth
                break
        except:
            if depth_res_count[max_depth]==len(possible_moves) and max_depth==len(possible_moves)-1:
                pool.terminate()
                pool.join()
                break

    #Beta Cutoff
    if beta_cutoff is not None:
        print('Beta cutoff')
        delta=time.time() - start_time
        print(f"Move time: {'{:.2f}s'.format(delta)}")
        return random.choice(best_move[beta_cutoff])
    #Check Results
    res_depth=0
    #print("Result Depth Count:", depth_res_count)
    #print("Possible moves: ",len(possible_moves))
    for idx, key in enumerate(sorted(list(depth_res_count.keys()), reverse=True)):
        if depth_res_count[key]==len(possible_moves):
            res_depth=key
            break

    delta=time.time() - start_time
    print(f"Move time: {'{:.2f}s'.format(delta)}")
    '''
    print(f"Best move @ depth {res_depth}")
    print(f'Best Score: {alpha[res_depth] if is_maximizing else beta[res_depth]}')
    print(f'Best Moves: \n{best_move[res_depth]}')
    print(f'Score map:')
    for i,row in enumerate(score_map[res_depth]):
        for col,con in enumerate(row):
            print(f"{con} ", end="")
        print("")
    '''
    #try close all remaining pool if exists
    try:
        pool.terminate()
        pool.join()
    except:
        pass
    #Return Best Move if None above
    return random.choice(best_move[res_depth])

def play_game(board_size, target):
    board = [[0 for _ in range(board_size)] for _ in range(board_size)]
    while True:
        # Player 1 (Maximizing player)
        print(f'Player {"X"}')
        row, col = make_move(board, True, target, True)
        board[row][col] = 1

        print_board(board)
        winner = check_winner(board, target)
        if winner != 0 or is_full(board):
            break

        # Player 2 (Minimizing player)
        print(f'Player {"O"}')
        row, col = make_move(board, False, target, False)
        board[row][col] = -1

        print_board(board)
        winner = check_winner(board, target)
        if winner != 0 or is_full(board):
            break
    #print(winner)
    if winner == 1:
        print("Player 1 (Maximizing player) wins!")
    elif winner == -1:
        print("Player 2 (Minimizing player) wins!")
    else:
        print("It's a draw!")

def print_board(board):
    for row in board:
        print(" ".join(["X" if x == 1 else "O" if x == -1 else "_" for x in row]))
    print()

def string_to_board(boardstr):
    ele_dict={"O":-1, "X":1, "_":0, "-":0}
    rows=boardstr.split("\n")
    rows.remove("")
    if " " in rows[0]:
        board=[[ele_dict[ele] for ele in row.split(" ")] for idx, row in enumerate(rows)]
    else:
        board=[[ele_dict[ele] for ele in [*row]] for idx, row in enumerate(rows)]
    return board

if __name__=='__main__':
    # Set your desired board size and target, then start the game
    #board_size = 8
    #target = 5
    board_size = 3
    target = 3
    play_game(board_size, target)

