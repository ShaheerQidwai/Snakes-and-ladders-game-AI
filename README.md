Project Overview:
This project presents a modified version of the traditional Snakes & Ladders game, enhanced with strategic gameplay mechanics and an AI opponent. The key innovations include the addition of multiple paths (main, safe, and risky), trap and power-up tiles, and a heuristic-based AI that makes decisions on path selection, trap placement, and power-up usage. The project aims to create a more engaging game experience while showcasing decision-making AI.


Algorithm and Heuristic Design:

Path Choice Heuristic:
  AI prefers risky path when behind and safe path when ahead, also considering the traps placed on either paths as well.

Trap Placement Heuristic:
  AI places traps when the human is ahead and likely to land on the trap within 3–6 tiles. 
  The traps are efficiently used when the human is within reach and by placing a trap the AI can likely catch up or move ahead of the human.

Power-up Strategy: 
  AI chooses to disarm traps if any exist; otherwise, it selects an extra roll.

  ![image](https://github.com/user-attachments/assets/f2e961e4-1c9f-44d7-b59d-12e2a3992c1d)

