import math

class Block:
    def __init__(self):
        self.positions = []
        # self.start = start
        # self.end = end

    def append(self, position):
        self.positions.append(position)

    

class PositionCollector:
    def __init__(self, max_distance):
        self.blocks = []
        self.max_distance = max_distance

    def add(self, position):
        self.blocks[-1].append(position)

    def new_block(self):
        self.blocks.append(Block())
    
    def print(self):
        for b in self.blocks:
            print(b.__dict__)

    def correct_position(self) -> (int, int):
        if len(self.blocks[-1].positions) == 1:
            return self.blocks[-1].positions[0]
        prev = self.blocks[-1].positions[-2]
        current = self.blocks[-1].positions[-1]
        opposite_side = current[1] - prev[1]
        next_side = current[0] - prev[0]

        if math.sqrt(opposite_side ** 2 + next_side ** 2) <= self.max_distance:
            return self.blocks[-1].positions[-1]

        if next_side == 0:
            self.blocks[-1].positions[-1] = (current[0], int(prev[1] + signum(current[1] - prev[1]) * self.max_distance))
            return self.blocks[-1].positions[-1]

        degree = math.atan(opposite_side/next_side)
        new_x = prev[0] + abs(math.cos(degree)) * self.max_distance * signum(current[0] - prev[0])
        new_y = prev[1] + abs(math.sin(degree)) * self.max_distance * signum(current[1] - prev[1])
        self.blocks[-1].positions[-1] = (int(new_x), int(new_y))
        return self.blocks[-1].positions[-1]

    def get_current(self):
        if len(self.blocks[-1].positions) == 0:
            return (-1, -1)
        return self.blocks[-1].positions[-1]

    def is_empty_block(self):
        return len(self.blocks[-1].positions) == 0
        
    
# def parity(value, subtrahend):
#     if value - subtrahend >= 0:
#         return 1
#     return -1

def signum(int):
    if(int < 0): return -1
    elif(int > 0): return 1
    else: return int

# c = PositionCollector(10)
# c.new_block()
# c.add((11,16))
# c.add((2,1))
# print(c.correct_position())