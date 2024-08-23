from parsing.stacknode import StackNode
from parsing.enums.token_type import TokenType
import random

class Compute:
    def __init__(self):
        self.i = 0
        self.cocked_rolls = []
        self.all_lists_of_rolls = []
        self.list_of_dice = []
        self.error = False
        self.cocked_odds = 0.025
    
    def roll_die(self, to_roll):
        num_rolls = int(to_roll[:to_roll.index('d')]) if to_roll[:to_roll.index('d')] != '' else 1
        num_sides = int(to_roll[to_roll.index('d')+1:])
        if num_rolls > 1000 or num_rolls > 10000:
            self.error = True
            return 0
        rolled_total = 0
        list_of_rolls = []
        for i in range(num_rolls):
            self.i += 1
            if random.random() < self.cocked_odds:
                self.cocked_rolls.append((random.randint(1, num_sides), self.i))
            roll = random.randint(1, num_sides)
            list_of_rolls.append(roll)
            rolled_total += roll
        self.all_lists_of_rolls.append(list_of_rolls)
        roll_avg = int((1+num_sides)/2*num_rolls)
        self.list_of_dice.append(str(num_rolls) + 'd' + str(num_sides))
        return (rolled_total, roll_avg)
    
    def roll_exploding_die(self, to_roll):
        num_rolls = int(to_roll[:to_roll.index('e')]) if to_roll[:to_roll.index('e')] != '' else 1
        num_sides = int(to_roll[to_roll.index('e')+1:])
        if num_rolls > 1000 or num_sides > 10000:
            self.error = True
            return 0
        rolled_total = 0
        list_of_rolls = []
        for i in range(num_rolls):
            roll = 0
            while(True):
                self.i += 1
                if random.random() < self.cocked_odds:
                    self.cocked_rolls.append((random.randint(1, num_sides), self.i))
                roll = random.randint(1, num_sides)
                rolled_total += roll
                list_of_rolls.append(roll)
                if roll != num_sides or num_sides == 1:
                    break
        roll_avg = 0
        for i in range(num_sides):
            roll_avg += (i + 1)
        roll_avg = int(roll_avg/(num_sides-1)*num_rolls)
        self.all_lists_of_rolls.append(list_of_rolls)
        return (rolled_total, roll_avg)
    
    def compute_expr(self, reduced_expr: StackNode):
        if reduced_expr.oper == TokenType.PLUS:
            res_left = self.compute_expr(reduced_expr.left)
            left_expr = (res_left[0], res_left[1])
            res_right = self.compute_expr(reduced_expr.right)
            right_expr = (res_right[0], res_right[1])
            return (left_expr[0] + right_expr[0], left_expr[1] + right_expr[1])
        elif reduced_expr.oper == TokenType.MINUS:
            res_left = self.compute_expr(reduced_expr.left)
            left_expr = (res_left[0], res_left[1])
            res_right = self.compute_expr(reduced_expr.right)
            right_expr = (res_right[0], res_right[1])
            return (left_expr[0] - right_expr[0], left_expr[1] - right_expr[1])
        elif reduced_expr.oper == TokenType.MULT:
            res_left = self.compute_expr(reduced_expr.left)
            left_expr = (res_left[0], res_left[1])
            res_right = self.compute_expr(reduced_expr.right)
            right_expr = (res_right[0], res_right[1])
            return (left_expr[0] * right_expr[0], left_expr[1] * right_expr[1])
        elif reduced_expr.oper == TokenType.DIV:
            res_left = self.compute_expr(reduced_expr.left)
            left_expr = (res_left[0], res_left[1])
            res_right = self.compute_expr(reduced_expr.right)
            right_expr = (res_right[0], res_right[1])
            if right_expr[0] == 0:
                self.error = True
                return 0
            return (int(left_expr[0] / right_expr[0]), int(left_expr[1] / right_expr[1]))
        elif reduced_expr.token_info.TokenType == TokenType.ERROR:
            self.error = True
            return 0
        elif 'd' in reduced_expr.token_info.lexeme:
            to_roll = reduced_expr.token_info.lexeme
            res = self.roll_die(to_roll)
            return (res[0], res[1])
        elif 'e' in reduced_expr.token_info.lexeme:
            to_roll = reduced_expr.token_info.lexeme
            res = self.roll_exploding_die(to_roll)
            return (res[0], res[1])
        else:
            num = int(reduced_expr.token_info.lexeme)
            return (num, num)