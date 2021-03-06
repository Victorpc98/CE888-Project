from src.uct import OXOState,OthelloState,NimState,UCT
import pandas as pd
import csv
from itertools import product
import random
import time
class DataCollector():

    def __init__(self,args):
        self.args = args
        self.game_to_play = args.game
        self.othello_size = args.othelloBoardSize
        self.nim_chips = args.nimChips
        self.games = {
            "oxo" : {
                "object" : OXOState,
                "rows" : ["Step","Cell_0","Cell_1", "Cell_2","Cell_3","Cell_4","Cell_5","Cell_6","Cell_7","Cell_8","Move","Agent"],
                "arguments" : False
            },
            "othello" : {
                "object" : OthelloState,
                "rows" : ["Step"] + ["Cell_"+str(x)+"_"+str(y) for x,y in product([ i%self.othello_size for i in range(self.othello_size)],[ i%self.othello_size for i in range(self.othello_size)])] + ["Move","Agent"],
                "arguments" : True,
                "args" : {"sz" : self.othello_size}
            },
            "nim" : {
                "object" : NimState,
                "rows" : ["Step","Chips","Move","Agent"],
                "arguments" : True,
                "args" : {"ch" : self.nim_chips}
            }
        }

    def collect(self,iteration,games=1,classifier=None):
        self.wins = {"0":0,"1":0,"2":0}
        first = True
        start_time = time.time()
        for i in range(games):
            if first:
                res = pd.DataFrame(self.dump(self.play(i,classifier,iteration)),columns=self.games[self.game_to_play]["rows"])
                first = False
            else:
                a = pd.DataFrame(self.dump(self.play(i,classifier,iteration)),columns=self.games[self.game_to_play]["rows"])
                res = pd.concat([res,a],ignore_index=True)

            if self.args.verbose: print("[INFO] Iteration {0}/{1} : Simulating {2} Games ... ({3}% Completed) ".format(iteration,self.args.iterations,self.args.ngames,round((i/games)*100,4)),end="\r", flush=True)
        
        print("[INFO] {0}Iteration {1}/{2} : Completed simulation for {3} Games in {4} seconds. Agent 1 wins {5} games. Agent 2 wins {6} games.".format("\033[K",iteration,self.args.iterations,self.args.ngames,round(time.time()-start_time,2),self.wins["1"],self.wins["2"]))
        return res,self.wins

    def play(self,n,classifier,iteration):
        if self.games[self.game_to_play]["arguments"]:
            state = self.games[self.game_to_play]["object"](**self.games[self.game_to_play]["args"])
        else:
            state = self.games[self.game_to_play]["object"]()
        game = []
        step = 0
        while (state.GetMoves() != []):
            
            if not classifier:
                if state.playerJustMoved == 1:
                    m = UCT(rootstate = state, itermax = 100, verbose = False) # play with values for itermax and verbose = True
                else:
                    m = UCT(rootstate = state, itermax = 100, verbose = False)
  
            if classifier:
                if state.playerJustMoved == 2 and self.args.agent2 == "mcts":
                    m = UCT(rootstate = state, itermax = 100, verbose = False) # play with values for itermax and verbose = True
                elif state.playerJustMoved == 1 and self.args.agent1 == "mcts":
                    m = UCT(rootstate = state, itermax = 100, verbose = False) # play with values for itermax and verbose = True
                else:
                    if random.randrange(10) == 0:
                        m = random.choice(state.GetMoves())
                    else:
                        if self.game_to_play in ["oxo","othello"]:
                            board = []
                            if self.game_to_play == "oxo":
                                board = state.board
                            elif self.game_to_play == "othello":
                                for l in state.board:
                                    for i in l:
                                        board.append(i)
                            m = classifier.predict([[step] + board + [3 - state.playerJustMoved]])
                            m = (str(m)[0],str(m)[1]) if len(str(m)) == 2 else (m,0)
                        elif self.game_to_play == "nim":
                            m = classifier.predict([[step] + [state.chips] + [3 - state.playerJustMoved]])
                        
                        if m not in state.GetMoves():
                            m = random.choice(state.GetMoves())

            if self.game_to_play in ["oxo","othello"]:
                game.append(
                    {
                        "step" : step,
                        "board" : state.Clone(),
                        "move" : m,
                        "agent" : 3 - state.playerJustMoved,
                    }
                )
            else:
                game.append(
                    {
                        "step" : step,
                        "chips" : state.chips,
                        "move" : m,
                        "agent" : 3 - state.playerJustMoved,
                    }
                )

            step += 1
            state.DoMove(m)
        
        if state.GetResult(state.playerJustMoved) == 1.0:
            self.wins[str(state.playerJustMoved)] +=1 
        elif state.GetResult(state.playerJustMoved) == 0.0:
            self.wins[str(3 - state.playerJustMoved)] +=1 
        else: 
            self.wins["0"] +=1 

        return game

    def dump(self,game):
        res = []
        for state in game:
            if self.game_to_play == "oxo":
                board = state["board"].board
                move = [state["move"]]
            elif self.game_to_play == "othello":
                board = []
                for l in state["board"].board:
                    for i in l:
                        board.append(i)
                move = [ str(state["move"][0]) + str(state["move"][1]) ]
            else:
                board = [state["chips"]]
                move = [state["move"]]

            res.append([state["step"]] + board + move + [state["agent"]])
        return res
