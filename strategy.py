# Copyright (c) 2013 Craig Dodd <github@craigdodd.co.uk>
#
# This file is part of the "Prisoner's Dilemma Simulator" application.
#
# The "Prisoner's Dilemma Simulator" is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

"""Module containing Prisoner's Dilemma strategy classes."""

# Standard library modules
import random

# Define the values for cooperation and defection
COOP = False
DEFECT = True

class Player(object):
    def __init__(self, strategy):
        self.strategy = strategy
        self.reset()

    def reset(self):
        self.total_payoff = 0
        self.players_played = []

    def move(self, game):
        return self.strategy.move(self, game)

    def record(self, game):
        # Save the opponent for future reference
        opponent = game.get_opponent(self)
        if opponent not in self.players_played:
            self.players_played.append(opponent)

        # Add the game score to the total payoff
        self.total_payoff += game.payoff_dict[self]

    def evolve(self):
        # Get the top scoring strategies of all opponents that have previously
        # been played.
        top_strategies = [self.strategy]
        top_payoff = self.total_payoff

        for opponent in self.players_played:
            payoff = opponent.total_payoff
            if payoff > top_payoff:
                top_payoff = payoff
                top_strategies = [opponent.strategy]
            elif payoff == top_payoff:
                top_strategies.append(opponent.strategy)

        # Randomly "adopt" one of the top strategies
        self.strategy = random.choice(top_strategies)


class CDIStrategy(object):
    def __init__(self, c=0.5, d=0.5, i=0.5):
        self.c = c
        self.d = d
        self.i = i
        self.name = 'CDI (%s/%s/%s)' % (c, d, i)

    def move(self, player, game):
        # Get the opponent's last move
        try:
            last_move = game.get_opponent_move(player, -1)
        except IndexError:
            last_move = None

        # Respond to opponent's last move
        if last_move is None:
            p_defect = self.i
        elif last_move == COOP:
            p_defect = self.c
        elif last_move == DEFECT:
            p_defect = self.d
        else:
            raise ValueError()

        if random.uniform(0, 1) < p_defect:
            return DEFECT
        else:
            return COOP