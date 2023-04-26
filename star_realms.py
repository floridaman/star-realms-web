import random

class Card:
    def __init__(self, name, card_type, faction, cost, primary_ability, ally_ability=None, scrap_ability=None):
        self.name = name
        self.card_type = card_type
        self.faction = faction
        self.cost = cost
        self.primary_ability = primary_ability
        self.ally_ability = ally_ability
        self.scrap_ability = scrap_ability

base_game_cards = [
    # Star Empire
    Card("Battle Station", "Outpost", "Star Empire", 3, {"combat": 2}, None, {"combat": 4}),
    Card("Imperial Frigate", "Ship", "Star Empire", 3, {"combat": 4, "draw": 1}, {"target_discard": 1}, None),
    Card("Imperial Fighter", "Ship", "Star Empire", 1, {"combat": 2}, {"target_discard": 1}, None),
    Card("Survey Ship", "Ship", "Star Empire", 1, {"trade": 1, "draw": 1}, None, None),
    Card("Space Station", "Outpost", "Star Empire", 4, {"trade": 2}, None, {"combat": 4}),

    # Blob
    Card("Blob Wheel", "Outpost", "Blob", 3, {"trade": 3}, None, None),
    Card("Blob Destroyer", "Ship", "Blob", 4, {"combat": 6}, None, {"target_discard": 1}),
    Card("Battle Pod", "Ship", "Blob", 2, {"combat": 4}, {"combat": 2}, None),
    Card("Ram", "Ship", "Blob", 1, {"combat": 5}, None, {"trade": 2}),
    Card("Blob Fighter", "Ship", "Blob", 1, {"combat": 3}, {"draw": 1}, None),

    # Trade Federation
    Card("Trade Escort", "Ship", "Trade Federation", 4, {"authority": 4, "trade": 2}, None, None),
    Card("Freighter", "Ship", "Trade Federation", 4, {"trade": 4}, {"authority": 4}, None),
    Card("Central Office", "Base", "Trade Federation", 3, {"trade": 2, "draw": 1}, None, None),
    Card("Embassy Yacht", "Ship", "Trade Federation", 3, {"authority": 2, "trade": 2}, {"authority": 2, "draw": 1}, None),
    Card("Barter World", "Base", "Trade Federation", 2, {"authority": 4}, {"trade": 2}, None),

    # Machine Cult
    Card("Defense Center", "Outpost", "Machine Cult", 4, {"combat": 2}, None, {"authority": 5}),
    Card("Missile Bot", "Ship", "Machine Cult", 2, {"combat": 2}, None, {"scrap_hand_or_discard": 1}),
    Card("Supply Bot", "Ship", "Machine Cult", 3, {"trade": 2}, None, {"scrap_hand_or_discard": 1}),
    Card("Stealth Needle", "Ship", "Machine Cult", 4, {"copy_ship": 1}, None, None),
    Card("Trade Bot", "Ship", "Machine Cult", 1, {"trade": 1}, None, {"scrap_hand_or_discard": 1}),
]


class Player:
    def __init__(self, authority=50, deck=None, hand=None, discard_pile=None, in_play=None, trade=0, combat=0):
        self.authority = authority
        self.deck = deck or self.initialize_starting_deck()
        self.hand = hand or []
        self.discard_pile = discard_pile or []
        self.in_play = in_play or []
        self.trade = trade
        self.combat = combat

    def initialize_starting_deck(self):
        starting_deck = [Card("Scout", "Ship", "Unaligned", 0, {"trade": 1}) for _ in range(8)]
        starting_deck.extend([Card("Viper", "Ship", "Unaligned", 0, {"combat": 1}) for _ in range(2)])
        random.shuffle(starting_deck)
        return starting_deck
    
    def print_hand(self):
        print("Hand:")
        for i, card in enumerate(self.hand):
            print(f"{i}: {card.name}")

    def draw_cards(self, num_cards=5):
        for _ in range(num_cards):
            if not self.deck:
                random.shuffle(self.discard_pile)
                self.deck, self.discard_pile = self.discard_pile, self.deck
            self.hand.append(self.deck.pop())

    def discard_cards(self, num_cards):
        for _ in range(num_cards):
            if not self.hand:
                break
            self.print_hand()
            card_index = int(input("Enter card index to discard: "))
            self.discard_pile.append(self.hand.pop(card_index))

    def discard_hand(self):
        self.discard_pile.extend(self.hand)
        self.hand.clear()

class Game:
    def __init__(self, player1, player2, trade_row=None, explorers=None):
        self.player1 = player1
        self.player2 = player2
        self.trade_row = trade_row or []
        self.explorers = explorers or [Card("Explorer", "Ship", "Unaligned", 2, {"trade": 2}, None, {"combat": 2}) for _ in range(5)]

        self.initialize_trade_row()

    def initialize_trade_row(self):
        random.shuffle(base_game_cards)
        for _ in range(5):
            self.trade_row.append(base_game_cards.pop())

    def play_card(self, player, card_index):
        card = player.hand.pop(card_index)
        player.in_play.append(card)

        # Apply primary ability
        for ability, value in card.primary_ability.items():
            self.apply_ability(player, ability, value)

        # Check for ally abilities
        for in_play_card in player.in_play:
            if in_play_card.faction == card.faction and in_play_card.ally_ability and in_play_card != card:
                for ability, value in in_play_card.ally_ability.items():
                    self.apply_ability(player, ability, value)

    def apply_ability(self, player, ability, value):
        if ability == "combat":
            player.combat += value
        elif ability == "trade":
            player.trade += value
        elif ability == "authority":
            player.authority += value
        elif ability == "draw":
            player.draw_cards(value)
        elif ability == "target_discard":
            opponent = self.get_opponent(player)
            opponent.discard_cards(value)

    def purchase_card(self, player, card_index):
        card = self.trade_row.pop(card_index)
        player.discard_pile.append(card)
        player.trade -= card.cost
        self.trade_row.append(base_game_cards.pop())

    def combat(self, attacker, target=None):
        if not target:
            target = self.get_opponent(attacker)
            target.authority -= attacker.combat
        else:
            if target.card_type == "Outpost":
                target.authority -= attacker.combat
            else:
                target.authority = 0

    def scrap_card(self, player, card_location, card_index):
        card = None
        if card_location == "hand":
            card = player.hand.pop(card_index)
        elif card_location == "in_play":
            card = player.in_play.pop(card_index)

        if card and card.scrap_ability:
            for ability, value in card.scrap_ability.items():
                self.apply_ability(player, ability, value)

    def get_opponent(self, player):
        if player == self.player1:
            return self.player2
        else:
            return self.player1

def print_game_state(player, game):
    print(f"Player {1 if player == game.player1 else 2}'s turn")
    print(f"Authority: {player.authority}")
    print(f"Trade: {player.trade}")
    print(f"Combat: {player.combat}")
    print("\nHand:")
    for i, card in enumerate(player.hand):
        print(f"{i}: {card.name}")
    print("\nIn play:")
    for card in player.in_play:
        print(card.name)
    print("\nTrade row:")
    for i, card in enumerate(game.trade_row):
        print(f"{i}: {card.name} ({card.cost})")
    print("\nOpponent's in play:")
    opponent = game.get_opponent(player)
    for card in opponent.in_play:
        if card.type == "Outpost":
            print(f"{card.name} (Outpost) - {card.defense}")
        elif card.type == "Base":
            print(f"{card.name} (Base)")


def main():
    # Initialize players and game
    player1 = Player()
    player2 = Player()
    game = Game(player1, player2)

    # Determine starting player and initial card draw
    starting_player = random.choice([player1, player2])
    if starting_player == player1:
        player1.draw_cards(3)
        player2.draw_cards(5)
    else:
        player1.draw_cards(5)
        player2.draw_cards(3)

    # Main game loop
    while player1.authority > 0 and player2.authority > 0:
        for player in [starting_player, game.get_opponent(starting_player)]:
            print_game_state(player, game)

            while True:
                action = input("Enter action (play, purchase, combat, scrap, or end): ")
                if action == "play":
                    card_index = int(input("Enter card index to play: "))
                    game.play_card(player, card_index)
                elif action == "purchase":
                    card_index = int(input("Enter card index to purchase: "))
                    game.purchase_card(player, card_index)
                elif action == "combat":
                    game.combat(player)
                elif action == "scrap":
                    card_location = input("Enter card location (hand or in_play): ")
                    card_index = int(input("Enter card index to scrap: "))
                    game.scrap_card(player, card_location, card_index)
                elif action == "end":
                    break
                else:
                    print("Invalid action. Please try again.")

                print_game_state(player, game)

            if game.get_opponent(player).authority <= 0:
                print(f"Player {1 if player == player1 else 2} wins!")
                break

            # Reset trade and combat properties for the next turn
            player.trade = 0
            player.combat = 0

            player.discard_hand()
            player.draw_cards(5)  # Draw 5 cards at the end of each player's turn

if __name__ == "__main__":
    main()

