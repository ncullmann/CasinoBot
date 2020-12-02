# CasinoBot
<h1>Getting Started</h1>
1. Make sure python 3.8 is installed.<br/>
2. Download and unzip the project.<br/>
3. Fill in the .env file with your token and guild identifiers.<br/>
4. In the directory, run `python3 bot/bot.py`<br/>
I plan on making these steps easier.<br/>
<br/>
<h1>Usage</h1><br/>
<h2>User Commands</h2><br/>
Initialize a new user, or show wallet information for existing users:<br/>
!wallet
<br/>
Add funds to a User's wallet:<br/>
!addfunds <funds><br/>
<br/>
Change a user's default bet:<br/>
!changebet <bet><br/>
<br/>
Show help message for a command:<br/>
!help <command><br/>
<br/>
<h2>Games</h2><br/>
Play blackjack:<br/>
!blackjack<br/>
!hit to hit a blackjack hand<br/>
!blackjack ready (after all are ready)<br/>
<br/>
Spin a slot machine:<br/>
!slot<br/>
<br/>
Play high/low. You can specify odds:<br/>
!highlow <high/low> <odds><br/>
<br/>
Play dice vs a friend:<br/>
!dicevs (must be called by two users)<br/>
<br/>
Roll dice:<br/>
!dice (defaults to 6 sides and 2 rolls)<br/>
To specify: !dice sides rolls<br/>
<br/>
Draw a random card from the deck:<br/>
!drawcard<br/>
