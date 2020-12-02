# CasinoBot
<h1>Getting Started</h1>
1. Make sure python 3.8 is installed.
2. Download and unzip the project.
3. Fill in the .env file with your token and guild identifiers.
4. In the directory, run `python3 bot/bot.py`

I plan on making these steps easier. 

<h1>Usage</h1>
<h2>User Commands</h2>
Initialize a new user, or show wallet information for existing users:
!wallet

Add funds to a User's wallet:
!addfunds <funds> 

Change a user's default bet:
!changebet <bet>

Show help message for a command:
!help <command>

<h2>Games</h2>
Play blackjack:
!blackjack
!hit to hit a blackjack hand
!blackjack ready (after all are ready)

Spin a slot machine:
!slot

Play high/low. You can specify odds:
!highlow <high/low> <odds>
  
Play dice vs a friend: 
!dicevs (must be called by two users)

Roll dice:
!dice (defaults to 6 sides and 2 rolls) 
To specify: !dice sides rolls

Draw a random card from the deck:
!drawcard
