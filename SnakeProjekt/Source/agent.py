from gameobjects import GameObject
from move import Move
from asyncio.queues import PriorityQueue, Queue
from move import Direction
from tkinter.constants import CURRENT


class Agent:
    
    current = None
    path = Queue()
    foodq = Queue()
    
    def find_food(self, board):    
        self.foodq = Queue()    
        # find food on map
        x = 0
        y = 0
        while x < (len(board)):
            y = 0
            while y < (len(board)):
                if (board[x][y] == GameObject.FOOD):
                    self.foodq.put_nowait((x, y))
                y = y + 1
            x = x + 1
            
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
        # current iteration of astar
        i = 0
        
        # set of evaluated nodes
        closed = set()
        
        # the set of discovered nodes
        # initially only contains the start current
        open = set()
        
        # backtracking map
        cameFrom = {}
        # f-values
        fscore = {}
        # g-values
        gscore = {}
        
        # add start to openlist
        open.add(start)
        gscore[start] = 0
        fscore[start] = self.cost_estimate(start)
        
        # search
        while len(open) > 0:
            
            current = self.get_node_lowest_fscore(open, fscore)
            x, y = current
        
            # check if goal
            if board[x][y] == GameObject.FOOD:
                self.reconstruct_path(cameFrom, current)
                return
            
            # remove from open nodes
            open.discard(current)
            # add to closed nodes
            closed.add(current)
            
            # get neighbours
            neighbours = self.get_neighbours(current, direction, board, gscore[current])
            for neighbour in neighbours._queue:
                # skip if current is already closed
                if neighbour in closed:
                    continue
                
                # check if valid field
                x, y = neighbour
                if board[x][y] == GameObject.EMPTY or board[x][y] == GameObject.FOOD:
                    # add to openlist if first discovered
                    if neighbour not in open and neighbour not in closed:
                        gscore[neighbour] = gscore[current] + 1
                        fscore[neighbour] = pow(self.cost_estimate(neighbour), 2) + pow(gscore[neighbour], 2)
                        open.add(neighbour)
                        cameFrom[neighbour] = current
                        
        return "failure"
            
    def get_node_lowest_fscore(self, openSet, fscore):
        min = 9999999999 
        minNode = None
        for node in openSet:
            if fscore[node] < min:
                minNode = node
                min = fscore[node]
                
        return minNode
        
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
            self.path.put_nowait(store.pop())
        
    def cost_estimate(self, node):
        res = 100000
        node_x, node_y = node
        for val in self.foodq._queue:
            x, y = val
            x = node_x - x
            y = node_y - y
            if (x < 0):
                x = x * -1
            if (y < 0):
                y = y * -1
            if (x + y < res):
                res = x + y
        return res;
    
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
        reaches 1 and there is not eaten the next turn, the snake dies. If the value is equal to -1, then the option
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
        
        if (turns_alive == 0):
            self.current = self.find_pos(board)
        
        if (True or self.path.empty()):
            self.find_food(board)
            
            self.path = Queue()
            
            self.astar_search(board, self.current, direction)
    
        # temp failsafe
        if (self.path.empty()):
            return Move.STRAIGHT
        
        next = self.path.get_nowait()
        # get individuals for comparison
        next_x, next_y = next
        x, y = self.current
        # update current pos for next turn
        self.current = next
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

    def on_die(self):
        """This function will be called whenever the snake dies. After its dead the snake will be reincarnated into a
        new snake and its life will start over. This means that the next time the get_move function is called,
        it will be called for a fresh snake. Use this function to clean up variables specific to the life of a single
        snake or to host a funeral.
        """
        pass
