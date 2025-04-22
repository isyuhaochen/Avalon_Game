from game import AvalonGame
from agents.base_agent import BaseAgent
import random

players = ['sjy', 'lsc', 'gc', 'lss', 'dfx', 'ljd', 'sl']

# 分配角色（简化版本：2 spy, 3 loyal）
roles = ['莫甘娜', '刺客', '梅林', '派西维尔', '忠臣1', '忠臣2', '奥伯伦']
random.shuffle(players)
random.shuffle(roles)

role2player = {role: name for name, role in zip(players, roles)}
agents = {}

for name, role in zip(players, roles):
    print(name, role)
    agents[name] = BaseAgent(name, role, players, role2player)
    

game = AvalonGame(players, roles, agents)
game.play_game()
