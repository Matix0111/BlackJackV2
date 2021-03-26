import random, os, sqlite3, argon2, getpass

class Blackjack():
    def __init__(self, username=None):
        self.username = username
    
    def updateChips(self, won=None, username=None):
        currentChips = self.fetchChips()

        if won == 'dealer':
            currentChips -= self.bet
        elif won == 'user':
            currentChips += self.bet

        cur.execute(f"UPDATE users SET chips = (?) WHERE username = ?", (currentChips, username))
        con.commit()

    def placeBet(self):
        bet = int(input('How many chips do you bet?: '))

        if bet < 500:
            print('You must bet 500 or more!')
        else:
            self.bet = bet

    def fetchChips(self):
        getChips = (f'{self.username}',)
        currentChips = cur.execute('SELECT chips FROM users WHERE username=?', getChips)
        currentChips = cur.fetchone()[0]
        return currentChips

    def setup(self):
        self.playerPoints = 0
        self.dealerPoints = 0
        self.playerPoints = random.randrange(1, 14)
        self.dealerPoints = random.randrange(1, 14)

    def startGame(self):
        self.setup()

        betPlaced = False
        done = False

        while not done:
            if not betPlaced:
                print(f'Available chip balance: {self.fetchChips()}')
                self.placeBet()
                print(f'You have bet {self.bet} chips.')
                print(f'Player : {self.playerPoints}\nDealer : {self.dealerPoints}')
            else:
                pass
            betPlaced = True
            over = False
            standOrHit = input('Hit or stand? [H/s] ').lower()
            if standOrHit == 'h':
                self.playerPoints += random.randrange(1, 14)
                if self.playerPoints > 21:
                    print('Bust!')
                    over = True
                    self.updateChips('dealer', self.username)
                elif self.playerPoints == 21:
                    print('You landed directly on 21! You win.')
                    self.updateChips('user', self.username)
                    over = True
                else:
                    print(f'Player : {self.playerPoints}')

            elif standOrHit == 's':
                while self.dealerPoints < 17:
                    self.dealerPoints += random.randrange(1, 14)
                
                if self.dealerPoints > 21:
                    print('Dealer busted! You win!')
                    self.updateChips('user', self.username)
                    over = True
                elif self.playerPoints == 21:
                    print('Dealer landed directly on 21! Dealer wins.')
                    self.updateChips('dealer', self.username)
                    over = True
                else:
                    if self.playerPoints > self.dealerPoints:
                        print('Player wins.')
                        self.updateChips('user', self.username)
                        over = True
                    elif self.playerPoints == self.dealerPoints:
                        print('Both have the same.')
                        over = True
                    else:
                        print('Dealer wins.')
                        self.updateChips('dealer', self.username)
                        over = True
            
            if over:
                done = self.replay()
                if not done:
                    betPlaced = False
                    self.setup()
        
    def replay(self):
        replay = input('Would you like to play again? [Y/n] ').lower()
        if replay == 'y':
            return False
        else:
            return True
    
    def startup(self):
        print('=-=-=-=-=-=-= WELCOME TO BLACKJACK! =-=-=-=-=-=-=\n\n')

        play = input(f'Ready to play, {self.username}? [Y/n] ').lower()

        if play == 'y':
            self.startGame()
        else:
            pass

class LoadInformation(Blackjack):
    def checkForTable(self):
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users'")
        if cur.fetchone()[0] == 1:
            return True
        else:
            cur.execute('''CREATE TABLE users (username text, password text, chips int)''')
            print('Users table now exists.')

    def fetchUserHash(self, username):
        query = (f'{username}',)
        cur.execute('SELECT password FROM users WHERE username=?', query)
        try:
            return cur.fetchone()[0]
        except TypeError:
            print('User does not exist.')
            sys.exit()

    def register(self):
        username = input('Desired username: ')
        password = getpass.getpass()
        passwordHash = str(ph.hash(password))
        defaultChips = 2000

        cur.execute(f"INSERT INTO users VALUES (?, ?, ?)", (f'{username}', f'{passwordHash}', defaultChips))
        con.commit()
    
    def login(self):
        username = input('Username: ')
        password = getpass.getpass()

        userHash = self.fetchUserHash(username)

        try:
            ver = ph.verify(userHash, password)
        except argon2.exceptions.VerifyMismatchError:
            ver = False
        
        if ver:
            b = Blackjack(username)
            b.startup()
        else:
            print('Login failed.')
    
    def getAction(self):
        exists = self.checkForTable()
        if exists:
            act = input('Do you have an account? [Y/n] ').lower()

            if act == 'y':
                self.login()
            elif act == 'n':
                self.register()

con = sqlite3.connect('accounts.db')
cur = con.cursor()
ph = argon2.PasswordHasher()

_start = LoadInformation()
_start.getAction()

# b = Blackjack()
# b.startup()