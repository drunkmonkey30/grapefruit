# player class

class Player:
    def __init__(self, name, position, level):
        self.name = name
        self.position = position
        self.level = level
        self.total_questions = 0
        self.total_correct = 0
        self.furthest_path = 0


    # set position of player to specific tile
    def set_position(self, tile_num):
        self.position = tile_num


    def inc_correct(self):
        self.total_correct += 1


    def inc_questions(self):
        self.total_questions += 1


    def clear_question_totals(self):
        self.total_questions = 0
        self.total_correct = 0


    def clear_furthest_path(self):
        self.furthest_path = 0


    def inc_furthest_path(self):
        self.furthest_path += 1