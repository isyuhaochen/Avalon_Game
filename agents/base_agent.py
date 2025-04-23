import random
import re
from model import get_model_response
from prompt import (
    avalon_game_rules,
    generate_propose_team_prompt,
    generate_team_comment_prompt,
    generate_vote_on_team_prompt,
    generate_mission_action_prompt,
    generate_assassinate_action_prompt,
    generate_morgana_role_prompt,
    generate_loyal_servant_prompt,
    generate_merlin_role_prompt,
    generate_percival_role_prompt,
    generate_assassin_role_prompt,
    generate_oberon_role_prompt,
    generate_confirm_prompt
)

class BaseAgent:
    def __init__(self, player_id, role, all_players, role2player):
        self.player_id = player_id
        self.role = role
        self.all_players = all_players
        self.role_message = ''
        self.role2player = role2player

        # Generate role-specific message based on the player's role
        self._generate_role_message()

    def _generate_role_message(self):
        """Helper method to generate the appropriate role message."""
        if self.role == '莫甘娜':
            self.role_message = generate_morgana_role_prompt(assassin=self.role2player['刺客'])
        elif self.role == '梅林':
            self.role_message = generate_merlin_role_prompt(
                loyal1=self.role2player['忠臣1'], loyal2=self.role2player['忠臣2'],
                percival=self.role2player['派西维尔'], assassin=self.role2player['刺客'],
                morgana=self.role2player['莫甘娜'], oberon=self.role2player['奥伯伦']
            )
        elif '忠臣' in self.role:
            self.role_message = generate_loyal_servant_prompt()
        elif self.role == '奥伯伦':
            self.role_message = generate_oberon_role_prompt()
        elif self.role == '派西维尔':
            self.role_message = generate_percival_role_prompt(
                merlin=self.role2player['梅林'], morgana=self.role2player['莫甘娜']
            )
        elif self.role == '刺客':
            self.role_message = generate_assassin_role_prompt(morgana=self.role2player['莫甘娜'])

    def propose_team(self, players, history, round_number):
        """Propose a team based on game history and rules."""
        team_size_list = [2, 3, 3, 4, 4]
        team_size = team_size_list[round_number]
        history = '游戏历史：' + "\n".join(history)
        
        prompt = history + '\n' + avalon_game_rules + '\n' + self.role_message + generate_propose_team_prompt(players, team_size)
        ans = get_model_response(prompt)
        
        try:
            # Extract team members from the response
            match = re.search(r'\[([^\]]*)\]', ans)
            if match:
                list_str = match.group(1).strip()
                if list_str:
                    result_list = [item.strip().strip('"').strip("'") for item in list_str.split(',')]
                    if len(result_list) != team_size:
                        print(f"提议队伍人数不符合要求: {len(result_list)} != {team_size}")
                        return random.sample(players, team_size)
                    return result_list
                else:
                    return random.sample(players, team_size)
        except Exception as e:
            print(f"非法队伍: {e}")
            return random.sample(players, team_size)

    def comment_on_team(self, proposed_team, history):
        """Comment on a proposed team."""
        history = '游戏历史：' + "\n".join(history)
        prompt = history + '\n' + avalon_game_rules + '\n' + self.role_message + generate_team_comment_prompt(str(proposed_team))
        
        ans = get_model_response(prompt)
        prompt = history + '\n' + avalon_game_rules + '\n' + self.role_message + generate_confirm_prompt(message=ans, team=str(proposed_team))
        
        ans = get_model_response(prompt)
        return ans
        
    def vote_on_team(self, proposed_team, history):
        """Vote on a proposed team."""
        history = '游戏历史：' + "\n".join(history)
        prompt = history + '\n' + avalon_game_rules + '\n' + self.role_message + generate_vote_on_team_prompt(str(proposed_team))
        
        ans = get_model_response(prompt)
        if 'yes' in ans.lower():
            return 'yes'
        elif 'no' in ans.lower():
            return 'no'
        else:
            print('投票失败')
            print(ans)
            if self.player_id in proposed_team:
                return "yes"
            return random.choice(["yes", "no"])

        

    def mission_action(self, history):
        """Perform mission action, depending on the agent's role."""
        history = '游戏历史：' + "\n".join(history)
        if self.role in ['莫甘娜', '刺客', '奥伯伦']:
            prompt = history + '\n' + avalon_game_rules + '\n' + self.role_message + generate_mission_action_prompt()
            ans = get_model_response(prompt)
            if 'success' in ans.lower():
                return 'success'
            elif 'fail' in ans.lower():
                return 'fail'
            else:
                return random.choice(["success", "fail"])
        return "success"
    
    def assassinate(self, history):
        """Assassinate a player based on role and game history."""
        history = '游戏历史：' + "\n".join(history)
        candidate_list = [self.role2player['梅林'], self.role2player['忠臣1'], self.role2player['忠臣2'], self.role2player['派西维尔']]
        
        prompt = history + '\n' + avalon_game_rules + '\n' + self.role_message + generate_assassinate_action_prompt(str(candidate_list))
        ans = get_model_response(prompt)
        
        for name in candidate_list:
            if name.lower() in ans.lower():
                return name
        
        return random.choice(candidate_list)
       
