# Discord bot to play blackjack, slots, dice, and other games against the bot
# or against friends.
import os
import random
from art import text2art
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')


# User class to store username, cash in wallet, default bet, and the result
# of an outcome if playing vs others.
class User:
    def __init__(self, name, wallet, bet, outcome=None):
        self.name = name
        self.wallet = wallet
        self.bet = bet
        self.outcome = outcome

    def save_string(self):
        return self.name + ',' + str(self.wallet) + ',' + str(self.bet)


# List of initialized users.
# Temporary list of users who are playing each other.
users = []
users_vs = []

# Read the users file, if available.
try:
    with open("users.txt", "r") as fp:
        for line in fp:
            user = line.strip().split(',')
            users.append(User(user[0], float(user[1]), float(user[2])))
except:
    print('Users file does not exist.')


@bot.event
async def on_ready():
    print('Logged in to server.')


# Helper method to return an initialized user from users[].
def find_user(name):
    name = str(name)
    if not users:
        return None
    for user in users:
        if user.name == name:
            return user
    return None


# Helper method to show if the game resulted in a win or loss.
def win_loss(won, user, bet_multiplier=1.0):
    if won:
        user.wallet += (bet_multiplier * user.bet)
        return ' You won! Balance now: ' + str(user.wallet)[:7]
    else:
        user.wallet -= (bet_multiplier * user.bet)
        if user.wallet < 0.0:
            user.wallet = 0.0
        return ' You lost! Balance now: ' + str(user.wallet)[:7]


# Helper method to print whether a user exists or not.
def user_dne(user):
    if user is None:
        return 'User does not exist. Type !wallet to initialize.'
    return ''


# Writes the users list into a text file.
def save_state():
    try:
        with open('users.txt', 'w') as fp:
            for user in users:
                fp.write(user.save_string() + '\n')
        print('Saved file.')
    except:
        print('Users file did not save.')


# Initialize a new user, or show wallet and bet information for existing users.
@bot.command(name='wallet', help='Initialize a new user, or show wallet '
                                 'information for existing users. \n'
                                 'Usage: !wallet')
async def wallet_init(ctx):
    user = find_user(ctx.author)
    save_state()
    if user is None:
        users.append(User(str(ctx.author), 100.0, 5.0))
        await ctx.send('Created profile for: ' +
                       str(ctx.author) + ', bet: 5, wallet: 100')
        return
    else:
        await ctx.send(user.name + '\'s funds: ' +
                       str(user.wallet)[:7] + ', bet: ' + str(user.bet))
        return


# Add funds to a user's wallet.
@bot.command(name='addfunds', help='Add funds to your wallet. \n'
                                   'Usage: !addfunds 100')
async def add_funds(ctx, funds):
    user = find_user(ctx.author)
    if user_dne(user) != '':
        await ctx.send(user_dne(user))
        return

    user.wallet += float(funds)
    await ctx.send('Added ' + str(funds) + ' to ' + user.name +
                   '\'s wallet. Wallet is now: ' + str(user.wallet)[:7])


# Change the default bet.
@bot.command(name='changebet', help='Change your default bet. \n'
                                    'Usage: !changebet 22')
async def change_bet(ctx, bet):
    user = find_user(ctx.author)
    if user_dne(user) != '':
        await ctx.send(user_dne(user))
        return

    if float(bet) < 0:
        await ctx.send('Cannot have a negative bet.')
        return
    user.bet = float(bet)
    await ctx.send('Changed bet to: ' + str(user.bet))


# Possibilities for the slot machine.
slot_rolls = [{'multiplier': 2.0, 'id': '7'},  # 7
              {'multiplier': 1.0, 'id': '*'},  # Star
              {'multiplier': 0.5, 'id': '#'},  # Hash
              {'multiplier': 0.3, 'id': '-'},  # Bar
              {'multiplier': 0.0, 'id': 'O'}]  # Blank


# Spin the slot machine. RNG picks three entries in slot_rolls
# with weighted odds and the possibility for duplicates.
@bot.command(name='slot', help='Spin the slot machine! \n'
                               'Usage: !slot')
async def slot_machine(ctx):
    user = find_user(ctx.author)
    if user_dne(user) != '':
        await ctx.send(user_dne(user))
        return

    # Weighted odds for slot rolls.
    rolls = random.choices(slot_rolls, [1, 3, 5, 7, 15], k=3)
    multiplier = 0.0
    result_string = ''

    # Add multipliers from each column.
    for roll in rolls:
        multiplier += roll['multiplier']
        result_string += roll['id']
    if user.bet <= (user.bet * multiplier):
        await ctx.send('`\n' + text2art(result_string, font='banner3-d')
                       + '`' + win_loss(True, user, multiplier))
    else:
        await ctx.send('`\n' + text2art(result_string, font='banner3-d')
                       + '`' + win_loss(False, user, 1 - multiplier))


# Build a deck of cards.
suits = ['hearts', 'diamonds', 'clubs', 'spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10',
         'Jack', 'Queen', 'King', 'Ace']


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

        # Blackjack values
        if len(rank) < 2:
            self.value = int(rank)
        elif len(rank) == 3:
            self.value = 11
        else:
            self.value = 10

    def hand(self):
        return self.rank + ' of ' + self.suit


# Create the deck.
deck = [Card(rank, suit) for rank in ranks for suit in suits]


# Draw a random card.
@bot.command(name='drawcard', help='Draw a random card from the deck. \n'
                                   'Usage: !drawcard')
async def drawcard(ctx):
    await ctx.send(deck[random.randrange(0, 52)].hand())


# Play blackjack!
@bot.command(name='blackjack', help='Play blackjack! \n'
                                    'Usage: !blackjack \n'
                                    '!blackjack ready (after all are ready)')
async def blackjack(ctx, ready=''):
    user = find_user(ctx.author)
    if user_dne(user) != '':
        await ctx.send(user_dne(user))
        return

    # Bot is the dealer.
    if len(users_vs) == 0:
        users_vs.append(User('Bot', 0, 0, [random.randrange(0, 52),
                                           random.randrange(0, 52)]))

    if ready.lower() != 'ready':
        # 0-51 to choose from the deck. A number maps to a card.
        user.outcome = [random.randrange(0, 52), random.randrange(0, 52)]
        # Add the user to the list of users that are playing this game.
        users_vs.append(user)
        await ctx.send(user.name + '\'s hand: ' + deck[user.outcome[0]].hand()
                       + ', ' + deck[user.outcome[1]].hand())
        await ctx.send('Bot is showing: ' +
                       deck[users_vs[0].outcome[0]].hand())
    else:
        bot_hand_string = 'Bot\'s hand: ' + deck[
            users_vs[0].outcome[0]].hand() + \
                          ', ' + deck[users_vs[0].outcome[1]].hand()
        await ctx.send(bot_hand_string)
        bot_hand_value = deck[users_vs[0].outcome[0]].value + \
                         deck[users_vs[0].outcome[1]].value

        bot_hit = -1
        # Keep hitting for the bot until 17 or greater.
        while bot_hand_value < 17:
            bot_hit = random.randrange(0, 52)
            users_vs[0].outcome.append(bot_hit)
            bot_hand_value += deck[bot_hit].value
            await ctx.send('Bot hit!')
            bot_hand_string += deck[bot_hit]

        # If bot hit, send the bot's updated hand.
        if bot_hit != -1:
            await ctx.send(bot_hand_string)

        # Skip the bot.
        iterusers = iter(users_vs)
        next(iterusers)
        for user in iterusers:
            hand_value = 0
            hand_string = user.name + '\'s hand: '

            for i in range(len(user.outcome)):
                hand_value += deck[user.outcome[i]].value
                hand_string += deck[user.outcome[i]].hand()
                hand_string += ', '

            await ctx.send(hand_string[:-2])

            # Devalue ace to 1.
            if hand_value > 21:
                if 'Ace' in hand_string:
                    hand_value -= 10
                else:
                    await ctx.send('Bust!')

            else:
                if hand_value > bot_hand_value or bot_hand_value > 21:
                    await ctx.send(user.name + ' won!')
                elif hand_value == bot_hand_value:
                    await ctx.send('Push!')
                else:
                    await ctx.send(user.name + ' lost!')

            # Done playing, clear the list.
            if i == len(users_vs):
                users_vs.clear()


# Lets a user hit a blackjack hand.
@bot.command(name='hit', help='Hit a blackjack hand. \n'
                              'Usage: !hit')
async def hit(ctx):
    if len(users_vs) == 0:
        await ctx.send('No blackjack game in progress.')
        return

    for user in users_vs:
        # If the user is playing, add a card.
        if user.name == str(ctx.author):
            hand_string = user.name + '\'s hand: '
            user.outcome.append(random.randrange(0, 52))

            for i in range(len(user.outcome)):
                hand_string += deck[user.outcome[i]].hand()
                hand_string += ', '

            await ctx.send(hand_string[:-2])
            return


# Roll two six-sided die, or specify number of rolls and sides.
@bot.command(name='dice', help='Roll two die, or specify '
                               'number of sides and rolls. \n'
                               'Usage: !dice, !dice 10 3 (sides, rolls)')
async def dice(ctx, sides=6, rolls=2, called=False):
    s = '('
    for i in range(rolls):
        s += str(random.randrange(1, sides + 1)) + ', '
    if called:
        return int(s[1:-2])
    await ctx.send(s[:-2] + ')')


# Play high/low!
@bot.command(name='highlow', help='Play high/low. You can specify odds. \n'
                                  'Usage: !highlow high, !highlow low 70')
async def high_low(ctx, option, chosen_odds=50):
    number = await dice(ctx, 100, 1, True)

    user = find_user(ctx.author)
    if user_dne(user) != '':
        await ctx.send(user_dne(user))
        return

    # Higher odds, lower payout.
    if option.lower() == 'high' and number > 100 - chosen_odds:
        await ctx.send(str(number) + win_loss(True, user, (
                100 - chosen_odds) / chosen_odds))
    elif option.lower() == 'low' and number <= chosen_odds:
        await ctx.send(str(number) + win_loss(True, user, (
                100 - chosen_odds) / chosen_odds))
    elif option.lower() == 'high' or option.lower() == 'low':
        await ctx.send(str(number) + win_loss(False, user, (
                100 - chosen_odds) / chosen_odds))
    else:
        await ctx.send('Option not valid. Please type high or low.')


# Play dice against another user.
@bot.command(name='dicevs', help='Play dice vs a friend! \n'
                                 'Usage: Player 1: !dicevs \n'
                                 'Player 2: !dicevs')
async def dice_vs(ctx):
    user = find_user(ctx.author)
    if user_dne(user) != '':
        await ctx.send(user_dne(user))
        return

    user.outcome = await dice(ctx, 6, 1, True)

    if user not in users_vs:
        users_vs.append(user)
    else:
        await ctx.send("You cannot play against yourself.")
        return

    if len(users_vs) > 1:
        # Compare the two users' dice results, then print the winner.
        if users_vs[0].outcome > users_vs[1].outcome:
            await ctx.send(users_vs[0].name + ' won! Rolled: ' +
                           str(users_vs[0].outcome) + '. Loser rolled: ' +
                           str(users_vs[1].outcome))
        elif users_vs[0].outcome == users_vs[1].outcome:
            await ctx.send('Tie! Both rolled: ' + str(users_vs[0].outcome))
        else:
            await ctx.send(users_vs[1].name + ' won! Rolled: ' +
                           str(users_vs[1].outcome) + '. Loser rolled: ' +
                           str(users_vs[0].outcome))
        users_vs.clear()
        user.outcome = 0
    else:
        await ctx.send('Rolled: ' + str(users_vs[0].outcome))


bot.run(TOKEN, bot=True, reconnect=True)
