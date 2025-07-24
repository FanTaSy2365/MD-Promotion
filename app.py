from flask import Flask, request, jsonify, send_from_directory
import os
import random


app = Flask(__name__)

class RankSystem:
    def __init__(self):
        self.ranks = [
            "Platinum 5", "Platinum 4", "Platinum 3", "Platinum 2", "Platinum 1",
            "Diamond 5", "Diamond 4", "Diamond 3", "Diamond 2", "Diamond 1",
            "Master 5", "Master 4", "Master 3", "Master 2", "Master 1"
        ]
        self.current_rank_index = 0
        self.points = 0
        self.consecutive_losses = 0

    def get_promotion_threshold(self):
        if "Master" in self.ranks[self.current_rank_index]:
            return 5
        else:
            return 4

    def update_rank(self, win):
        promotion_threshold = self.get_promotion_threshold()

        if win:
            self.points += 1
            self.consecutive_losses = 0
            if self.points >= promotion_threshold:
                if self.current_rank_index < len(self.ranks) - 1:
                    self.current_rank_index += 1
                    self.points = 0
                else:
                    return "Max Rank"
            else:
                pass
        else:
            if self.points > 0:
                self.points -= 1
            elif self.points == 0:
                self.consecutive_losses += 1

            if self.points == 0 and self.consecutive_losses == 3 and \
                not self.ranks[self.current_rank_index].endswith("5") and \
                self.current_rank_index != len(self.ranks) - 1:
                if self.current_rank_index > 0:
                    self.current_rank_index -= 1
                    self.points = 0
                    self.consecutive_losses = 0
                else:
                    pass
            else:
                pass

    def get_rank_order(self):
        return self.ranks  

    def simulate_games(self, win_rate, num_games, starting_rank_index):
        self.current_rank_index = starting_rank_index
        results = {}
        for _ in range(num_games):
            if self.current_rank_index == len(self.ranks) - 1:
                break
            win = random.random() < win_rate / 100
            self.update_rank(win)
            rank = self.ranks[self.current_rank_index]
            if rank not in results:
                results[rank] = {"count": 1, "wins": int(win), "losses": int(not win)}
            else:
                results[rank]["count"] += 1
                results[rank]["wins"] += int(win)
                results[rank]["losses"] += int(not win)

        sorted_results = {}
        for rank in self.get_rank_order():
            if rank in results:
                sorted_results[rank] = results[rank]

        return sorted_results
        

rank_system = RankSystem()

@app.route('/')
def serve_html():
    return send_from_directory(directory=os.path.dirname(__file__), path="md.html")
@app.route("/run_simulation", methods=["GET"])

def run_simulation():
    win_rate = request.args.get("win_rate")
    num_games = request.args.get("num_games")
    starting_rank_index = request.args.get("rank_index")

    # 요청에서 win_rate, num_games, starting_rank_index가 모두 전달되었는지 확인
    if win_rate is None or num_games is None or starting_rank_index is None:
        return jsonify({"error": "win_rate, num_games, starting_rank_index are required parameters"})

    # 유효성 검사: 전달된 win_rate이 숫자인지 확인
    try:
        win_rate = float(win_rate)
    except ValueError:
        return jsonify({"error": "win_rate must be a valid number"})
    # 유효성 검사: 전달된 num_games와 starting_rank_index가 정수인지 확인
    try:
        num_games = int(num_games)
        starting_rank_index = int(starting_rank_index)
    except ValueError:
        return jsonify({"error": "num_games and starting_rank_index must be integers"})

    results = rank_system.simulate_games(win_rate, num_games, starting_rank_index)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)