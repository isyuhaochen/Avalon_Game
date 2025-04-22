import random
import datetime

class AvalonGame:
    def __init__(self, players, roles, agents):
        """Initialize the game with players, roles, agents, and set up initial state."""
        self.players = players
        self.agents = agents
        self.roles = roles
        self.history = []
        self.round_number = 0
        self.failed_team_votes = 0
        self.failed_missions = 0
        self.successful_missions = 0
        self.current_leader_idx = 0
        self.game_over = False

    def next_leader(self):
        """Get the next leader in the round-robin order."""
        leader = self.players[self.current_leader_idx]
        self.current_leader_idx = (self.current_leader_idx + 1) % len(self.players)
        return leader

    def log(self, msg):
        """Log a message to the game history and print it."""
        print(msg)
        self.history.append(msg)

    def play_round(self):
        """Play a single round of the game."""
        self.round_number += 1
        self.log(f"----- 第 {self.round_number} 轮 -----\n")
       
        leader = self.next_leader()
        self.log(f"当前队长: {leader}\n")

        # Propose a team
        team = self.agents[leader].propose_team(self.players, self.history, self.failed_missions + self.successful_missions)
        self.log(f"{leader} 提议的队伍: {team}\n")
       
        # Player comments on the team
        self.log("玩家发言：\n")
        for player in self.players:
            comment = self.agents[player].comment_on_team(team, self.history)
            self.log(f"{player}：{comment}")

        # Collect votes
        votes = {}
        self.log("投票情况：\n")
        for player in self.players:
            vote = self.agents[player].vote_on_team(team, self.history)
            votes[player] = vote
            print(f"{player} 投票：{vote}")

        # Count votes and check if the team is approved
        approved = sum(1 for v in votes.values() if v == "yes") > len(self.players) // 2

        if approved:
            self.log("队伍通过，执行任务\n")
            mission_results = [self.agents[p].mission_action(self.history) for p in team]
            self.log(f"任务执行情况：成功 {mission_results.count('success')} 票，失败 {mission_results.count('fail')} 票\n")

            # Determine mission success or failure based on conditions
            is_fourth_round = self.failed_missions + self.successful_missions + 1 == 4
            fail_count = mission_results.count("fail")

            if (is_fourth_round and fail_count < 2) or (not is_fourth_round and fail_count == 0):
                self.log("任务成功\n")
                self.successful_missions += 1
                mission_success = True
            else:
                self.log("任务失败\n")
                self.failed_missions += 1
                mission_success = False
        else:
            self.log("队伍未通过\n")
            mission_success = None
            self.failed_team_votes += 1

        # Log round details
        self.history.append(str({
            "round": self.round_number,
            "leader": leader,
            "team": team,
            "votes": votes,
            "mission_success": mission_success
        }))

        # Check for game-ending conditions
        self.check_game_over()

    def check_game_over(self):
        """Check if the game has ended based on current conditions."""
        if self.failed_team_votes >= 5:
            self.log('累计5次队伍未通过，坏人胜利！')
            self.game_over = True
        elif self.failed_missions >= 3:
            self.log('坏人成功破坏3次任务，胜利！')
            self.game_over = True
        elif self.successful_missions >= 3:
            self.assassinate_and_check_game_end()

    def assassinate_and_check_game_end(self):
        """Perform the assassin action and check if the game ends."""
        assassin_index = self.roles.index('刺客')
        target_role = self.agents[self.players[assassin_index]].assassinate(self.history)
        self.log(f'刺客刺杀的角色为{target_role}')
        
        # Check if the assassin killed Merlin
        merlin_index = self.roles.index('梅林')
        if target_role == self.players[merlin_index]:
            self.log('刺杀成功，坏人胜利')
        else:
            self.log("刺杀失败，坏人胜利")
        self.game_over = True

    def play_game(self):
        """Run the game until it's over."""
        while not self.game_over:
            self.play_round()

        # Game has ended, log the results
        self.log(f"----- 游戏结束 -----\n")

        # Save the game history to a file
        self.save_game_history()

    def save_game_history(self):
        """Save the game history to a log file with a timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"game_log/history_log_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.writelines([line + '\n' for line in self.history])
