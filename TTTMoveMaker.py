'''
Dependencies 
'''
import random
from multiprocessing import Manager, Queue, Pool, cpu_count
from TTTStrategy import TTTStrategy
import time 

'''
Functions 
'''

'''
Mover Worker for Multiprocessing
'''
def move_worker(input_queue, result_queue):
    ttt=TTTStrategy()
    while True:
        try:
            #ranked_moves[idx][0], ranked_moves[idx][1], board, is_maximizing, target, max_depth, alpha[max_depth], beta[max_depth], new_last_moves, evaluator
            i, j, board, is_maximizing, target, max_depth, alpha, beta, last_moves, evaluator =input_queue.get()
            #print(f"Get Data for Move @ ({i,j} @ Depth {max_depth})")
            board[i][j] = 1 if is_maximizing else -1
            score = ttt.minmax(board, 0, i, j, not is_maximizing, target, alpha, beta, max_depth, last_moves, evaluator)
            board[i][j] = 0
            #print(f"Scoring: {(i, j, max_depth, score)}")
            result_queue.put((i, j, max_depth, score))
        except Exception as e:
            print(f"Exception: {e}")
        except:
            print("Wait for data")
            pass

'''
Function to Determine a Move 
'''
def make_move(board, is_maximizing, target, last_moves, evaluator, timeout, ttt):
    cpu=cpu_count()-1
    start_time = time.time()
    best_score={}
    best_move={}
    alpha={}
    beta={}
    immediate_winning_move = (-1, -1)
    intermediate_winning_move = {1:[], 2:[], 3:[], 4:[]}
    opponent_winning_move = {0: (-1,-1), 1:[], 2:[], 3:[], 4:[]}
    '''
    Start the asychronized processes early on to save time 
    '''
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
    
    
    '''
    Back to Pattern Checking while the async processes is starting 
    '''
    #Check Winning and Blocking Moves
    possible_moves=ttt.get_possible_moves(board)
    for idx, move in enumerate(possible_moves):
        i,j=move
        board[i][j] = 1 if is_maximizing else -1
        #S0 (Immediate Winning): Take the winning move if available
        if ttt.is_winning_move(board, target, i, j):
            immediate_winning_move = (i, j)
            delta=time.time() - start_time
            print(f"Move time: {'{:.2f}s'.format(delta)}")
            print("Winning Move.")
            return immediate_winning_move
        board[i][j] = 0
        #S0 (Immediate Winning) Check if the opponent has a winning move
        # Block opponent's winning move if needed
        board[i][j] = -1 if is_maximizing else 1
        if ttt.is_winning_move(board, target, i, j):
            opponent_winning_move[0] = (i, j)
            board[i][j] = 0
            continue
        board[i][j] = 0
        if target>=len(board)-1:
            continue
        #Chek for Additional Patterns for Player
        board[i][j] = 1 if is_maximizing else -1
        tmp_immediate_winning_move=ttt.intermediate_winning_pattern(board, target, i, j, is_maximizing)
        for idx in range(1, 5):
            intermediate_winning_move[idx]+=tmp_immediate_winning_move[idx]
        board[i][j] = 0
        #Chek for Additional Patterns for Opponent
        board[i][j] = -1 if is_maximizing else 1
        tmp_immediate_winning_move=ttt.intermediate_winning_pattern(board, target, i, j, not is_maximizing)
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
        pool.terminate()
        pool.join()
        return (i,j)
    #Iterate Through Player and Opponent's winning move down the list
    # Block opponent's winning move if needed:
    if opponent_winning_move[0]!=(-1,-1):
        delta=time.time() - start_time
        print(f"Move time: {'{:.2f}s'.format(delta)}")
        print("Blocking Move.")
        pool.terminate()
        pool.join()
        return opponent_winning_move[0]
    for idx in range(1,5):
        if intermediate_winning_move[idx]!=[]:
            delta=time.time() - start_time
            print(f"Move time: {'{:.2f}s'.format(delta)}")
            print(f"Intermediate Winning Move @ Scenario{idx}.")
            pool.terminate()
            pool.join()
            return random.choice(intermediate_winning_move[idx])
        elif opponent_winning_move[idx]!=[]:
            delta=time.time() - start_time
            print(f"Move time: {'{:.2f}s'.format(delta)}")
            print(f"Intermediate Blocking Move @ Scenario {idx}.")
            pool.terminate()
            pool.join()
            return random.choice(opponent_winning_move[idx])
    #Rank Possible Moves 
    ranked_moves=ttt.rank_moves(possible_moves, last_moves)
    #print(ranked_moves)
    #print(board)
    while True:
        if time.time()-start_time>timeout:
            pool.terminate()
            pool.join()
            break
        try:
            if skip==False:
                new_last_moves=[last_moves[-1], ranked_moves[idx]]
                #print(f"Input Data:{(ranked_moves[idx][0], ranked_moves[idx][1], board, is_maximizing, target, max_depth, alpha[max_depth], beta[max_depth], player, new_last_moves)}")
                iqueue.put_nowait((ranked_moves[idx][0], ranked_moves[idx][1], board, is_maximizing, target, max_depth, alpha[max_depth], beta[max_depth], new_last_moves, evaluator))
                #print(f"Input Data {possible_moves[idx]}")
                if idx==len(ranked_moves)-1:
                    max_depth=int(max_depth+1)
                    depth_res_count[max_depth]=0
                    best_move[max_depth]=[]
                    alpha[max_depth]=-float('inf')
                    beta[max_depth]=float('inf')
                    score_map[max_depth]=[[None]*len(board) for _ in range(len(board))]
                    if max_depth==len(ranked_moves):
                        #print("Max Depth Reached")
                        skip=True
                        max_depth-=1
                idx= idx+1 if idx!=len(ranked_moves)-1 else 0
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
            if depth_res_count[max_depth]==len(ranked_moves) and max_depth==len(ranked_moves)-1:
                pool.terminate()
                pool.join()
                break

    #Beta Cutoff
    if beta_cutoff is not None:
        print('Beta cutoff')
        delta=time.time() - start_time
        print(f"Move time: {'{:.2f}s'.format(delta)}")
        pool.terminate()
        pool.join()
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
    
    print(f"Best move @ depth {res_depth}")
    '''
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
