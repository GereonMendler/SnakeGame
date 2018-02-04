from gameobjects import GameObject
from move import Move
from asyncio.queues import Queue
from move import Direction
from datetime import datetime


class Agent:
    
    current = None
    path = []
    foods = set()
    altPath = False
    count = 0
    
    def find_food(self, board, thr):    
        self.foods.clear()    
        # find food on map
        x = 0
        y = 0
        while x < (len(board)):
            y = 0
            while y < (len(board)):
                if board[x][y] == GameObject.FOOD:
                    if (self.good_food(board, (x, y), 2) 
                    or self.manhatten_distance((x, y), self.current) <= 1):
                        self.foods.add((x, y))
                y = y + 1
            x = x + 1
        if len(self.foods) == 0:
            self.find_food(board, thr - 1)
    
    def good_food(self, board, food, thr):
        x, y = food
        empty = 0
        if x < len(board) - 1:
            if board[x + 1][y] == GameObject.EMPTY or board[x + 1][y] == GameObject.FOOD:
                empty += 1
        if x > 0:
            if board[x - 1][y] == GameObject.EMPTY or board[x - 1][y] == GameObject.FOOD:
                empty += 1
        if y < len(board) - 1:
            if board[x][y + 1] == GameObject.EMPTY or board[x][y + 1] == GameObject.FOOD:
                empty += 1
        if y > 0:
            if board[x][y - 1] == GameObject.EMPTY or board[x][y - 1] == GameObject.FOOD:
                empty += 1   
        
        return empty >= thr
            
    def find_pos (self, board):
        # find food on map
        x = 0
        y = 0
        while x < (len(board)):
            y = 0
            while y < (len(board)):
                if (board[x][y] == GameObject.SNAKE_HEAD):
                    return (x, y)
                y = y + 1
            x = x + 1
            
    def astar_search(self, board, start, direction):
        self.altPath = False        
        # set of evaluated nodes
        closedSet = set()
        
        # the set of discovered nodes
        # initially only contains the start current
        openSet = set()
        
        # backtracking map
        cameFrom = {}
        # f-values
        fscore = {}
        # g-values
        gscore = {}
        
        # add start to openlist
        openSet.add(start)
        gscore[start] = 0
        fscore[start] = self.cost_estimate(start)
        
        # search
        while len(openSet) > 0:
            
            current = self.get_node_lowest_fscore(openSet, fscore)
            x, y = current
        
            # check if goal
            if current in self.foods:
                self.reconstruct_path(cameFrom, current)
                return
            
            # remove from openSet nodes
            openSet.discard(current)
            # add to closedSet nodes
            closedSet.add(current)
            
            # get neighbours
            neighbours = self.get_neighbours(current, direction, board, gscore[current])
            for neighbour in neighbours._queue:
                # skip if current is already closedSet
                if neighbour in closedSet:
                    continue
                
                # check if valid field
                x, y = neighbour
                if board[x][y] == GameObject.EMPTY or board[x][y] == GameObject.FOOD:
                    # add to openlist if first discovered
                    if neighbour not in openSet and neighbour not in closedSet:
                        gscore[neighbour] = gscore[current] + 1
                        fscore[neighbour] = pow(self.cost_estimate(neighbour), 2) + pow(gscore[neighbour], 2)
                        openSet.add(neighbour)
                        cameFrom[neighbour] = current
        
        altGoal = self.get_node_highest_gscore(closedSet, gscore)
        self.reconstruct_path(cameFrom, altGoal)
        self.altPath = True
        return "failure"
            
    def get_node_lowest_fscore(self, openSet, fscore):
        minVal = 9999999999 
        minNode = None
        for node in openSet:
            if fscore[node] < minVal:
                minNode = node
                minVal = fscore[node]
                
        return minNode
        
    def get_node_highest_gscore(self, closedSet, gscore):
        maxVal = 0 
        maxNode = None
        for node in closedSet:
            if gscore[node] > maxVal:
                maxNode = node
                maxVal = gscore[node]
                
        return maxNode
    
    def get_neighbours(self, node, direction, board, g):
        successors = Queue()
        x, y = node

        if (g == 0):
            if (x != 0 and direction != Direction.EAST):
                successors.put_nowait((x - 1, y))
            if (x != len(board) - 1 and direction != Direction.WEST):
                successors.put_nowait((x + 1, y))
            if (y != 0 and direction != Direction.SOUTH):
                successors.put_nowait((x, y - 1))
            if (y != len(board) - 1 and direction != Direction.NORTH):
                successors.put_nowait((x, y + 1))
        else:
            if (x != 0):
                successors.put_nowait((x - 1, y))
            if (x != len(board) - 1):
                successors.put_nowait((x + 1, y))
            if (y != 0):
                successors.put_nowait((x, y - 1))
            if (y != len(board) - 1):
                successors.put_nowait((x, y + 1))
                
        return successors
        
    def reconstruct_path(self, cameFrom, goal):
        store = []
        current = goal
        while (cameFrom.__contains__(current)):
            store.append(current)
            current = cameFrom.__getitem__(current)
        while (len(store) != 0):
            self.path.append(store.pop())
        
    def cost_estimate(self, node):
        res = 100000
        for food in self.foods:
            distance = self.manhatten_distance(node, food)
            if (distance < res):
                res = distance
        return res;
    
    def manhatten_distance(self, a, b):
        x1, y1 = a
        x2, y2 = b
        x = x1 - x2
        y = y1 - y2
        if (x < 0):
            x = x * -1
        if (y < 0):
            y = y * -1
        return x + y
            
    def get_move(self, board, score, turns_alive, turns_to_starve, direction):
        """This function behaves as the 'brain' of the snake. You only need to change the code in this function for
        the project. Every turn the agent needs to return a move. This move will be executed by the snake. If this
        functions fails to return a valid return (see return), the snake will die (as this confuses its tiny brain
        that much that it will explode). The starting direction of the snake will be North.

        :param board: A two dimensional array representing the current state of the board. The upper left most
        coordinate is equal to (0,0) and each coordinate (x,y) can be accessed by executing board[x][y]. At each
        coordinate a GameObject is present. This can be either GameObject.EMPTY (meaning there is nothing at the
        given coordinate), GameObject.FOOD (meaning there is food at the given coordinate), GameObject.WALL (meaning
        there is a wall at the given coordinate. TIP: do not run into them), GameObject.SNAKE_HEAD (meaning the head
        of the snake is located there) and GameObject.SNAKE_BODY (meaning there is a body part of the snake there.
        TIP: also, do not run into these). The snake will also die when it tries to escape the board (moving out of
        the boundaries of the array)

        :param score: The current score as an integer. Whenever the snake eats, the score will be increased by one.
        When the snake tragically dies (i.e. by running its head into a wall) the score will be reset. In ohter
        words, the score describes the score of the current (alive) worm.

        :param turns_alive: The number of turns (as integer) the current snake is alive.

        :param turns_to_starve: The number of turns left alive (as integer) if the snake does not eat. If this number
        reaches 1 and there is not eaten the nextStep turn, the snake dies. If the value is equal to -1, then the option
        is not enabled and the snake can not starve.

        :param direction: The direction the snake is currently facing. This can be either Direction.NORTH,
        Direction.SOUTH, Direction.WEST, Direction.EAST. For instance, when the snake is facing east and a move
        straight is returned, the snake wil move one cell to the right.

        :return: The move of the snake. This can be either Move.LEFT (meaning going left), Move.STRAIGHT (meaning
        going straight ahead) and Move.RIGHT (meaning going right). The moves are made from the viewpoint of the
        snake. This means the snake keeps track of the direction it is facing (North, South, West and East).
        Move.LEFT and Move.RIGHT changes the direction of the snake. In example, if the snake is facing north and the
        move left is made, the snake will go one block to the left and change its direction to west.
        """
        
        if turns_alive == 0:
            self.current = self.find_pos(board)
            self.timestamp = datetime.now()
            self.count+=1
        
        if True or self.altPath or len(self.path) == 0:
            self.find_food(board, 3)
            
            self.path.clear()
            
            self.astar_search(board, self.current, direction)
    
        # temp failsafe
        if (len(self.path) == 0):
            return Move.STRAIGHT
        
        nextStep = self.path.pop(0)
        # get individuals for comparison
        next_x, next_y = nextStep
        x, y = self.current
        # update current pos for nextStep turn
        self.current = nextStep
        # calc differences
        diffx = x - next_x
        diffy = y - next_y
        # compute which direction
        if (direction == Direction.NORTH):
            if (diffx == 0):
                return Move.STRAIGHT
            if (diffx > 0):
                return Move.LEFT
            else:
                return Move.RIGHT
        if (direction == Direction.EAST):
            if (diffy == 0):
                return Move.STRAIGHT
            if (diffy > 0):
                return Move.LEFT
            else:
                return Move.RIGHT
        if (direction == Direction.SOUTH):
            if (diffx == 0):
                return Move.STRAIGHT
            if (diffx < 0):
                return Move.LEFT
            else:
                return Move.RIGHT
        if (direction == Direction.WEST):
            if (diffy == 0):
                return Move.STRAIGHT
            if (diffy < 0):
                return Move.LEFT
            else:
                return Move.RIGHT

    def on_die(self, score, tics, board):
        """This function will be called whenever the snake dies. After its dead the snake will be reincarnated into a
        new snake and its life will start over. This means that the next time the get_move function is called,
        it will be called for a fresh snake. Use this function to clean up variables specific to the life of a single
        snake or to host a funeral.
        """
        diff = datetime.now() - self.timestamp
        file = open("results.txt","a")
        file.write("{}\t{}\t{}\t{}\t{}\n".format(self.count,len(board),diff.total_seconds(),score,tics))
        print("{}\t{}".format(self.count,diff.total_seconds()))
        pass
