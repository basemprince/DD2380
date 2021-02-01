#!/usr/bin/env python3
import random
from time import time
import math
from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR

class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()
        self.move_count =0

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate game tree object
        first_msg = self.receiver()
        # Initialize your minimax model
        model = self.initialize_model(initial_data=first_msg)

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)
            #print(msg)
            # Possible next moves: "stay", "left", "right", "up", "down"
            self.move_count +=1
            best_move = self.search_best_next_move(
                model=model, initial_tree_node=node, move_count=self.move_count)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def initialize_model(self, initial_data):
        """
        Initialize your minimax model 
        :param initial_data: Game data for initializing minimax model
        :type initial_data: dict
        :return: Minimax model
        :rtype: object

        Sample initial data:
        { 'fish0': {'score': 11, 'type': 3}, 
          'fish1': {'score': 2, 'type': 1}, 
          ...
          'fish5': {'score': -10, 'type': 4},
          'game_over': False }

        Please note that the number of fishes and their types is not fixed between test cases.
        """
        subdivisions = self.settings.space_subdivisions
        model = minmax_algorithm(initial_data, subdivisions)

        return model

    def search_best_next_move(self, model, initial_tree_node,move_count):
        """
        Use your minimax model to find best possible next move for player 0 (green boat)
        :param model: Minimax model
        :type model: object
        :param initial_tree_node: Initial game tree node 
        :type initial_tree_node: game_tree.Node 
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###
        
        # NOTE: Don't forget to initialize the children of the current node 
        #       with its compute_and_get_children() method!
        
        start_time = time()
        
        #best_possible_move,_= model.minmax_prune(initial_tree_node,start_time)

        best_possible_move,_= model.iterativeDeepening(initial_tree_node,start_time)
  
        print_center(model,move_count)
        model.reset()
    
        return ACTION_TO_STR[best_possible_move]


def print_center(model,move_count):
    print('\n############### move num (', move_count, ') ###############')
    print('max_depth: ',model.deepest, ' elapsed_time: ', (round(model.elapsed_time* 10**3,0)))
    print('############################################')

class minmax_algorithm:
    def __init__(self, initial_data,subdivisions):
        self.initial_data = initial_data
        self.next_children = []
        self.bestPossibleMove = 0
        self.counter = 0
        self.type = 'combination'
        self.target = None
        self.y_check = 0
        self.subdivisions = subdivisions
        self.deepest = 0
        self.hash_t = {}
        self.elapsed_time = 0

    def reset(self):
        self.deepest = 0
        self.elapsed_time = 0


    def hursitic(self,node):
        if self.type == 'score':
            return node.state.player_scores[0]-node.state.player_scores[1]

        if self.type == 'close':
            fish_list = node.state.fish_positions
            #print("fish list length" , len(fish_list))
            fish_score = node.state.fish_scores

            score_diff = node.state.player_scores[0]-node.state.player_scores[1]
            my_hook = node.state.hook_positions[0]
            closest = my_distance = float('inf')

            for key in fish_list:
                fish = fish_list[key]
                fish_s = fish_score[key]

                my_distance1 = ((my_hook[0] - fish[0])**2 + (my_hook[1] - fish [1])**2)
                my_distance2 = ((my_hook[0] - fish[0] + self.subdivisions)**2 + (my_hook[1] - fish [1])**2)
                my_distance3 = ((my_hook[0] - fish[0] - self.subdivisions)**2 + (my_hook[1] - fish [1])**2)
                my_distance = min(my_distance1,my_distance2,my_distance3)

                #check if fish is worth going after, if this fish is the closest, and oponent is not within 1 block
                if fish_s >= 0  and my_distance < closest:
                    self.target = key
                    closest = my_distance   

            final_score = -closest
            return final_score  


        if self.type == 'combination':
            fish_list = node.state.fish_positions
            #print("fish list length" , len(fish_list))
            fish_score = node.state.fish_scores
            caught_check_me = node.state.get_caught()[0]
            caught_check_op = node.state.get_caught()[1]

            my_hook = node.state.hook_positions[0]
            oponent_hook = node.state.hook_positions[1]
            score_diff = node.state.player_scores[0]-node.state.player_scores[1]
            self.y_check = 0
            closest = my_distance = float('inf')
            fish_away_count = 0.0
            
            #print(len(fish_list) == 0 and caught_check_me is not None , "  ",  caught_check_me)
            if len(fish_list) == 0 :
                closest = float('-inf')

            for key in fish_list:
                fish = fish_list[key]
                fish_s = fish_score[key]

                my_distance1 = ((my_hook[0] - fish[0])**2 + (my_hook[1] - fish [1])**2)
                my_distance2 = ((my_hook[0] - fish[0] + self.subdivisions)**2 + (my_hook[1] - fish [1])**2)
                my_distance3 = ((my_hook[0] - fish[0] - self.subdivisions)**2 + (my_hook[1] - fish [1])**2)
                my_distance = min(my_distance1,my_distance2,my_distance3)
                #print(my_distance)
                
                oponent_distance = ((oponent_hook[0] - fish[0])**2 + (oponent_hook[1] - fish [1])**2)

                #check if fish is worth going after, if this fish is the closest, and oponent is not within 1 block
                if fish_s >= 0  and my_distance < closest  and caught_check_op != key:
                    self.target = key
                    if math.sqrt(oponent_distance) > math.sqrt(my_distance):
                        closest = my_distance / oponent_distance
                    else:
                        closest = my_distance   

                #check how many fish are on other side
                if fish[0] > oponent_hook[0] and oponent_hook[0] > my_hook[0]:
                    fish_away_count += 1
                if fish[1] > my_hook[1]:
                    self.y_check += 1

            percent_away = fish_away_count / len(fish_list) if len(fish_list) !=0 else 1

            #move ship to the other side if remaning fish are there
            if percent_away >= 0.99 and node.move == 3:
                closest = float('-inf')
            try:
                final_score = -closest   + fish_score[self.target] + score_diff
            except:
                final_score = -closest + score_diff

            return final_score  

    def illegal_moves(self,CurrentNode,child):
        #print(self.y_check)
        illegal = False
        # if CurrentNode.state.hook_positions[1][0] - CurrentNode.state.hook_positions[0][0] == 1 and child.move == 4:
        #     illegal = True
        # elif CurrentNode.state.hook_positions[0][0] - CurrentNode.state.hook_positions[1][0] == 1 and child.move == 3:
        #     illegal = True
        # if self.y_check == 0 and child.move == 1:
        #     illegal = True
        return illegal

    def minmax_prune(self,CurrentNode,start_time,alpha=float('-inf'),beta=float('inf')):
        self.elapsed_time = time() - start_time
        next_children = CurrentNode.compute_and_get_children()
        hash_key = str (CurrentNode.depth)  + str(CurrentNode.state.player_scores)  + str(CurrentNode.state.hook_positions)
        
        if hash_key in self.hash_t:
            return self.hash_t[hash_key]

        
        if CurrentNode.depth > self.deepest: self.deepest = CurrentNode.depth

        if next_children is None   or self.elapsed_time >= 10*1e-3: #
            huristic = self.hursitic(CurrentNode)
            #print("hurisitic:" ,huristic, "depth:", CurrentNode.depth, "move:",  ACTION_TO_STR[CurrentNode.move])
            return  CurrentNode.move, huristic

        else:
            current_player = CurrentNode.state.player
            bestPossible = float('-inf') if current_player == 0 else float ('inf')

            for child in next_children:
                #print (child.state.hook_positions[0][0] , "   " ,child.state.hook_positions[1][0])
                if self.illegal_moves(child):
                    #print("whatsup")
                    continue

                m, v = self.minmax_prune(child,start_time,alpha,beta)

                if current_player == 0 and v > bestPossible and self.target != None:  #if max turn
                    bestPossible = v
                    self.bestPossibleMove = child.move
                    alpha = max(alpha,bestPossible)

                elif current_player == 1 and v < bestPossible and self.target != None: # if min turn
                    bestPossible = v
                    self.bestPossibleMove = child.move
                    beta = min(beta,bestPossible)

                if beta <= alpha:
                    break

            self.hash_t[hash_key] = self.bestPossibleMove, bestPossible
            return  self.bestPossibleMove, bestPossible

    def minmax_prune_IDS(self,CurrentNode,depth,alpha,beta,start_time):
        self.elapsed_time = time() - start_time
        next_children = CurrentNode.compute_and_get_children()

        hash_key = str (CurrentNode.depth)  + str(CurrentNode.state.player_scores)  + str(CurrentNode.state.hook_positions)
        
        if hash_key in self.hash_t:
            return self.hash_t[hash_key]

        if CurrentNode.depth > self.deepest: self.deepest = CurrentNode.depth
        if next_children is None or CurrentNode.depth >= depth or self.elapsed_time >= 55*1e-3:
            huristic = self.hursitic(CurrentNode)
            #print("hurisitic:" ,huristic, "depth:", CurrentNode.depth, "move:",  ACTION_TO_STR[CurrentNode.move])
            return  CurrentNode.move, huristic
        else:
            current_player = CurrentNode.state.player
            bestPossible = float('-inf') if current_player == 0 else float ('inf')
            for child in next_children:
                #print (child.state.hook_positions[0][0] , "   " ,child.state.hook_positions[1][0])
                if self.illegal_moves(CurrentNode,child):
                    #print("whatsup")
                    continue

                m, v = self.minmax_prune_IDS(child,depth,alpha,beta,start_time)

                if current_player == 0 and v > bestPossible and self.target != None:  #if max turn
                    bestPossible = v
                    self.bestPossibleMove = child.move
                    alpha = max(alpha,bestPossible)

                elif current_player == 1 and v < bestPossible and self.target != None: # if min turn
                    bestPossible = v
                    self.bestPossibleMove = child.move
                    beta = min(beta,bestPossible)

                if beta <= alpha:
                    break
            
            self.hash_t[hash_key] = self.bestPossibleMove, bestPossible
            return  self.bestPossibleMove, bestPossible

    def iterativeDeepening (self,CurrentNode,start_time):     
        next_children = CurrentNode.compute_and_get_children()
        allowedDepth = 50
        bestPossible = float('-inf')
        self.deepest = 0

        for depth in range (1,allowedDepth+1): #while elapsed_time <= 8*1e-3:

            self.hash_t.clear()

            alpha=float('-inf')
            beta=float('inf')     
            if depth > self.deepest: self.deepest = depth
            for child in next_children:
                m, v = self.minmax_prune_IDS(child,depth,alpha,beta,start_time)
                if v > bestPossible:
                    bestPossible, self.bestPossibleMove = v, child.move

        #print('hash_table: ' , len(self.hash_t))
        return  self.bestPossibleMove, bestPossible