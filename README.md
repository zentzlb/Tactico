# Tactico

Tactico is a fog-of-war style turn based strategy game adapted from the popular board game 
Stratego. The goal of the game is to capture the flag (F).
<div align="lft">
    <img src="assets/F.png" width="" />
</div>
The rank of enemy pieces is concealed 
until they enter into combat. Higher rank pieces will win when matched against lower rank pieces.
Mines (M) are unable to move or attack, but will destroy an opposing piece when attacked. The 
flail tank (3) can safely remove mines.
<br>
<div style="display: inline-block; margin-right: 10px;">
  <img src="assets/3.png" width=""/>
</div>
<div style="display: inline-block;">
  <img src="assets/M.png" width="20"/>
</div>
<br>
The sniper (1) can remove adjacent pieces if it can correctly identify their rank.
<div align="lft">
    <img src="assets/1.png" width="" />
</div>

The Spy (S) can defeat the Terminator (10) if it initiates combat.
<br>
<div style="display: inline-block; margin-right: 10px;">
  <img src="assets/S.png" width=""/>
</div>
<div style="display: inline-block;">
  <img src="assets/10.png" width=""/>
</div>
<br>

Pieces may move in one direction and attack in a turn. Piece movement is based on rank.

| Movement | 0    | 1                    | 2       | ∞ |
|----------|------|----------------------|---------|---|
| Pieces   | M, F | S, 1, 4, 5, 8, 9, 10 | 3, 6, 7 | 2 |

<div align="left">
    <img src="assets/game.png" width="800" />
</div>