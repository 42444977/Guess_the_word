from flask import Flask, render_template, request, jsonify
import random
import string

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

    # 若未輸入房間代碼或重複，則隨機生成
    if not room_code or room_code in rooms:
        room_code = ''.join(random.choices(string.ascii_uppercase, k=5))
    
    rooms[room_code] = {
        'host': username,
        'word': word,
        'players': [{'name': username, 'attempts': 0}],
        'guesses': [],
        'winner': None  # 新增獲勝者欄位
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

    # 從玩家列表中移除該玩家
    room['players'] = [player for player in room['players'] if player['name'] != username]

    # 從猜測記錄中移除該玩家的猜測
    room['guesses'] = [guess for guess in room['guesses'] if guess['username'] != username]

    # 如果房間沒有玩家，刪除房間
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
    
    # 檢查是否已有獲勝者
    if room.get('winner'):
        return jsonify({
            'success': False,
            'feedback': f"遊戲已結束！獲勝者：{room['winner']['username']} (用了 {room['winner']['attempts']} 步)"
        })
    
    # 更新玩家猜測次數
    attempts = 0
    for player in room['players']:
        if player['name'] == username:
            player['attempts'] += 1
            attempts = player['attempts']
            break
    
    # 檢查猜測
    if guess == room['word']:
        room['winner'] = {
            'username': username,
            'attempts': attempts
        }
        return jsonify({
            'success': True,
            'feedback': '恭喜你猜對了！',
            'winner': room['winner']
        })
    
    # 計算反饋
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
    
    # 儲存猜測紀錄
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