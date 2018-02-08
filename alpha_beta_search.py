"""Games, or Adversarial Search (Chapter 5)"""

import copy

infinity = float('inf')


def alphabeta_search(state, game):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = game.to_move(state)

    # Functions used by alphabeta
    def max_value(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = -infinity
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = infinity
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alphabeta_cutoff_search:
    best_score = -infinity
    beta = infinity
    best_action = None
    for a in game.actions(state):
        print('a: ')
        print(a)
        v = min_value(game.result(state, a), best_score, beta)
        if v > best_score:
            best_score = v
            best_action = a
    print(v)
    return best_action

# ______________________________________________________________________________
# Some Sample Games


class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))


class Poker(Game):

    def actions(self, state):
        """Return a list of the allowable moves at this point."""

        # state is organized as
        # {'card_sets' : [card_set_0, card_set_1], "moving_side" : 0, "last_ply" : {'card': 7 , 'num' : 2}}

        card_sets = state['card_sets']
        moving_side = state['moving_side']
        last_ply = state['last_ply']

        candidate_set = card_sets[moving_side]
        last_card = last_ply['card']
        last_num = last_ply['num']

        possible_move = []

        if last_card:
            # the last ply is real card
            for i in range(last_card + 1, len(candidate_set) ):
                diff_num = candidate_set[i] - last_num
                if diff_num >= 0:
                    possible_move.append({'card' : i, 'num' : last_num})

            # pass if we do not have anythin bigger than that
            # note that sometimes we want to pass even if we can beat it
            # later refine this
            if len(possible_move) == 0:
                possible_move.append({'card' : None, 'num' : 0})

        else:
            # the opponent past the last round, and we play whatever we want
            for i in range(len(candidate_set)):
                if candidate_set[i] > 0:
                    for j in range(1, candidate_set[i] + 1):
                        possible_move.append({'card' : i, 'num' : j})

        # print('state: ')
        # print(state)
        # print(possible_move)
        # print('\n')
        return possible_move


    def result(self, state, move):
        """Return the state that results from making a move from a state."""

        new_state = copy.deepcopy(state)
        card_sets = new_state['card_sets']
        moving_side = new_state['moving_side']
        last_ply = new_state['last_ply']

        # make a copy; otherwise it is still linked
        changed_set = card_sets[moving_side]
        changed_card = move['card']
        changed_num = move['num']

        # reduce the number of cards
        if changed_card != None:
            changed_set[changed_card] -= changed_num

        # change the moving side
        if moving_side == 1:
            moving_side = 0
        else:
            moving_side = 1

        # mark the new last_ply
        last_ply = move

        new_state = {'card_sets' : card_sets, 'moving_side' : moving_side, 'last_ply' : last_ply}
        # print('new_state: ')
        # print(new_state)
        return new_state

    def utility(self, state, player):
        """Return the value of this final state to player."""
        # note this is related to how to find the best moves of the loser
        # moving_side is the side to move
        # if it is already a terminal state when you are moving_side
        # if meanns the other people wins
        # a little bit tricky and intuitive here; be CRREFUL
        if player != state['moving_side']:
            return 1
        else:
            return -1

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        # return not self.actions(state)
        card_sets = state['card_sets']
        for card_set in card_sets:
            if sum(card_set) == 0:
                # print(state)
                # print('terminal_test')
                return True


        return False

    def to_move(self, state):
        return state['moving_side']


class Fig52Game(Game):
    """The game represented in [Figure 5.2]. Serves as a simple test case."""

    succs = dict(A=dict(a1='B', a2='C', a3='D'),
                 B=dict(b1='B1', b2='B2', b3='B3'),
                 C=dict(c1='C1', c2='C2', c3='C3'),
                 D=dict(d1='D1', d2='D2', d3='D3'))
    utils = dict(B1=2, B2=12, B3=8, C1=3, C2=4, C3=6, D1=14, D2=5, D3=2)
    initial = 'A'

    def actions(self, state):
        return list(self.succs.get(state, {}).keys())

    def result(self, state, move):
        return self.succs[state][move]

    def utility(self, state, player):
        if player == 'MAX':
            return self.utils[state]
        else:
            return -self.utils[state]

    def terminal_test(self, state):
        return state not in ('A', 'B', 'C', 'D')

    def to_move(self, state):
        return 'MIN' if state in 'BCD' else 'MAX'

    # def display(self, state):
        # print(state)


# game = Fig52Game()
# best_action = alphabeta_search('A', game)
# print(best_action)

game = Poker()
# init_state = {'card_sets' : [[1, 0, 1], [0, 1, 1]], "moving_side" : 0, "last_ply" : {'card': None , 'num' : 0}}
card_sets = [[2, 2, 2, 0, 3, 3, 0, 1], [0, 0, 0, 2, 0, 0, 2, 0]]
init_state = {'card_sets' : card_sets, "moving_side" : 0, "last_ply" : {'card': None , 'num' : 0}}
best_action = alphabeta_search(init_state, game)
print(best_action)
