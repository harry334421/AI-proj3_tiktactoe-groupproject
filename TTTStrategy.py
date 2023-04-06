'''
Strategy Class That Defines all Strategy Functions
'''

class TTTStrategy:
    def __init__(self):
        import math 
        import numpy as np
        self.np=np
        self.math=math 
        
    #Function to Check Winner 
    #Now Only Checks the Around Last Action, which is reasonable
    def check_winner(self, board, target, row, col):
        rows, cols = board.shape
        diag1=col-row
        pos1=row if diag1>=0 else col 
        diag2=(cols-1-col)-row
        pos2=row if diag2>0 else (cols-1-col)
        # Check rows
        for j in range(max(0, row-target+1), cols - target + 1):
            window = board[row, j:j + target]
            if self.np.all(window == 1):
                return 1
            elif self.np.all(window == -1):
                return -1
        # Check columns
        for i in range(max(0, col-target+1), rows - target + 1):
            window = board[i:i + target, col]
            if self.np.all(window == 1):
                return 1
            elif self.np.all(window == -1):
                return -1
        # Check diagonals (top-left to bottom-right)
        array=board.diagonal(diag1)
        if len(array)>=target:
            for i in range(max(0, pos1-target+1), len(array) - target + 1):
                window = array[i:i+target]
                #print(window)
                if self.np.all(self.np.diag(window) == 1):
                    return 1
                elif self.np.all(self.np.diag(window) == -1):
                    return -1
        # Check diagonals (top-right to bottom-left)
        array=self.np.fliplr(board).diagonal(diag2)
        if len(array)>=target:
            for i in range(max(0, pos2-target+1), len(array) - target + 1):
                window = array[i:i+target]
                if self.np.all(self.np.diag(window) == 1):
                    return 1
                elif self.np.all(self.np.diag(window) == -1):
                    return -1
        return 0
    
    #Function to Check Full Board
    def is_full(self, board):
        return all(0 not in row for row in board)
    #Get Possible Moves 
    def get_possible_moves(self, board):
        indices=self.np.where(board==0)
        return list(zip(indices[0], indices[1]))
    
    #Check Immediate Winning Move
    def is_winning_move(self, board, target, row, col):
        player = board[row][col]
        #Check Winner
        if self.check_winner(board, target, row, col)==player:
            return True
        return False
    
    #Rank Moves that is closer to last moves 
    def rank_moves(self, possible_moves, last_moves):
        last_moves=last_moves+last_moves if len(last_moves)==1 else last_moves
        #print(possible_moves)
        dist1=[max(abs(move[0]-last_moves[0][0]),abs(move[1]-last_moves[0][1])) for i, move in enumerate(possible_moves)]
        #print(dist1)
        dist2=[max(abs(move[0]-last_moves[1][0]),abs(move[1]-last_moves[1][1])) for i, move in enumerate(possible_moves)]
        #print(dist2)
        min_dist=[min(d1,d2) for d1, d2 in zip(dist1, dist2)]
        '''
        print(min_dist)
        for i, move in enumerate(possible_moves):
            print(f"Move: {move}")
            print(f"Dist: {min_dist[i]}")
        '''
        sorted_moves = [move for _, move in sorted(zip(min_dist, possible_moves))]
        return sorted_moves
    
    #Check Winning Moves in Two Steps using Known Patterns
    def intermediate_winning_pattern(self, board, target, row, col, player):
        player=1 if player else -1
        #results holder
        intermediate_winning_move={1:[], 2:[], 3:[], 4:[]}
        #One T-1 Sequence Two-Way Unblocked
        count_2w_tm1, count_2w_tm1_seq=self.find_2way_unblocked_sequences(board, target, target-1, player, max_gap=0)
        for seq in count_2w_tm1_seq:
            if (row, col) in seq:
                intermediate_winning_move[1].append((row,col))
                break
        #Two T-1 Sequence One-Way Unblocked
        count_1w_tm1, count_1w_tm1_seq=self.find_1way_unblocked_sequences(board, target, target-1, player)
        counter=0
        for seq in count_1w_tm1_seq:
            if (row, col) in seq: counter+=1
            if counter==2:
                intermediate_winning_move[1].append((row,col))
        #One T-1 Sequence One-Way Blocked and one T-2 Sequence Two-way Unblocked
        count_2w_tm2, count_2w_tm2_seq=self.find_1way_unblocked_sequences(board, target, target-1, player)
        for seq1 in count_1w_tm1_seq:
            if (row, col) in seq:
                for seq2 in count_2w_tm2_seq:
                    if (row, col) in seq2:
                        intermediate_winning_move[2].append((row,col))
        #Two T-2 Sequence Two-Way Unblocked
        counter=0
        for seq in count_2w_tm2_seq:
            if (row, col) in seq: counter+=1
            if counter==2:
                intermediate_winning_move[3].append((row,col))
        #One T-2 Sequence Two-Way Unblocked and One T-2 Sequence One-Way Unblocked
        count_1w_tm2, count_1w_tm2_seq=self.find_1way_unblocked_sequences(board, target, target-2, player)
        for seq in count_2w_tm2_seq:
            if (row, col) in seq:
                for seq2 in count_1w_tm2_seq:
                        if (row, col) in seq2:
                            intermediate_winning_move[4].append((row,col))
        return intermediate_winning_move
    
    ##Ancillary Function to Check Unblocked Sequences
    def find_2way_unblocked_sequences(self, board, target, required_length, player, max_gap=1):
        # Window Length
        window_lengths = []
        for gap in range(max_gap + 1):
            window_lengths.append(min(max(required_length + gap + 2, target), board.shape[1]))
        window_lengths = list(set(window_lengths))
        # Player
        unblocked_count = 0
        unblocked_list = []
        # Check Row
        for row in range(board.shape[0]):
            array = board[row]
            for window_length in window_lengths:
                for idx1 in range(board.shape[1] - window_length + 1):
                    window = array[idx1:idx1 + window_length]
                    if all(val != -player for val in window) and sum(val == player for val in window) == required_length:
                        min_idx = list(window).index(player)
                        max_idx = len(window) - 1 - list(window)[::-1].index(player)
                        gaps = max_idx - min_idx + 1 - required_length
                        if gaps <= 1 and min_idx != 0 and max_idx != len(window) - 1:
                            seq = []
                            for idx2, role in enumerate(window):
                                if role == player:
                                    seq.append((row, idx1 + idx2))
                            if seq not in unblocked_list:
                                unblocked_list.append(seq)
                                unblocked_count += 1

        #Check Column
        for col in range(board.shape[1]):
            array = board.transpose()[col]
            for window_length in window_lengths:
                for idx1 in range(board.shape[0] - window_length + 1):
                    window = array[idx1:idx1 + window_length]
                    if all(val != -player for val in window) and sum(val == player for val in window) == required_length:
                        min_idx = list(window).index(player)
                        max_idx = len(window) - 1 - list(window)[::-1].index(player)
                        gaps = max_idx - min_idx + 1 - required_length
                        if gaps <= 1 and min_idx != 0 and max_idx != len(window) - 1:
                            seq = []
                            for idx2, role in enumerate(window):
                                if role == player:
                                    seq.append((idx1 + idx2, col))
                            if seq not in unblocked_list:
                                unblocked_list.append(seq)
                                unblocked_count += 1
        
        #Diagonal
        for idx0 in range(board.shape[0]):
            array = self.np.diagonal(board, offset=idx0)
            for window_length in window_lengths:
                if len(array) >= window_length:
                    for idx1 in range(len(array) - window_length + 1):
                        window = array[idx1:idx1 + window_length]
                        if all(val != -player for val in window) and sum(val == player for val in window) == required_length:
                            min_idx = list(window).index(player)
                            max_idx = len(window) - 1 - list(window)[::-1].index(player)
                            gaps = max_idx - min_idx + 1 - required_length
                            if gaps <= 1 and min_idx != 0 and max_idx != len(window) - 1:
                                seq = []
                                for idx2, role in enumerate(window):
                                    if role == player and idx0 >= 0:
                                        seq.append((idx0 + idx1 + idx2, idx1 + idx2))
                                    elif role == player and idx0 < 0:
                                        seq.append((idx1 + idx2, idx0 + idx1 + idx2))
                                if seq not in unblocked_list:
                                    unblocked_list.append(seq)
                                    unblocked_count += 1
        
        #Anti-Diagonal
        for idx0 in range(board.shape[0]):
            for dr in [-1,1]:
                array = self.np.fliplr(board).diagonal(idx0*dr)
                for window_length in window_lengths:
                    if len(array) >= window_length:
                        for idx1 in range(len(array)-window_length+1):
                            window = array[idx1:idx1+window_length]
                            if all(val != -player for val in window) and sum(val == player for val in window) == required_length:
                                min_idx = list(window).index(player)
                                max_idx = len(window) - 1 - required_length
                                gaps = max_idx - min_idx + 1 - sum(window)
                                if gaps <= 1 and min_idx != 0 and max_idx != len(window)-1:
                                    seq = []
                                    for idx2, role in enumerate(window):
                                        if role == player and dr == 1:
                                            seq.append((board.shape[0] - 1 - (idx1+idx2), idx0+idx1+idx2))
                                        elif role == player and dr == -1:
                                            seq.append((board.shape[0] - 1 - (idx0+idx1+idx2), idx1+idx2))
                                    if seq not in unblocked_list:
                                        unblocked_list.append(seq)
                                        unblocked_count += 1
        return unblocked_count, unblocked_list
    
    def find_1way_unblocked_sequences(self, board, target, required_length, player, max_gap=1):
        
        window_lengths=[]
        for gap in range(max_gap+1):
            window_lengths.append(min(max(required_length+gap+2, target),board.shape[1]))
        window_lengths=list(set(window_lengths))
        #Player
        unblocked_count=0
        unblocked_list=[]
        #Check Row
        for row in range(board.shape[0]):
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
                    elif (sum(val == -player for val in window)==0 and (idx1==0 or idx1+window_length==board.shape[1])) and sum(val == player for val in window)==required_length:
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
        for col in range(board.shape[1]):
            array = board[:, col]
            for window_length in window_lengths:
                for idx1 in range(len(array)-window_length+2):
                    window = array[idx1:idx1+window_length]
                    if (self.np.count_nonzero(window == -player) == 1 and (window[0] == -player or window[-1] == -player)) and self.np.count_nonzero(window == player) == required_length:
                        flag_idx = self.np.where(window == -player)[0][0]
                        min_idx = self.np.where(window == player)[0][0]
                        max_idx = len(window) - 1 - self.np.where(window[::-1] == player)[0][0]
                        gaps = max_idx - min_idx + 1 - required_length
                        if gaps <= 1 and (min_idx == flag_idx+1 or max_idx == flag_idx-1):
                            seq = []
                            for idx2, role in enumerate(window):
                                if role == player:
                                    seq.append((idx1+idx2, col))
                            if seq not in unblocked_list:
                                unblocked_list.append(seq)
                                unblocked_count += 1
                    elif (self.np.count_nonzero(window == -player) == 0 and (idx1 == 0 or idx1+window_length == len(board))) and self.np.count_nonzero(window == player) == required_length:
                        min_idx = self.np.where(window == player)[0][0]
                        max_idx = len(window) - 1 - self.np.where(window[::-1] == player)[0][0]
                        gaps = max_idx - min_idx + 1 - required_length
                        if gaps <= 1 and (min_idx == 0 or max_idx == len(window)-1):
                            seq = []
                            for idx2, role in enumerate(window):
                                if role == player:
                                    seq.append((idx1+idx2, col))
                            if seq not in unblocked_list:
                                unblocked_list.append(seq)
                                unblocked_count += 1
        #Diagonal
        for idx0 in range(board.shape[0]):
            for dr in [-1,1]:
                array = self.np.diagonal(board, idx0 * dr)
                for window_length in window_lengths:
                    if len(array) >= window_length:
                        for idx1 in range(len(array) - window_length + 2):
                            window = array[idx1:idx1+window_length]
                            if (self.np.count_nonzero(window == -player) == 1 and (window[0] == -player or window[-1] == -player)) and self.np.count_nonzero(window == player) == required_length:
                                flag_idx = self.np.where(window == -player)[0][0]
                                min_idx = self.np.where(window == player)[0][0]
                                max_idx = self.np.where(window == player)[0][-1]
                                gaps = max_idx - min_idx + 1 - required_length
                                if gaps <= 1 and (min_idx == flag_idx + 1 or max_idx == flag_idx - 1):
                                    seq = []
                                    for idx2, role in enumerate(window):
                                        if role == player and dr == 1:
                                            seq.append((idx1+idx2, idx0+idx1+idx2))
                                        elif role == player and dr == -1:
                                            seq.append((idx0+idx1+idx2, idx1+idx2))
                                    if seq not in unblocked_list:
                                        unblocked_list.append(seq)
                                        unblocked_count += 1
                            elif (self.np.count_nonzero(window == -player) == 0 and (idx1 == 0 or idx1+window_length == len(board))) and self.np.count_nonzero(window == player) == required_length:
                                min_idx = self.np.where(window == player)[0][0]
                                max_idx = self.np.where(window == player)[0][-1]
                                gaps = max_idx - min_idx + 1 - required_length
                                if gaps <= 1 and (min_idx == 0 or max_idx == len(window)-1):
                                    seq = []
                                    for idx2, role in enumerate(window):
                                        if role == player and dr == 1:
                                            seq.append((idx1+idx2, idx0+idx1+idx2))
                                        elif role == player and dr == -1:
                                            seq.append((idx0+idx1+idx2, idx1+idx2))
                                    if seq not in unblocked_list:
                                        unblocked_list.append(seq)
                                        unblocked_count += 1
        #Anti-Diagonal
        for idx0 in range(board.shape[0]):
            for dr in [-1, 1]:
                array = self.np.fliplr(board).diagonal(idx0 * dr)
                for window_length in window_lengths:
                    if len(array) >= window_length:
                        for idx1 in range(len(array) - window_length + 1):
                            window = array[idx1 : idx1 + window_length]
                            if (
                                (sum(val == -player for val in window) == 1 and (window[0] == -player or window[-1] == -player))
                                and sum(val == player for val in window) == required_length
                            ):
                                flag_idx = list(window).index(-player)
                                min_idx = list(window).index(player)
                                max_idx = len(window) - 1 - list(window)[::-1].index(player)
                                gaps = max_idx - min_idx + 1 - required_length
                                # print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                                if gaps <= 1 and (min_idx == flag_idx + 1 or max_idx == flag_idx - 1):
                                    seq = []
                                    for idx2, role in enumerate(window):
                                        if role == player and dr == 1:
                                            seq.append((len(board) - 1 - (idx1 + idx2), idx0 + idx1 + idx2))
                                        elif role == player and dr == -1:
                                            seq.append((len(board) - 1 - (idx0 + idx1 + idx2), idx1 + idx2))
                                    if seq not in unblocked_list:
                                        unblocked_list.append(seq)
                                        unblocked_count += 1
                            elif (
                                (sum(val == -player for val in window) == 0 and (idx1 == 0 or idx1 + window_length == len(board)))
                                and sum(val == player for val in window) == required_length
                            ):
                                min_idx = list(window).index(player)
                                max_idx = len(window) - 1 - list(window)[::-1].index(player)
                                gaps = max_idx - min_idx + 1 - required_length
                                # print(f"Min Index:{min_idx}, Max Index:{max_idx}, Gaps:{gaps}")
                                if gaps <= 1 and (min_idx == 0 or max_idx == len(window) - 1):
                                    seq = []
                                    for idx2, role in enumerate(window):
                                        if role == player and dr == 1:
                                            seq.append((len(board) - 1 - (idx1 + idx2), idx0 + idx1 + idx2))
                                        elif role == player and dr == -1:
                                            seq.append((len(board) - 1 - (idx0 + idx1 + idx2), idx1 + idx2))
                                    if seq not in unblocked_list:
                                        unblocked_list.append(seq)
                                        unblocked_count += 1
        return unblocked_count, unblocked_list

    # Board Evaluator Functions
    def evaluate1(self, board, target):
        #Base for Exponential 
        base = target**2+1
        
        
        #Board Size 
        rows, cols=board.shape
        
        # Calculate score for rows
        row_scores = self.np.zeros(rows, dtype='float64')
        for j in range(cols-target+1):
            sub_board=board[:,j:j+target]
            flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=1)
            flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=1)
            flag=flag_x+flag_o
            row_scores+=self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis], axis=1))*flag
        score = self.np.sum(row_scores)
        #print(score)
        # Calculate score for columns
        col_scores = self.np.zeros(cols, dtype='float64')
        for i in range(rows-target+1):
            sub_board=board[i:i+target,:]
            flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=0)
            flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=0)
            flag=flag_x+flag_o
            col_scores+=self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis].T, axis=0))*flag
        score += self.np.sum(col_scores)
        #print(score)
        # Calculate score for diagonals
        for idx in range(rows-target+1):
            idx_list=list(set([idx,-idx]))
            sub_board1=[self.np.diagonal(board, offset=i) for i in idx_list] #Diagonal
            sub_board2=[self.np.diagonal(self.np.fliplr(board), offset=i) for i in idx_list] #Anti-Diagonal
            diag_board=self.np.array(sub_board1+sub_board2)
            d_rows, d_cols=diag_board.shape
            row_scores = self.np.zeros(d_rows, dtype='float64')
            #print(row_scores)
            for i in range(d_cols-target+1):
                sub_board=diag_board[:,i:i+target]
                #print(sub_board)
                flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=1)
                flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=1)
                flag=flag_x+flag_o
                row_scores+=self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis], axis=1))*flag
            score += self.np.sum(row_scores)
        return score

    def evaluate2(self, board, target):
        #Base for Exponential 
        base = target**2+1
        
        #Board Size 
        rows, cols=board.shape
        
        # Calculate score for rows
        row_scores = self.np.zeros(rows, dtype='float64')
        for j in range(cols-target+1):
            sub_board=board[:,j:j+target]
            flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=1)
            flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=1)
            flag=flag_x+flag_o
            row_scores+=self.np.max(sub_board*flag[:, self.np.newaxis], axis=1)*flag
        score = self.np.sum(row_scores)
        # Calculate score for columns
        col_scores = self.np.zeros(cols, dtype='float64')
        for i in range(rows-target+1):
            sub_board=board[i:i+target,:]
            flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=0)
            flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=0)
            flag=flag_x+flag_o
            col_scores+=self.np.max(sub_board*flag[:, self.np.newaxis].T, axis=0)*flag
        score += self.np.sum(col_scores)
        # Calculate score for diagonals
        for idx in range(rows-target+1):
            idx_list=list(set([idx,-idx]))
            sub_board1=[self.np.diagonal(board, offset=i) for i in idx_list] #Diagonal
            sub_board2=[self.np.diagonal(self.np.fliplr(board), offset=i) for i in idx_list] #Anti-Diagonal
            diag_board=self.np.array(sub_board1+sub_board2)
            d_rows, d_cols=diag_board.shape
            row_scores = self.np.zeros(d_rows, dtype='float64')
            #print(row_scores)
            for i in range(d_cols-target+1):
                sub_board=diag_board[:,i:i+target]
                #print(sub_board)
                flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=1)
                flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=1)
                flag=flag_x+flag_o
                row_scores+=self.np.max(sub_board*flag[:, self.np.newaxis], axis=1)*flag
            score += self.np.sum(row_scores)
        return score

    def evaluate3(self, board, target):
        #Base for Exponential 
        base = target
        
        
        #Board Size 
        rows, cols=board.shape
        
        # Calculate score for rows
        row_scores = self.np.zeros(rows, dtype='float64')
        for j in range(cols-target+1):
            sub_board=board[:,j:j+target]
            flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=1)
            flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=1)
            flag=flag_x+flag_o
            row_scores+=self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis], axis=1))*flag
        score = self.np.sum(row_scores)
        
        # Calculate score for columns
        col_scores = self.np.zeros(cols, dtype='float64')
        for i in range(rows-target+1):
            sub_board=board[i:i+target,:]
            flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=0)
            flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=0)
            flag=flag_x+flag_o
            col_scores+=self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis].T, axis=0))*flag
        score += self.np.sum(col_scores)
        
        # Calculate score for diagonals
        for idx in range(rows-target+1):
            idx_list=list(set([idx,-idx]))
            sub_board1=[self.np.diagonal(board, offset=i) for i in idx_list] #Diagonal
            sub_board2=[self.np.diagonal(self.np.fliplr(board), offset=i) for i in idx_list] #Anti-Diagonal
            diag_board=self.np.array(sub_board1+sub_board2)
            d_rows, d_cols=diag_board.shape
            row_scores = self.np.zeros(d_rows, dtype='float64')
            #print(row_scores)
            for i in range(d_cols-target+1):
                sub_board=diag_board[:,i:i+target]
                #print(sub_board)
                flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=1)
                flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=1)
                flag=flag_x+flag_o
                row_scores+=self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis], axis=1))*flag
            score += self.np.sum(row_scores)
        return score

    def evaluate4(self, board, target):
        #Base for Exponential 
        base = target**2+1
        
        #Board Size 
        rows, cols=board.shape
        
        # Calculate score for rows
        row_scores = self.np.zeros(rows, dtype='float64')
        for j in range(cols-target+1):
            sub_board=board[:,j:j+target]
            flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=1)
            flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=1)
            flag=flag_x+flag_o
            row_flag = self.np.arange(sub_board.shape[0])[:, self.np.newaxis]
            discount=abs(self.np.sum(sub_board, axis=1)*flag)/(sub_board.shape[1] - self.np.argmax((sub_board == flag[row_flag])[:, ::-1], axis=1) - self.np.argmax(sub_board == flag[row_flag], axis=1))
            row_scores+=(self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis], axis=1))*flag)*self.np.expm1(discount)
        score = self.np.sum(row_scores)
        
        # Calculate score for columns
        col_scores = self.np.zeros(cols, dtype='float64')
        for i in range(rows-target+1):
            sub_board=board[i:i+target,:]
            flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=0)
            flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=0)
            flag=flag_x+flag_o
            col_flag = self.np.arange(sub_board.shape[1])[self.np.newaxis, :]
            discount=abs(self.np.sum(sub_board, axis=0))/(sub_board.shape[0] - self.np.argmax((sub_board.T == flag[:, self.np.newaxis])[:, ::-1], axis=1) - self.np.argmax(sub_board.T == flag[:, self.np.newaxis], axis=1))
            col_scores+=self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis].T, axis=0))*flag*self.np.expm1(discount)
        score += self.np.sum(col_scores)
        
        # Calculate score for diagonals
        for idx in range(rows-target+1):
            idx_list=list(set([idx,-idx]))
            sub_board1=[self.np.diagonal(board, offset=i) for i in idx_list] #Diagonal
            sub_board2=[self.np.diagonal(self.np.fliplr(board), offset=i) for i in idx_list] #Anti-Diagonal
            diag_board=self.np.array(sub_board1+sub_board2)
            d_rows, d_cols=diag_board.shape
            diag_scores = self.np.zeros(d_rows, dtype='float64')
            for i in range(d_cols-target+1):
                sub_board=diag_board[:,i:i+target]
                flag_x = self.np.max(self.np.where(sub_board == 1, 1, 0),axis=1)
                flag_o = self.np.min(self.np.where(sub_board == -1, -1, 0),axis=1)
                flag=flag_x+flag_o
                row_flag = self.np.arange(sub_board.shape[0])[:, self.np.newaxis]
                discount=abs(self.np.sum(sub_board, axis=1)*flag)/(sub_board.shape[1] - self.np.argmax((sub_board == flag[row_flag])[:, ::-1], axis=1) - self.np.argmax(sub_board == flag[row_flag], axis=1))
                diag_scores+=(self.np.power(base, self.np.sum(sub_board*flag[:, self.np.newaxis], axis=1))*flag)*self.np.expm1(discount)
            score += self.np.sum(diag_scores)
        return score

    def evaluate(self, board, target, evaluator):
        if evaluator==1:
            return self.evaluate1(board,target)
        elif evaluator==2:
            return self.evaluate2(board,target)
        elif evaluator==3: 
            return self.evaluate3(board,target)
        elif evaluator==4:
            return self.evaluate4(board,target)
    
    def minmax(self, board, depth, row, col, is_maximizing, target, alpha, beta, max_depth, last_moves, evaluator):
        winner = self.check_winner(board, target, row, col)
        if winner == 1:
            return math.inf
        elif winner == -1:
            return -math.inf
        elif self.is_full(board):
            return 0
        elif depth >= max_depth:
            return self.evaluate(board, target, evaluator)
        #Rank Possible Moves 
        ranked_moves=self.rank_moves(self.get_possible_moves(board), last_moves)
        if is_maximizing:
            best_score = -float('inf')
            for idx,move in enumerate(ranked_moves):
                i, j = move
                board[i][j] = 1
                new_last_moves=[last_moves[-1], move]
                #print(new_last_moves)
                score = self.minmax(board, depth + 1, i, j, False, target, alpha, beta, max_depth, new_last_moves, evaluator)
                board[i][j] = 0
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if best_score >= beta:
                    break
            return best_score
        else:
            best_score = float('inf')
            for idx,move in enumerate(ranked_moves):
                i, j = move
                board[i][j] = -1
                new_last_moves=[last_moves[-1], move]
                score = self.minmax(board, depth + 1, i, j, True, target, alpha, beta, max_depth, new_last_moves, evaluator)
                board[i][j] = 0
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if best_score <= alpha:
                    break
            return best_score


