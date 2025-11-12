
## Overview
**Connect4 Enhanced** is an upgraded version of the classic Connect Four game built with **Python** and **Pygame**. It features AI gameplay using the **Minimax algorithm** with **Alpha-Beta pruning**, multiple difficulty levels, animations, sound effects, and a polished graphical interface.

This enhanced version provides:
- Smooth animations for dropping discs
- Sound effects for moves and wins
- AI opponent with selectable difficulty (Easy, Medium, Hard)
- Game restart and exit options after each match
- Visual highlight of winning combinations
- Optimized AI logic with transposition caching

---

## Features
 **AI Opponent (Minimax + Alpha-Beta Pruning)** – Makes intelligent moves with customizable search depth.  
 **Difficulty Levels** – Easy (depth 2), Medium (depth 4), and Hard (depth 6).  
 **Graphical UI with Pygame** – Interactive GUI with mouse controls.  
 **Animations** – Realistic falling disc animation.  
 **Sound Effects** – Optional sounds for drop and win (use `drop.wav` and `win.wav`).  
 **Winning Highlight** – Green outline around the winning four discs.  
 **Restart or Exit Menu** – Replay or quit easily after a match.  
 **Optimized Performance** – Caching (transposition table) to speed up AI calculations.  

---

##  Game Rules
1. The board consists of **7 columns** and **6 rows**.
2. Players alternate dropping colored discs into a column.
3. The first player to align **4 discs horizontally, vertically, or diagonally** wins.
4. If the board is full and no one wins, it’s a draw.

---

##  Requirements
- **Python 3.8+**
- **Pygame** library

Install dependencies:   
```bash
pip install pygame numpy
```

Optional: Add sound files in the same directory:
- `drop.wav` – sound when a disc is dropped
- `win.wav` – sound when someone wins

---

##  How to Run
Clone or download this repository and run:
```bash
python connect4_enhanced.py
```

### Gameplay Instructions
1. When prompted, choose difficulty level (Easy, Medium, or Hard).
2. Click a column to drop your disc.
3. The AI will respond after your move.
4. After the game ends, click **Play Again** or **Exit**.

---

##  Code Structure
```
connect4_enhanced.py     # Main game script (AI, UI, logic)
drop.wav / win.wav        # Optional sound files
LICENSE                   # License file (MIT or Apache recommended)
README.md                 # This file
```

---

##  AI Logic Details
The AI uses **Minimax** with **Alpha-Beta pruning** and a **transposition table** to avoid redundant calculations.

### Heuristic Evaluation
- +1000 for 4 in a row
- +50 for 3 in a row with one empty
- +10 for 2 in a row with two empties
- −80 for opponent’s 3-in-a-row threats
- Additional weighting for **center column control**

---

##  Screenshots 
Add sample images like:
```
/images/screenshot1.png
/images/screenshot2.png
```

---

##  License
This project is open-source under the **MIT License**.  
You are free to use, modify, and distribute it with attribution.

```
MIT License
Copyright (c) 2025 Your Name
```

If you want to include sound or external assets, make sure they are under compatible licenses (e.g., CC0 or CC BY).

---

##  Future Enhancements
- Multiplayer mode (local or online)
- Smarter AI (Monte Carlo Tree Search)
- Leaderboard / scoring system
- Configurable themes and board sizes
- Touchscreen and mobile support

---

##  Author
**Your Name**  
Python Developer 
 Email: satyamsid51@gmail.com   

---

Enjoy playing **Connect4 Enhanced** — where strategy meets style! 

