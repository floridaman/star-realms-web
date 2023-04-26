import random

class Card:
    def __init__(self, name, card_type, cost, faction, abilities, defense=None):
        self.name = name
        self.type = card_type
        self.cost = cost
        self.faction = faction
        self.abilities = abilities
        self.defense = defense

class Deck:
    def __init__(self, cards=None):
        self.cards = cards or []

    def draw(self):
        if not self.cards:
            return None
        return self.cards.pop(0)

    def shuffle(self):
        random.shuffle(self.cards)

class Player:
    def __init__(self, name, authority=50, deck=None, hand=None, discard_pile=None, in_play=None, trade=0, combat=0):
        self.name = name
        self.authority = authority
        self.deck = deck or self.initialize_starting_deck()
        self.hand = hand or []
        self.discard_pile = discard_pile or []
        self.in_play = in_play or []
        self.trade = trade
        self.combat = combat

    def initialize_starting_deck(self):
        starting_deck = Deck([Card("Scout", "Ship", 0, "Unaligned", {"trade": 1}, defense=None)] * 8 + [Card("Viper", "Ship", 0, "Unaligned", {"combat": 1}, defense=None)] * 2)
        starting_deck.shuffle()
        return starting_deck

    def draw_cards(self, count=1):
        for _ in range(count):
            card = self.deck.draw()
            if card:
                self.hand.append(card)
            else:
                self.deck.cards = self.discard_pile
                self.discard_pile = []
                self.deck.shuffle()
                card = self.deck.draw()
                if card:
                    self.hand.append(card)

    def discard_card(self, card_index):
        if card_index >= len(self.hand):
            print("Invalid card index.")
            return

        self.discard_pile.append(self.hand[card_index])
        self.hand.pop(card_index)

    def discard_hand(self):
        self.discard_pile.extend(self.hand)
        self.hand.clear()

class Game:
    def __init__(self, player1, player2, trade_deck, trade_row):
        self.player1 = player1
        self.player2 = player2
        self.trade_deck = trade_deck
        self.trade_row = trade_row

    def get_opponent(self, player):
        if player == self.player1:
            return self.player2
        return self.player1

    def play_card(self, player, card_index):
        if card_index >= len(player.hand):
            print("Invalid card index.")
            return False

        card = player.hand[card_index]
        player.in_play.append(card)
        player.hand.pop(card_index)
        self.apply_card_effect(player, card)
        return True

    def apply_card_effect(self, player, card, check_ally=True):
        if check_ally:
            ally_faction = self.check_ally_in_play(player, card.faction)

        for ability, value in card.abilities.items():
            if check_ally and ability.endswith("_ally") and not ally_faction:
                continue

            if ability.startswith("trade"):
                player.trade += value
            elif ability.startswith("combat"):
                player.combat += value
            elif ability.startswith("authority"):
                player.authority += value
            elif ability.startswith("draw"):
                player.draw_cards(value)
            elif ability.startswith("opponent_discard"):
                opponent = self.get_opponent(player)
                if opponent.hand:
                    card_index = int(input("Enter card index for the opponent to discard: "))
                    opponent.discard_card(card_index)
            # Add more card abilities here as needed

    def check_ally_in_play(self, player, faction):
        return any(card.faction == faction for card in player.in_play)

    def purchase_card(self, player, card_index):
        if card_index >= len(self.trade_row):
            print("Invalid card index.")
            return False
        
        card = self.trade_row[card_index]
        if player.trade < card.cost:
            print("Not enough trade points to purchase this card.")
            return False

        player.discard_pile.append(card)
        player.trade -= card.cost
        self.trade_row[card_index] = self.trade_deck.draw()
        return True

    def combat(self, attacker):
        if attacker.combat <= 0:
            print("No combat points available.")
            return False

        if not target:
            target = self.get_opponent(attacker)
            target.authority -= attacker.combat
        else:
            if target.card_type == "Outpost":
                target.authority -= attacker.combat
            else:
                target.authority = 0

        return True

    def scrap_card(self, player, card_location, card_index):
        if card_location == "hand":
            card_list = player.hand
        elif card_location == "in_play":
            card_list = player.in_play
        else:
            print("Invalid card location.")
            return False

        if card_index >= len(card_list):
            print("Invalid card index.")
            return False

        card = card_list[card_index]
        if "scrap_ability" not in card.abilities:
            print("This card does not have a scrap ability.")
            return False

        # Add more scrap logic here as needed

        card_list.pop(card_index)
        return True

def print_game_state(player, game):
    print(f"Player {player.authority} Authority")
    print(f"Trade: {player.trade} | Combat: {player.combat}")
    print("Hand:", [card.name for card in player.hand])
    print("In-Play:", [card.name for card in player.in_play])
    print("Trade Row:", [card.name for card in game.trade_row])

def main():
    # Initialize game components
    base_game_cards = [
        # Blob
        Card("Blob Fighter", "Ship", 1, "Blob", {"combat": 3, "draw_ally": 1}, defense=None),
        Card("Blob Wheel", "Base", 1, "Blob", {"trade": 1, "authority_ally": 1}, defense=5),
        Card("Battle Pod", "Ship", 2, "Blob", {"combat": 4, "scrap_ability": {"trade_row": 1}}, defense=None),
        Card("Trade Pod", "Ship", 2, "Blob", {"trade": 3, "combat_ally": 1}, defense=None),
        Card("Blob Destroyer", "Ship", 4, "Blob", {"combat": 6, "destroy_base": 1, "draw_ally": 1}, defense=None),
        Card("Blob Carrier", "Ship", 6, "Blob", {"combat": 7, "acquire_ship_ally": 1}, defense=None),
        Card("Blob World", "Base", 8, "Blob", {"combat": 5, "draw": 1, "draw_ally": 1}, defense=7),

        # Trade Federation
        Card("Trade Escort", "Ship", 2, "Trade Federation", {"authority": 4, "trade_ally": 2}, defense=None),
        Card("Defense Center", "Base", 2, "Trade Federation", {"combat": 2, "authority_ally": 3}, defense=5),
        Card("Trading Post", "Base", 3, "Trade Federation", {"trade": 1, "authority_ally": 1}, defense=4),
        Card("Freighter", "Ship", 4, "Trade Federation", {"trade": 4, "authority_ally": 4}, defense=None),
        Card("Central Office", "Base", 4, "Trade Federation", {"draw": 1, "trade_ally": 2}, defense=6),
        Card("Command Ship", "Ship", 8, "Trade Federation", {"authority": 4, "draw": 2, "destroy_base_ally": 1}, defense=None),
        Card("Fleet HQ", "Base", 8, "Trade Federation", {"combat_ship": 1}, defense=8),

        # Star Empire
        Card("Imperial Fighter", "Ship", 1, "Star Empire", {"combat": 2, "opponent_discard_ally": 1}, defense=None),
        Card("Survey Ship", "Ship", 1, "Star Empire", {"trade": 1, "draw_ally": 1}, defense=None),
        Card("Corvette", "Ship", 2, "Star Empire", {"combat": 1, "draw": 1, "draw_ally": 1}, defense=None),
        Card("Supply Bot", "Ship", 3, "Star Empire", {"trade": 2, "scrap_ability": {"combat": 2}}, defense=None),
        Card("Space Station", "Base", 4, "Star Empire", {"combat": 2, "trade_ally": 2}, defense=4),
        Card("Recycling Station", "Base", 4, "Star Empire", {"discard": 2, "draw": 2, "trade_ally": 1}, defense=5),
        Card("Imperial Frigate", "Ship", 5, "Star Empire", {"combat": 4, "opponent_discard": 1, "draw_ally": 1}, defense=None),
        Card("War World", "Base", 5, "Star Empire", {"combat": 3, "combat_ally": 4}, defense=4),
        Card("Battlecruiser", "Ship", 6, "Star Empire", {"combat": 5, "draw": 1, "opponent_discard_ally": 1}, defense=None),
        Card("Dreadnaught", "Ship", 7, "Star Empire", {"combat": 7, "draw": 1, "combat_ally": 5}, defense=None),

        # Machine Cult
        Card("Missile Bot", "Ship", 1, "Machine Cult", {"combat": 2, "scrap_ability": {"hand": 1}}, defense=None),
        Card("Supply Bot", "Ship", 2, "Machine Cult", {"trade": 2, "scrap_ability": {"combat": 2}}, defense=None),
        Card("Patrol Mech", "Ship", 3, "Machine Cult", {"trade": 3, "combat": 2, "scrap_ability": {"hand": 1}}, defense=None),
        Card("Stealth Needle", "Ship", 4, "Machine Cult", {"copy_ship": 1}, defense=None),
        Card("Battle Mech", "Ship", 5, "Machine Cult", {"combat": 4, "draw": 1, "scrap_ability": {"hand": 1}}, defense=None),
        Card("Mech World", "Base", 5, "Machine Cult", {"universal_ally": 1}, defense=6),
        Card("Junkyard", "Base", 6, "Machine Cult", {"scrap_ability": {"discard": 1}}, defense=5),
        Card("Machine Base", "Base", 7, "Machine Cult", {"combat": 5, "draw_ally": 1}, defense=6),
    ]

    unaligned_cards = [
        # Unaligned
        Card("Explorer", "Ship", 2, "Unaligned", {"trade": 2, "combat_ally": 2}, defense=None)
    ]

    trade_deck = Deck(base_game_cards)
    trade_deck.shuffle()
    trade_row = [trade_deck.draw() for _ in range(5)]

    player1 = Player(name="Player 1")
    player2 = Player(name="Player 2")
    game = Game(player1, player2, trade_deck, trade_row)

    starting_player = random.choice([player1, player2])
    if starting_player == player1:
        player1.draw_cards(3)
        player2.draw_cards(5)
    else:
        player1.draw_cards(5)
        player2.draw_cards(3)

    print(f"Player {starting_player.name} goes first")

    # Main game loop
    while player1.authority > 0 and player2.authority > 0:
        for player in [starting_player, game.get_opponent(starting_player)]:

            print_game_state(player, game)

            while True:
                action = input("Enter action (play, play all, purchase, combat, scrap, or end): ")
                success = False

                if action == "play":
                    card_index = int(input("Enter card index to play: "))
                    success = game.play_card(player, card_index)
                elif action == "play all":
                    for i, card in enumerate(player.hand):
                        success = game.play_card(player, i)
                elif action == "purchase":
                    card_index = int(input("Enter card index to purchase: "))
                    success = game.purchase_card(player, card_index)
                elif action == "combat":
                    success = game.combat(player)
                elif action == "scrap":
                    card_location = input("Enter card location (hand or in_play): ")
                    card_index = int(input("Enter card index to scrap: "))
                    success = game.scrap_card(player, card_location, card_index)
                elif action == "end":
                    break
                else:
                    print("Invalid action. Please try again.")

                if success:
                    print_game_state(player, game)

            player.discard_hand()
            player.draw_cards(5)

if __name__ == "__main__":
    main()
