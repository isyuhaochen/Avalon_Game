# USTC 社会计算（COMP6223P01）实验二  
## 大模型参与的社交博弈游戏：阿瓦隆（7人局）

本实验模拟了LLM在社交推理游戏《阿瓦隆》中的决策行为。支持7人标准局的游戏设定。（LLM看起来总是在抄袭前面玩家的发言，建议prompt大师调整一下prompt）

### 结构说明

- `run_game.py`  
  游戏启动脚本，运行该文件以开始一局阿瓦隆游戏。

- `prompt.py`  
  提示词模块，定义角色提示信息和游戏中各阶段所需的 prompt，可根据需要自行调整优化。

- `model.py`  
  大语言模型接口模块。可通过修改 `api_url` 和 `api_key` 来切换不同的在线模型服务。

- `game.py`  
  游戏核心逻辑模块，控制整个阿瓦隆游戏的执行流程与规则实现。

- `agents/base_agent.py`  
  智能体行为定义，包含各类角色基于大模型的策略生成与响应逻辑。

