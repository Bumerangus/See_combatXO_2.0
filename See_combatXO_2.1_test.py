from random import randint
import time

# Exceptions
ship_lives = None
succes_dots = []
attempt_shot = 0
repeat = None
ho_move = None

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Координаты за пределами поля"


class BoardOutExceptionAI(BoardException):
    def __str__(self):
        return "Думает.."


class BoardUsedException(BoardException):
    def __str__(self):
        return "Сюда уже стреляли"


class BoardUsedExceptionAI(BoardException):
    def __str__(self):
        return "Думает..."


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, l, o):    # Координаты носа(Dot(x,y)), длинна(1 - 3), ориентация(0 - гор. 1 - верт.)
        self.bow = bow
        self.l = l
        self.lives = l
        self.o = o

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid                            # Скрывать или показывать поле
        self.size = size                          # Размер
        self.count = 0                            # Кол- во подбитых кораблей
        self.field = [['0'] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        global succes_dot, succes_dots, repeat
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)
        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    if ho_move == 0:
                        succes_dots = []
                    return True
                else:
                    print("Буум..Баах...")
                    if ship.lives:
                        succes_dot = d
                    return True

        self.field[d.x][d.y] = "."
        print("Промазал!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        global succes_dot, succes_dots, attempt_shot
        if succes_dots:
            attempt_shot += 1
            rand_var = randint(0, 3)
            D = succes_dots[-1]
            if attempt_shot > 10:
                D = succes_dots[-2]
            elif attempt_shot > 100:
                d = Dot(randint(0, 5), randint(0, 5))
                print(f"Ход ИИ: {d.x + 1} {d.y + 1}")
                return d
            v_1 = Dot(D.x + 1, D.y)    # 0
            v_2 = Dot(D.x - 1, D.y)    # 1
            v_3 = Dot(D.x, D.y + 1)    # 2
            v_4 = Dot(D.x, D.y - 1)    # 3
            var = [v_1, v_2, v_3, v_4]
            d = var[rand_var]
            if not((0 <= d.x < 6) and (0 <= d.y < 6)):
                print(f"Ход ИИ: {d.x + 1} {d.y + 1}")
                raise BoardOutExceptionAI()
            else:
                print(f"Ход ИИ: {d.x + 1} {d.y + 1}")
                return d
        else:
            d = Dot(randint(0, 5), randint(0, 5))
            print(f"Ход ИИ: {d.x + 1} {d.y + 1}")
            return d


class User(Player):
    def ask(self):
        while True:
            cords = f'{randint(0, 5)}',  f'{randint(0, 5)}'
            if len(cords) != 2:
                print(" Введите 2 координаты ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Это не числа! ")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = False
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("  See Combat 2.0  ")
        print("-" * 50)
        print("  Вам предстоит победить искуственный интелект.\n Он попытается выйграть у вас в морской бой 6x6.  ")
        print("             От исхода этой битвы  ")
        print("                  зависит судьба человечества...")
        print("-" * 50)
        print("Вводи координаты в формате - X Y")
        print(" X - строка, Y - столбец")

    def print_boards(self):
        print("-" * 20)
        print("Ваши корабли:")
        print(self.us.board)
        print("-" * 20)
        print("Корабли ИИ:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        global succes_dots, succes_dot, repeat, ho_move
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ваш ход")
                repeat = self.us.move()
                succes_dot = None
                ho_move = 1
            else:
                print("Ход ИИ")
                time.sleep(0)
                repeat = self.ai.move()
                ho_move = 0
                if succes_dot:
                    succes_dots.append(succes_dot)
                    print(succes_dots)
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                self.print_boards()
                print("-" * 20)
                print("Вы выйграли!")
                print("ИИ повержен! Мир спасен!")
                print("✮Слава пользователю✮")
                break

            if self.us.board.count == len(self.us.board.ships):
                self.print_boards()
                print("-" * 20)
                print("ИИ победил!")
                print("Вы запустили восстание машин..")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
