# Local application modules
from strategy import COOP, DEFECT

class SimpleGame(object):

    # Define the pay payoffs
    REWARD = 3
    STEAL = 5
    LOSE = 0
    PUNISH = 1

    def __init__(self, player1, player2):

        # Save the players as instance variables
        self.player1 = player1
        self.player2 = player2

        # Create lists to store player moves
        self.player1_moves = []
        self.player2_moves = []

        # Create a mapping of a player to an opponent (Giving the opponent
        # instance and move history as a Tuple)
        self.opponents = {
            player1: (player2, self.player2_moves),
            player2: (player1, self.player1_moves),
        }

    def run(self, iterations=4):

        # Play the specified number of iterations and track the players moves
        for iteration in range(iterations):
            self.player1_moves.append(self.player1.move(self))
            self.player2_moves.append(self.player2.move(self))

        # Calculate the scores
        player1_score = 0
        player2_score = 0

        # Merge both players move histories into a 2D list.
        merged_moves = zip(self.player1_moves, self.player2_moves)

        for player1_move, player2_move in merged_moves:

            # Both players Cooperate
            if player1_move == COOP and player2_move == COOP:
                player1_score += self.REWARD
                player2_score += self.REWARD

            # Player 1 cooperates, Player 2 defects
            elif player1_move == COOP and player2_move == DEFECT:
                player1_score += self.LOSE
                player2_score += self.STEAL

            # Player 1 defects, Player 2 cooperates
            elif player1_move == DEFECT and player2_move == COOP:
                player1_score += self.STEAL
                player2_score += self.LOSE

            # Both players defect
            elif player1_move == DEFECT and player2_move == DEFECT:
                player1_score += self.PUNISH
                player2_score += self.PUNISH
            else:
                raise ValueError('One of the players did not return COOP or DEFECT.')

        # Return a mapping of each player to its mean payoff for the game
        self.payoff_dict = {self.player1: float(player1_score) / len(merged_moves),
                            self.player2: float(player2_score) / len(merged_moves)}

        # Prompt the players to record the game
        self.player1.record(self)
        self.player2.record(self)

    def get_opponent_move(self, player, index):
        """Returns the last move for the given player."""
        move_list = self.opponents[player][1]

        if not move_list:
            return None
        else:
            return move_list[index]

    def get_opponent(self, player):
        return self.opponents[player][0]
