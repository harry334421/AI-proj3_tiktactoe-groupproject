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
            func_type, data = input_queue.get()
            if func_type==1:
                i, j, board, is_maximizing, target, max_depth, alpha, beta, last_moves, evaluator = data
                #print(f"Get Data for Move @ ({i,j} @ Depth {max_depth})")
                board[i][j] = 1 if is_maximizing else -1
                score = ttt.minmax(board, 0, i, j, not is_maximizing, target, alpha, beta, max_depth, last_moves, evaluator)
                board[i][j] = 0
                #print(f"Scoring: {(i, j, max_depth, score)}")
                result_queue.put((func_type, (i, j, max_depth, score)))
            elif func_type==2:
                board, target, is_maximizing, i, j = data
                player_winning_move, opponent_winning_move = ttt.pattern_check(board, target, is_maximizing, i, j)
                result_queue.put((func_type, (player_winning_move, opponent_winning_move)))
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
    player_winning_move = {0:(-1,-1), 1:[], 2:[], 3:[], 4:[]}
    opponent_winning_move = {0: (-1,-1), 1:[], 2:[], 3:[], 4:[]}
    '''
    Start the asychronized processes early on to save time 
    '''
    #Queue Setup
    m=Manager()
    iqueue=m.Queue(maxsize=2)
    rqueue=m.Queue()
    #Dispatch Workers
    pool=Pool(cpu)
    pool_tuple=[(iqueue, rqueue) for _ in range(cpu)]
    pool.starmap_async(move_worker, pool_tuple)
    
    #print(possible_moves)
    #Get Possible Moves
    possible_moves=ttt.get_possible_moves(board)
    
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
    
    #Rank Possible Moves 
    ranked_moves=ttt.rank_moves(possible_moves, last_moves)
    
    
    '''
    Back to Pattern Checking while the async processes is starting 
    '''
    #Check Winning and Blocking Moves
    
    if len(possible_moves)<=len(board)**2-2*target+1:
        res_counter=0
        max_count=len(possible_moves)
        pidx=0
        while True:
            if time.time()-start_time>timeout:
                pool.terminate()
                pool.join()
                break
            try:
                if pidx<max_count:
                    iqueue.put_nowait((2, (board, target, is_maximizing, ranked_moves[pidx][0], ranked_moves[pidx][1])))
                    pidx+=1
            except:
                pass
            try:
                func_type, (tmp_player_winning_move, tmp_opponent_winning_move)=rqueue.get_nowait()
                if tmp_player_winning_move[0]!=(-1,-1):
                    pool.terminate()
                    pool.join()
                    return tmp_player_winning_move[0]
                else:
                    player_winning_move[0]=tmp_player_winning_move[0]
                    opponent_winning_move[0]=tmp_opponent_winning_move[0]
                    for lv in range(1, 5):
                        player_winning_move[lv]+=tmp_player_winning_move[lv]
                        opponent_winning_move[lv]+=tmp_opponent_winning_move[lv]
                res_counter+=1
                if res_counter>=max_count:
                    break
            except:
                pass
    print(f"Time for pattern checking {time.time()-start_time}")
    
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
        if player_winning_move[idx]!=[]:
            delta=time.time() - start_time
            print(f"Move time: {'{:.2f}s'.format(delta)}")
            print(f"Intermediate Winning Move @ Scenario{idx}.")
            pool.terminate()
            pool.join()
            return random.choice(player_winning_move[idx])
        elif opponent_winning_move[idx]!=[]:
            delta=time.time() - start_time
            print(f"Move time: {'{:.2f}s'.format(delta)}")
            print(f"Intermediate Blocking Move @ Scenario {idx}.")
            pool.terminate()
            pool.join()
            return random.choice(opponent_winning_move[idx])
    
    #Start the IDS Process
    #MinMax with Iterative Deepenining
    max_depth=0
    depth_res_count={0:0}
    best_move[max_depth]=[]
    alpha[max_depth]=-float('inf')
    beta[max_depth]=float('inf')
    score_map={0:[[None]*len(board) for _ in range(len(board))]}
    counter=0
    beta_cutoff=None
    idx=0
    skip=False
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
                iqueue.put_nowait((1, (ranked_moves[idx][0], ranked_moves[idx][1], board, is_maximizing, target, max_depth, alpha[max_depth], beta[max_depth], new_last_moves, evaluator)))
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
            func_type, (i, j, depth, score)=rqueue.get_nowait()
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
    #print(max_depth)
    #print(depth_res_count)
    
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
