#app.py
from flask import Flask, render_template, request, jsonify
import random
import string
from googletrans import Translator

app = Flask(__name__)

rooms = {}  # 儲存房間資訊

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    username = request.form['username']
    room_code = request.form.get('room_code', '').strip()
    word = request.form['word']

    if not room_code or room_code in rooms:
        room_code = ''.join(random.choices(string.ascii_uppercase, k=5))
    
    rooms[room_code] = {
        'host': username,
        'word': word,
        'players': [{'name': username, 'attempts': 0}],
        'guesses': [],
        'winner': None
    }
    return jsonify({'room_code': room_code})

@app.route('/join_room', methods=['POST'])
def join_room():
    username = request.form['username']
    room_code = request.form['room_code']

    if room_code not in rooms:
        return jsonify({'success': False})
    
    rooms[room_code]['players'].append({'name': username, 'attempts': 0})
    return jsonify({'success': True})

@app.route('/leave_room', methods=['POST'])
def leave_room():
    room_code = request.form['room_code']
    username = request.form['username']

    if room_code not in rooms:
        return jsonify({'success': False, 'message': '房間不存在'})
    
    room = rooms[room_code]
    room['players'] = [player for player in room['players'] if player['name'] != username]
    room['guesses'] = [guess for guess in room['guesses'] if guess['username'] != username]

    if not room['players']:
        del rooms[room_code]

    return jsonify({'success': True})

@app.route('/game')
def game():
    room_code = request.args.get('room_code')
    username = request.args.get('username')
    room_info = rooms.get(room_code)

    if not room_info:
        return "房間不存在", 404
    
    is_host = (room_info['host'] == username)
    player_list = [{'name': p['name'], 'attempts': p['attempts']} for p in room_info['players']]

    return render_template(
        'game.html',
        room_code=room_code,
        players=player_list,
        word_length=len(room_info['word']),
        is_host=is_host,
        word=room_info['word'],
        room_info=room_info,
        username=username,
        winner=room_info.get('winner')
    )

@app.route('/guess_word', methods=['POST'])
def guess_word():
    room_code = request.form['room_code']
    guess = request.form['word']
    username = request.form['username']

    if room_code not in rooms:
        return jsonify({'success': False, 'feedback': '房間不存在'})
    
    room = rooms[room_code]
    
    if room.get('winner'):
        return jsonify({
            'success': False,
            'feedback': f"遊戲已結束！獲勝者：{room['winner']['username']} (用了 {room['winner']['attempts']} 步)"
        })
    
    attempts = 0
    for player in room['players']:
        if player['name'] == username:
            player['attempts'] += 1
            attempts = player['attempts']
            break
    
    if guess == room['word']:
        translator = Translator()
        try:
            translation = translator.translate(room['word'], dest='zh-tw').text
        except Exception as e:
            print(f"翻譯錯誤：{str(e)}")
            translation = "（翻譯失敗）"
        
        room['winner'] = {
            'username': username,
            'attempts': attempts,
            'word': room['word'],
            'translation': translation
        }
        return jsonify({
            'success': True,
            'feedback': '恭喜你猜對了！',
            'winner': room['winner']
        })
    
    feedback = []
    correct_count = 0
    wrong_position_count = 0
    for i in range(len(guess)):
        if i < len(room['word']) and guess[i] == room['word'][i]:
            feedback.append(f"{guess[i]}存在且位置正確")
            correct_count += 1
        elif guess[i] in room['word']:
            feedback.append(f"{guess[i]}存在但位置錯誤")
            wrong_position_count += 1
    
    guess_result = {
        'username': username,
        'guess': guess,
        'correct_count': correct_count,
        'wrong_position_count': wrong_position_count,
        'feedback': ', '.join(feedback)
    }
    room['guesses'].append(guess_result)

    return jsonify({'success': False, 'feedback': ', '.join(feedback)})

if __name__ == '__main__':
    app.run(debug=True)