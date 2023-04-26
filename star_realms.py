from game import Game
from flask import Flask, render_template, request

app = Flask(__name__)
game = Game()
PLAYER_NAMES = ['player1', 'player2']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/play_card', methods=['POST'])
def play_a_card():
    card_id = request.json['card_id']
    player_name = request.json['player_name']
    try:
        game.play_card(card_id, player_name)
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    return {'success': True}

@app.route('/api/draw_card', methods=['POST'])
def draw_a_card():
    player_name = request.json['player_name']
    try:
        game.draw_card(player_name)
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    return {'success': True}

@app.route('/api/end_turn', methods=['POST'])
def end_a_turn():
    player_name = request.json['player_name']
    try:
        game.end_turn(player_name)
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    return {'success': True}

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    state = {}
    for player_name in PLAYER_NAMES:
        player_state = {}
        player_state['hand'] = game.get_hand(player_name)
        player_state['deck_size'] = game.get_deck_size(player_name)
        player_state['discard_pile'] = game.get_discard_pile(player_name)
        player_state['authority'] = game.get_authority(player_name)
        player_state['in_play'] = game.get_in_play(player_name)
        state[player_name] = player_state
    return state

@app.errorhandler(404)
def not_found_error(error):
    return {'success': False, 'message': 'Endpoint not found'}

@app.errorhandler(500)
def internal_error(error):
    return {'success': False, 'message': 'Internal server error'}

if __name__ == '__main__':
    app.run(debug=True)
