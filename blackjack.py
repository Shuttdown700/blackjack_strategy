
import string
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style
from matplotlib.ticker import PercentFormatter
style.use('ggplot')

class card(object):
    def __init__(self,val,suit):
        self.val = val
        self.suit = suit.lower()
        if val in string.digits[2:]:
            self.num_val = int(val) 
        elif val in 'TJQK':
            self.val.upper()
            self.num_val = 10
        elif val == 'A':
            self.num_val = 11
    def __str__(self):
        return f'{self.val}{self.suit}'

class hand(object):
    def __init__(self):
        self.hand_cards = []
        self.hand_num_val = 0
        self.hard_total = 0
        self.soft_total = False
        self.played = False
        self.bet = -1
        self.split = False
        self.plays = []
    def __str__(self):
        self.calc_val()
        return ', '.join([f'{c.val}{c.suit}' for c in self.hand_cards])+f': {self.hard_total}'
    def add_card(self,c):
        self.hand_cards.append(c)
    def calc_val(self):
        if len(self.hand_cards) == 0: print('no cards'); return 0
        self.hand_num_val = sum([c.num_val for c in self.hand_cards])
        if self.hand_num_val > 21 and self.check_soft_ace():
            # has to check if A has already been accounted for
            for c in self.hand_cards:
                if c.val == 'A' and c.num_val == 11:
                    c.num_val = 1
                    self.calc_val()
            self.hand_num_val = sum([c.num_val for c in self.hand_cards])
        self.hard_total = self.hand_num_val
        if self.check_soft_ace():
            if self.hand_num_val == 21 and len(self.hand_cards) == 2:
                self.soft_total = False
            else:
                self.soft_total = True
        if not self.check_soft_ace():
            self.soft_total = False
    def check_soft_ace(self):
        self.soft_total = 11 in [c.num_val for c in self.hand_cards] and self.hand_num_val not in [20,21]
        return self.soft_total        
    def check_pair(self):
        return len(list(set([c.val for c in self.hand_cards]))) == 1 and len(self.hand_cards) == 2
    def num_cards(self):
        return len(self.hand_cards)
    def clear_hand(self):
        self.hand_cards = []
        self.hand_num_val = 0
        self.hard_total = 0
        self.hard_total = 0
        self.soft_total = False
        self.played = False
    def double_bet(self):
        self.bet *= 2

class deck(object):
    def __init__(self):
        card_types = list(string.digits[2:])+list('TJQKA')
        card_suits = list('schd')
        self.deckStack = [card(ct,cs) for ct in card_types for cs in card_suits]
    def __str__(self):
        return ', '.join([f'{c.val}{c.suit}' for c in self.deckStack])+'\n'
    def shuffle(self):
        random.shuffle(self.deckStack)
    def top(self):
        return self.deckStack[0]
    def top_remove(self):
        self.deckStack = self.deckStack[1:]

class shoe(object):
    def __init__(self,num_decks):
        self.shoe = []
        self.num_decks = num_decks
        for nd in range(num_decks):
            d = deck(); d.shuffle()
            self.shoe += d.deckStack
        self.num_init_cards = 52*num_decks
        self.shoe_depth = 0
    def __str__(self):
        return ', '.join([f'{c.val}{c.suit}' for c in self.shoe])+'\n'
    def shuffle(self):
        random.shuffle(self.shoe)
    def top(self):
        return self.shoe[0]
    def top_remove(self):
        self.shoe = self.shoe[1:]
    def check_shoe(self,penetration):
        self.shoe_depth = 1-((len(self.shoe)/self.num_init_cards))
        # print(f'Shoe Depth = {round(self.shoe_depth*100,2)}%')
        if self.shoe_depth > penetration:
            # print(f'!!!! shuffle at {self.shoe_depth}')
            self.shoe = []
            for nd in range(self.num_decks):
                d = deck(); d.shuffle()
                self.shoe += d.deckStack
            self.shuffle()
            return True
        return False
                
class table(object):
    def __init__(self,num_decks,penetration):
        self.num_decks = num_decks
        self.shoe = shoe(self.num_decks)
        self.dealer_hand = hand()
        self.player_hands = []
        self.dealer_show_card = False
        self.dealer_showdown = True
        self.penetration = penetration
        self.num_dones = 0
        self.shoe_num = 1
        # if self.num_decks == 1:
        #     self.card_count = 0
        # elif self.num_decks == 2:
        #     self.card_count = -4
        # elif self.num_decks == 6:
        #     self.card_count = -20
        # elif self.num_decks == 8:
        #     self.card_count = -28
        self.card_count = 0
        self.real_count = 0
        self.running_count = [0]
        self.running_real_count = [0]
        self.shuffle_points = []
        self.running_player_hands = []
        self.running_dealer_hands = []
        self.running_bets = []
        self.hand_num = 1
        self.hand_num_in_shoe = 1
        self.outcomes = []
        self.no_more_money = False
        self.split_bool = False
        self.money_committed = 0
        self.blackjack_count_tracker = []
        self.shoe.top_remove()
    def __str__(self):
        self.dealer_hand.calc_val()
        stng = 'Player Hands:\n'
        for ph in self.player_hands:
            ph.calc_val()
            stng += f'{ph.hand_num_val}: '+', '.join([f'{c.val}{c.suit}' for c in ph.hand_cards])+'\n'
        stng += '\nDealer Hand:\n'
        stng += f'{self.dealer_hand.hand_num_val}: '+', '.join([f'{c.val}{c.suit}' for c in self.dealer_hand.hand_cards])+'\n'
        return stng
    def spawn_player_hands(self,num_players):
        self.no_more_money = False
        for num_p in range(num_players):
            h = hand()
            self.player_hands.append(h)
    def deal_table(self):
        for ph in self.player_hands:
            c = self.shoe.top(); self.shoe.top_remove()
            ph.add_card(c)
        c = self.shoe.top(); self.shoe.top_remove()
        self.dealer_hand.add_card(c)
        self.dealer_show_card = c
        for ph in self.player_hands:
            c = self.shoe.top(); self.shoe.top_remove()
            ph.add_card(c)
            ph.calc_val()
        c = self.shoe.top(); self.shoe.top_remove()
        self.dealer_hand.add_card(c)
        self.dealer_hand.calc_val()
    def hit_hand(self,h):
        c = self.shoe.top(); self.shoe.top_remove()
        h.add_card(c)
    def split_hand(self,h):
        c1 = h.hand_cards[0]; c2 = h.hand_cards[1]
        h.clear_hand()
        h.add_card(c1)
        h.split = True
        nc1 = self.shoe.top(); self.shoe.top_remove()
        h.add_card(nc1)
        h2 = hand()
        h2.bet = h.bet
        h2.add_card(c2)
        h2.split = True
        nc2 = self.shoe.top(); self.shoe.top_remove()
        h2.add_card(nc2)
        self.player_hands.append(h2)
        for ph in self.player_hands:
            ph.calc_val()
        self.money_committed += h.bet
    def check_bust(self,h):
        h.calc_val()
        return h.hard_total > 21
    def check_blackjack(self,h):
        h.calc_val()
        return  h.hard_total == 21 and len(h.hand_cards) == 2 and h.split == False
    def shoe_stats(self):
        num_cards = len(self.shoe.shoe)
        num_decks = round(num_cards/52,2)
        depth = round((1-(num_cards/(52*self.num_decks)))*100,2)
        return f'{num_cards} cards; {num_decks} decks ({depth}% depth)'
    def clear_dealer_hand(self):
        self.dealer_show_card = False
        self.dealer_showdown = False
        self.dealer_hand.clear_hand()
    def clear_player_hands(self):
        self.player_hands = []
        self.num_dones = 0
        self.hand_num += 1
        self.hand_num_in_shoe += 1
        self.money_committed = 0
    def adjust_count(self):
        # done after hand #
        for h in self.player_hands+[self.dealer_hand]:
            for c in h.hand_cards:
                if c.val in 'ATJQK': self.card_count -= 1
                elif c.val in '23456': self.card_count += 1
        self.running_count.append(self.card_count)
        self.get_real_count()
        if (len(self.shoe.shoe)/52) > 0:
            self.running_real_count.append(self.card_count / (len(self.shoe.shoe)/52))        
    def check_penetration(self):
        if self.shoe.check_shoe(self.penetration):
            self.card_count = 0
            self.real_count = 0
            self.shoe_num += 1
            self.shuffle_points.append(self.hand_num)
            self.hand_num_in_shoe = 1
    def get_real_count(self):
        if (len(self.shoe.shoe)/52) > 0:
            self.real_count = self.card_count / (len(self.shoe.shoe)/52)

def basic_strategy(t,player_hand,dealer_show,card_count,balance,count_divider):
    player_hand.calc_val()
    play = None
    if player_hand.hand_num_val in [20,21]:
        play = 'stand'; return play
    if player_hand.check_pair() and not t.no_more_money and play == None:
        if player_hand.hand_cards[0].val in ['A','8'] and t.money_committed + player_hand.bet <= balance:
            play = 'split'
        elif player_hand.hand_cards[0].num_val == 10:
            play = 'stand'
        elif player_hand.hand_cards[0].val == '9' and dealer_show.num_val not in [7,10,11] and t.money_committed + player_hand.bet <= balance:
            play = 'split'
        elif player_hand.hand_cards[0].val == '9' and dealer_show.num_val in [7,10,11]:
            play = 'stand'     
        elif player_hand.hand_cards[0].val == '7' and dealer_show.num_val <= 7 and t.money_committed + player_hand.bet <= balance:
            play = 'split'
        elif player_hand.hand_cards[0].val == '7' and dealer_show.num_val > 7:
            play = 'hit'
        elif player_hand.hand_cards[0].val == '6' and dealer_show.num_val <= 6 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'split'
        elif player_hand.hand_cards[0].val == '6' and dealer_show.num_val > 6:
            play = 'hit'
        elif player_hand.hand_cards[0].val == '5' and dealer_show.num_val <= 9  and len(player_hand.hand_cards) == 2 and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        elif player_hand.hand_cards[0].val == '5' and dealer_show.num_val <= 9  and len(player_hand.hand_cards) == 2:
            play = 'hit'
        elif player_hand.hand_cards[0].val == '5' and dealer_show.num_val > 9:
            play = 'hit'
        elif player_hand.hand_cards[0].val == '4' and dealer_show.num_val in [5,6] and t.money_committed + player_hand.bet <= balance:
            play = 'split'
        elif player_hand.hand_cards[0].val == '4' and dealer_show.num_val not in [5,6]:
            play = 'hit'
        elif player_hand.hand_cards[0].val in ['2','3'] and dealer_show.num_val <= 7 and t.money_committed + player_hand.bet <= balance:
            play = 'split'
        elif player_hand.hand_cards[0].val in ['2','3'] and dealer_show.num_val > 7:
            play = 'hit'
        if play != None: return play
    if player_hand.check_soft_ace():
        if player_hand.hand_num_val >= 20:
            play = 'stand'
        # elif player_hand.hand_num_val == 19 and 4 <= dealer_show.num_val <= 6 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance and t.card_count >= count_divider:
        #     play = 'double'
        elif player_hand.hand_num_val == 19 and dealer_show.num_val != 6: # always stand?
            play = 'stand'
        elif player_hand.hand_num_val == 19 and dealer_show.num_val == 6 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        elif player_hand.hand_num_val == 18 and dealer_show.num_val <= 6 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        elif player_hand.hand_num_val == 18 and 7 <= dealer_show.num_val <= 8:
            play = 'stand'     
        elif player_hand.hand_num_val == 17 and 3 <= dealer_show.num_val <= 6 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        elif 15 <= player_hand.hand_num_val <= 16 and 4 <= dealer_show.num_val <= 6 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        elif 13 <= player_hand.hand_num_val <= 14 and 5 <= dealer_show.num_val <= 6 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        else:
            play = 'hit'
        return play
    else:
        if player_hand.hard_total >= 17:
            play = 'stand'
        elif player_hand.hard_total == 16 and dealer_show.num_val in [7,8] and t.card_count >= count_divider:
            play = 'stand'   
        elif player_hand.hard_total == 15 and dealer_show.num_val in [7] and t.card_count >= count_divider:
            play = 'stand'
        elif 13 <= player_hand.hard_total <= 16 and dealer_show.num_val <= 6:
            play = 'stand'
        elif player_hand.hard_total == 12 and 4 <= dealer_show.num_val <= 6:
            play = 'stand'
        elif player_hand.hard_total == 11 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        elif player_hand.hard_total == 10 and dealer_show.num_val <= 9 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        elif player_hand.hard_total == 9 and 3 <= dealer_show.num_val <= 6 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance:
            play = 'double'
        # elif player_hand.hard_total == 8 and 4 <= dealer_show.num_val <= 6 and len(player_hand.hand_cards) == 2 and not t.no_more_money and t.money_committed + player_hand.bet <= balance and t.card_count >= count_divider:
        #     play = 'double'
        else:
            play = 'hit'
        return play

def determine_bet(t,min_bet,balance,bet_multiple,count_divider):
    for ph in t.player_hands:
        if t.card_count < count_divider:
            ph.bet = min_bet
        elif count_divider <= t.card_count:
            ph.bet = int(min_bet)*bet_multiple
        # elif t.real_count > bet_multiple:
        #     ph.bet = min_bet*bet_multiple
        # if (ph.bet*2 > balance): print(ph.bet,balance,len(t.player_hands))
        while ph.bet > balance or (ph.bet > t.card_count and ph.bet != min_bet):
            ph.bet -= 1
        t.money_committed += ph.bet
    if ph.bet*2 + ph.bet*(len(t.player_hands)-1) > balance: # ?
        t.no_more_money = True
    return t

def determine_num_players(t,count_divider):
    if t.card_count >= count_divider:
        # what is optimal?
        num_players = 1
        return num_players
    else:
        num_players = 1
        return num_players

def play_hands(t, balance, count_divider):
    for i,ph in enumerate(t.player_hands):
        t.dealer_hand.calc_val()
        if t.dealer_hand.hard_total == 21 and len(t.dealer_hand.hand_cards) == 2:
            # print(ph)
            if not ph.played:
                t.blackjack_count_tracker.append(t.card_count)
            ph.played = True
            continue
        play = ''; bust = False
        # print(ph)
        while play != 'stand' and not bust and not ph.played:
            ph.calc_val()
            play = basic_strategy(t,ph,t.dealer_show_card,t.card_count,balance,count_divider)
            ph.plays.append(play)
            if play == 'split':
                t.split_bool = True
                t.split_hand(ph)
                # for j,plh in enumerate(t.player_hands):
                #     print(f'Hand {j+1}: {plh}')
                play_hands(t, balance, count_divider)
            elif play == 'double': 
                t.hit_hand(ph)
                play = 'stand'
                ph.double_bet()
                t.money_committed += ph.bet
                # print(ph,play)
                ph.played = True
            elif play == 'hit':
                t.hit_hand(ph)
            elif t.check_bust(ph): 
                play = 'bust'
                t.num_dones += 1
                # print(ph,play)
                ph.played = True
                ph.plays.append(play)
            elif t.check_blackjack(ph):
                play = 'stand'
                t.num_dones += 1
                # print(ph,play)
                ph.played = True
                ph.plays.append(play)
        ph.played = True

def dealer_play(t):
    if t.num_dones < len(t.player_hands):
        while True:
            t.dealer_hand.calc_val()
            if t.dealer_hand.hard_total >= 18:
                break
            if t.dealer_hand.hard_total == 17 and t.dealer_hand.soft_total == False:
                break
            t.hit_hand(t.dealer_hand)

def assess_outcome(t,balance,bjp):
    winners = []; winnings = []
    t.dealer_hand.calc_val()
    for i,ph in enumerate(t.player_hands):
        ph.calc_val()
        if ph.hard_total > 21:
            # print('Player busts. Dealer wins.')
            winners.append('dealer')
            winnings.append(-1*ph.bet)
        elif t.dealer_hand.hand_num_val > 21:
            # print('Dealer busts. Player wins.')
            winners.append('player')
            winnings.append(ph.bet)
        elif ph.hard_total == 21 and len(ph.hand_cards) == 2 and t.dealer_hand.hand_num_val < 21:
            winners.append('player')
            winnings.append((bjp)*ph.bet)
        elif ph.hard_total > t.dealer_hand.hand_num_val:
            # print('Player wins')
            winners.append('player')
            winnings.append(ph.bet)
        elif ph.hard_total == t.dealer_hand.hand_num_val:
            # print('Push')
            winners.append('push')
            winnings.append(0)
        else:
            # print('Dealer wins')
            winners.append('dealer')
            winnings.append(-1*ph.bet)
    return winners, winnings, t.card_count

def session(num_players,num_shoes,num_decks,balance,penetration,bet_multiple,bjp,count_divider,max_balance,print_bool):
    min_bet = 1
    session_winnings = 0
    num_dealer_wins = 0
    num_player_wins = 0
    num_pushes = 0
    min_shoes = 3
    t = table(num_decks,penetration)
    while t.shoe_num <= num_shoes and balance < max_balance:
        t.check_penetration()
        if balance < min_bet*2 or t.shoe_num > num_shoes: break
        if print_bool: print('\n----------------------------\n')
        if print_bool: print(f'Count before hand: {t.card_count}')
        if print_bool: print(f'Balance before hand: {balance}')
        # change number of players (aka hands) based on count
        num_players = determine_num_players(t,count_divider)
        t.spawn_player_hands(num_players)
        determine_bet(t,min_bet,balance,bet_multiple,count_divider)
        t.deal_table()
        if print_bool: print(f'Dealer Show: {t.dealer_show_card}')
        # for i,ph in enumerate(t.player_hands):
        #     if print_bool: print(f'Hand {i+1}: {ph}')
        play_hands(t,balance,count_divider)
        dealer_play(t)
        for i,ph in enumerate(t.player_hands):
            if print_bool: print(f'Hand {i+1} Cards: {ph}')
            if print_bool: print(f'Hand {i+1} Plays: {", ".join(ph.plays)}')
            if print_bool: print(f'Hand {i+1} Bet: {ph.bet} {"unit" if ph.bet == 1 else "units"}')
        if print_bool: print(f'Dealer Hand: {t.dealer_hand}')
        round_winners, round_winnings, card_count = assess_outcome(t,balance,bjp)
        t.running_player_hands.append([h.hand_num_val for h in t.player_hands])
        t.running_dealer_hands.append(t.dealer_hand.hand_num_val)
        t.running_bets.append([h.bet for h in t.player_hands])
        t.adjust_count()
        t.clear_dealer_hand()
        t.clear_player_hands()
        balance += sum(round_winnings)
        t.outcomes.append(round_winners)
        session_winnings += sum(round_winnings)
        if print_bool: print(f'Round winnings: {sum(round_winnings)}')
        if print_bool: print(f'Balance after hand: {balance}')
        if print_bool: print(f'Count before hand: {t.card_count}')
        if print_bool: print(f'Shoe #: {t.shoe_num}')
        if print_bool: print(f'Shoe Depth: {t.shoe_stats()}')
        num_player_wins += round_winners.count('player')
        num_dealer_wins += round_winners.count('dealer')
        num_pushes += round_winners.count('push')
                
    # print(f'Count after hand: {t.card_count}')
    # avg_player_wins = num_player_wins/num_players
    # print('\n\n###########\n###########\n')
    # print(f'Table Winnings: {session_winnings} units')
    # print(f'Player Wins: {num_player_wins} wins')
    # if num_players > 1: print(f'Avg. Player Wins: {avg_player_wins} wins')
    # print(f'Dealer Wins: {num_dealer_wins} wins')
    # print(f'Pushes: {num_pushes} pushes')
    # print(f'Number of Shoes: {t.shoe_num} ({num_decks}-deck) shoes')
    # print(f'Estimated Time: {round(estimate_time(t,num_players)/60,2)} minutes ({round(estimate_time(t,num_players)/60/60,2)} hours)')
    # # df = assess_count_based_wins(t)
    if print_bool: print('\n----------------------------\n')
    return session_winnings, t

def sessions(num_sessions,num_players,num_decks,num_shoes,balance,penetration,bet_multiple,bjp,count_divider,max_balance,print_bool):
    winnings_tracker = []
    running_counts = []
    running_real_counts = []
    running_outcomes = []
    running_player_hands = []
    running_dealer_hands = []
    running_bets = []
    running_bj_counts = []
    for s in range(num_sessions):
        winnings, t = session(num_players,num_shoes,num_decks,balance,penetration,bet_multiple,bjp,count_divider,max_balance,print_bool)
        winnings_tracker.append(winnings)
        running_counts += t.running_count
        running_real_counts += t.running_real_count
        running_outcomes += t.outcomes
        running_player_hands += t.running_player_hands
        running_dealer_hands += t.running_dealer_hands
        running_bets += t.running_bets
        running_bj_counts += t.blackjack_count_tracker
    return winnings_tracker, running_counts, running_real_counts, running_outcomes, running_player_hands, running_dealer_hands, running_bets, running_bj_counts

def analyze_sessions(winnings_tracker, running_counts, running_real_counts, running_bj_counts, balance, num_shoes, num_decks):
    total_winnings = sum(winnings_tracker)
    running_winnings = []
    for i,wt in enumerate(winnings_tracker):
        if i == 0: running_winnings.append(wt); continue
        else: running_winnings.append(wt+running_winnings[i-1])
    num_sessions = len(winnings_tracker)
    winning_sessions = len([wt for wt in winnings_tracker if wt > 0])
    # losing_sessions = len([wt for wt in winnings_tracker if wt < 0])
    winning_percent = winning_sessions/len(winnings_tracker)
    avg_session_winnings = round(np.average(winnings_tracker),2)
    median_session_winnings = round(np.median(winnings_tracker),2)
    # losing_percent = losing_sessions/len(winnings_tracker)
    num_busts = len([wt for wt in winnings_tracker if wt <= -1*(balance-1)])
    bust_rate = num_busts/len(winnings_tracker)
    print(f'\nOver {num_sessions:,.0f} {"session" if num_sessions == 1 else "sessions"} with a {balance:,}-unit starting balance...\n{total_winnings:,.1f} (units) winnings ({(total_winnings/(num_sessions*balance))*100:,.2f}% ROI, {total_winnings/balance:,.2f} starting balances, {total_winnings/(num_shoes*num_sessions):.5f} avg profit per shoe, {total_winnings/(num_decks*num_shoes*num_sessions):.7f} avg profit per deck)\n{num_busts:,} balance {"bust" if winnings_tracker.count(-1*balance) == 1 else "busts"} ({bust_rate*100:.2f}%)\n{winning_percent*100:.2f}% winning sessions\n{avg_session_winnings} avg. session (units)\n{median_session_winnings} median session (units)')
    plt.figure()
    plt.hist(winnings_tracker, weights=np.ones(len(winnings_tracker)) / len(winnings_tracker), bins=100)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.title('Sessions Winnings')
    plt.ylabel('Frequency')
    plt.xlabel('Winnings (in units)')
    plt.show()
    plt.figure()
    plt.hist(running_counts,weights=np.ones(len(running_counts)) / len(running_counts),bins=len(set(running_counts)))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.title('Nominal Card Counts')
    plt.xlabel('Card Count')
    plt.ylabel('Frequency')
    plt.show()
    plt.figure()
    plt.hist(running_real_counts,weights=np.ones(len(running_real_counts)) / len(running_real_counts),bins=len(set(running_counts)))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.title('Real Card Counts')
    plt.xlabel('Card Count')
    plt.ylabel('Frequency')
    plt.show()
    plt.figure()
    plt.hist(running_bj_counts,weights=np.ones(len(running_bj_counts)) / len(running_bj_counts),bins=len(set(running_bj_counts)))
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.title('BlackJack Counts')
    plt.xlabel('Card Count')
    plt.ylabel('BlackJack Frequency')
    plt.show()
    plt.figure()
    plt.plot(range(1,len(running_winnings)+1),running_winnings)
    plt.title('Running Winners')
    plt.xlabel('Session')
    plt.ylabel('Winnings')
    plt.show()    
    
    # assess profiability of different counts (depends on bet system)
    
    # assess winability of different counts

def test_strategy(num_decks,num_players,pen,m,bjp,count_divider):
    num_sessions = 30000
    num_shoes = 5
    balance = 30
    max_balance = balance*1.5
    winnings_tracker = []
    for s in range(num_sessions):
        winnings_tracker.append(session(num_players,num_shoes,num_decks,balance,pen,m,bjp,count_divider,max_balance,print_bool=False)[0])
    # analyze_sessions(winnings_tracker)
    return [round(sum(winnings_tracker)/num_shoes,5), num_decks, num_players,pen,m,bjp,count_divider]

def test_strategies():
    candidate_decks = [2]
    candidate_num_players = [1]
    penetrations = [2/3,3/4]
    bet_multiples = [3,4,5,6,8]
    bj_payouts = [3/2]
    count_dividers = [1,2,3,4,5]
    data = []
    columns = ['Winnings (per shoe)','# Decks','# Players','Penetration','BlackJack Payout','Bet Multiple','Count Divider']
    for can_deck in candidate_decks:
        for num_players in candidate_num_players:
            for pen in penetrations:
                for m in bet_multiples:
                    for bjp in bj_payouts:
                        for cd in count_dividers:
                            print(f'{num_players} {"player" if num_players == 1 else "players"}, {can_deck} decks, {int(pen*100)}% penetration, {m} bet multiple, {round(bjp,2)} BlackJack payout')
                            data.append(test_strategy(can_deck,num_players,pen,m,bjp,cd))
    strategy_df = pd.DataFrame(data,columns=columns)
    strategy_df.to_csv(r'C:\Users\brend\Documents\Coding Projects\Blackjack\strategy_tests.csv')
    return strategy_df

# strategy_df = test_strategies()

### Test Area ###

num_sessions = 10000
num_players = 2 # starting num
num_decks = 1
num_shoes = 6
# balance = int(2*num_decks*num_shoes*num_players)
balance = 20
max_balance = balance*2
penetration = 2/3
blackjack_payout = 6/5
count_divider = 2
bet_multiple = 4
print_bool = False

winnings_tracker, running_counts, running_real_counts, running_outcomes, running_player_hands, running_dealer_hands, running_bets, running_bj_counts = sessions(num_sessions,num_players,num_decks,num_shoes,balance,penetration,bet_multiple,blackjack_payout,count_divider,max_balance,print_bool)

analyze_sessions(winnings_tracker, running_counts, running_real_counts, running_bj_counts, balance, num_shoes, num_decks)

min(winnings_tracker)

# print('\n########################\n')
# counts = list(range(min(running_bj_counts),max(running_bj_counts)+1))
# for count in counts:
#     outcomes = []
#     loss_count = 0; win_count = 0; push_count = 0
#     for i,ro in enumerate(running_outcomes):
#         if running_counts[i] == count:
#             outcomes += ro
#     loss_count = outcomes.count('dealer'); win_count = outcomes.count('player'); push_count = outcomes.count('push')
#     if round((running_bj_counts.count(count)/len(running_bj_counts))*100,2) > 1 and round((running_counts.count(count)/len(running_counts))*100,2) > 1:
#         # print(f'\n{round((running_bj_counts.count(count)/len(running_bj_counts))*100,2)}% BlackJacks on {count} count')
#         print(f'\n{round((running_counts.count(count)/len(running_counts))*100,2)}% of hands are at a {count} count hands')        
#         print(f'{round((running_bj_counts.count(count)/running_counts.count(count))*100,2)}% of {count} count hands are BlackJacks')
#         if loss_count+win_count+push_count > 0:
#             print(f'{round((win_count/(loss_count+win_count+push_count))*100,2)}% of {count} count hands are wins')
#             print(f'{round((loss_count/(loss_count+win_count+push_count))*100,2)}% of {count} count hands are losses')
#             print(f'{round((push_count/(loss_count+win_count+push_count))*100,2)}% of {count} count hands are pushes')
#     pos_bjs = 0
#     neg_bjs = 0
#     zero_bjs = 0
#     for c in running_bj_counts:
#         if int(c) > 0:
#             pos_bjs += 1
#         elif int(c) < 0:
#             neg_bjs += 1
#         else:
#             zero_bjs += 1
# print('\n########################\n')
# print(f'{round((pos_bjs/len(running_bj_counts))*100,2)}% BlackJacks on a positive count')
# print(f'{round((neg_bjs/len(running_bj_counts))*100,2)}% BlackJacks on a negative count')
# print(f'{round((zero_bjs/len(running_bj_counts))*100,2)}% BlackJacks on a zero count')
   

'''
Questions:
    What is the bust % of each dealer starting hand?
    What is the win % of each starting hand vs each dealer show card?
    Is there a max balance we can reliably close a session on with good ROI?
    When is insurance profitable? True count, decks remaining vs. 2:1 odds

'''

'''
Findings:
    Card count does not affect winning, losing, or pushing %
    33% more blackjacks on pos counts than neg counts
    BlackJack is most likely on 0 count hands (somehow)
    Count (nominal and real) or normally dist. around µ = 0
    
'''

