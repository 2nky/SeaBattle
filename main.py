import time
from random import randint

# Класс, в котором храняться данные точек
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return other.x == self.x and other.y == self.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


# Класс, в котором храняться ошибки
class BoardException(Exception):
    pass


class OutOfBoard(BoardException):
    def __str__(self):
        return "Не стреляй вне доски"


class DuplicateShoot(BoardException):
    def __str__(self):
        return "Точка уже поражена"


class WrongShipPlacement(BoardException):
    pass


HORIZONTAL = 0
VERTICAL = 1


# Класс, в котором храняться данные корабля
class Ship:
    def __init__(self, size, placement, start):
        self.size = size
        self.placement = placement
        self.start = start
        self.lives = self.size

    def dots(self):
        dots = []

        for i in range(self.size):
            if self.placement == HORIZONTAL:
                dots.append(Dot(self.start.x + i, self.start.y))
            else:
                dots.append(Dot(self.start.x, self.start.y + i))

        return dots

    def shoot(self, dot):
        if dot not in self.dots():
            return False

        if self.lives > 0:
            self.lives -= 1
            return True

    def lives_left(self):
        return self.lives > 0

    def __str__(self):
        return f"Ship({self.size}, {self.placement}, {self.start}, dots = {self.dots})"


# Класс, в котором хранятся данные игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def show_board(self):
        self.board.display()

    def ask(self):
        raise NotImplementedError()

    def make_move(self):
        while True:
            try:
                target_x, target_y = self.ask()
                repeat = self.enemy.shoot(target_x, target_y)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        x = randint(1, 6)
        y = randint(1, 6)
        print(f"Ход компьютера: {x} {y}")
        return x, y


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("*** Введите 2 координаты! ***")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("*** Введите числа! ***")
                continue

            x, y = int(x), int(y)

            return x, y


# Класс, в котором храняться данные доски
class Board:
    def __init__(self, h, w, hidden=False):
        self.h = h
        self.w = w
        self.busy_dots = []
        self.ships = []
        self.hidden = hidden
        self.hits = []

        self.dots = []
        for a in range(h):
            row = []

            for b in range(w):
                row.append("~")

            self.dots.append(row)

    def ships_left(self):
        return any([ship.lives_left() for ship in self.ships])

    def shoot(self, x, y):
        dot = Dot(x - 1, y - 1)
        if not self.is_valid(dot):
            raise OutOfBoard

        if dot in self.hits:
            raise DuplicateShoot

        hit = False

        for ship in self.ships:
            if ship.shoot(dot):
                print("Попадание!")
                hit = True

                if not ship.lives_left():
                    print("КОРАБЛЬ УНИЧТОЖЕН!")
                    time.sleep(1)

                    self.make_contour(ship, draw=True)
                break

        if hit:
            self.dots[y - 1][x - 1] = "X"
        else:
            self.dots[y - 1][x - 1] = "*"
        self.hits.append(dot)

    def display(self):
        header = []
        header.append("    ")
        result = ""
        for a in range(self.w):
            header.append(str(a + 1))
            header.append("   ")
        result += "".join(header) + "\n"

        if self.hidden == False:
            print("*****[ Доска игрока ]*****")
        else:
            print("*****[ Доска компьютера ]*****")

        for a in range(self.h):
            row = " | ".join(self.dots[a])
            result += f"{a + 1} | {row} |\n"

        if self.hidden:
            result = result.replace("■", " ")
        print(result)

    def ships_generator(self):
        ships_list = [3, 2, 2, 1, 1, 1, 1]
        new_ships = []
        self.busy_dots = []
        self.dots = []
        self.ships = []
        for a in range(self.h):
            row = []

            for b in range(self.w):
                row.append(" ")

            self.dots.append(row)

        for l in ships_list:
            x = randint(0, 5)
            y = randint(0, 5)
            o = randint(0, 1)

            ship = Ship(l, o, Dot(x, y))
            dots = ship.dots()

            for dot in dots:
                if not self.is_valid(dot):
                    return False

                else:
                    if dot in self.busy_dots:
                        return False

            new_ships.append(ship)
            for dot in dots:
                self.busy_dots.append(dot)
            self.make_contour(ship)

        self.ships = new_ships
        for ship in self.ships:
            for dot in ship.dots():
                self.dots[dot.y][dot.x] = "■"
        return True

    def make_contour(self, ship, draw=False):
        pointers = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
        ]

        for dot in ship.dots():
            for dx, dy in pointers:
                x = dot.x + dx
                y = dot.y + dy
                candidat = Dot(x, y)

                if not self.is_valid(candidat):
                    continue

                if self.dots[y][x] == " ":
                    self.busy_dots.append(Dot(x, y))

                    if draw:
                        self.dots[y][x] = "·"

    def is_valid(self, dot):
        if dot.x < 0 or dot.x > 5:
            return False
        if dot.y < 0 or dot.y > 5:
            return False
        return True

# Класс, в котором хранится логика игры
class Game:
    def random_board(self, hidden=False):
        board = Board(6, 6, hidden=hidden)
        generated = False

        while not generated:
            generated = board.ships_generator()

        return board

    def __init__(self, size=6):
        self.size = size
        player_board = self.random_board()
        computer_board = self.random_board(hidden=True)

        self.ai = AI(computer_board, player_board)
        self.us = User(player_board, computer_board)

    def greet(self):
        print("*****************************")
        print("     Привет, Капитан!      ")
        print("*****************************")
        print("чтобы выстрелить введи: x и y")
        print("     x - номер строки        ")
        print("     y - номер столбца       ")

    def loop(self):
        num = 0
        while True:
            self.us.show_board()
            self.ai.show_board()

            print("*" * 29)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.make_move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.make_move()
            if repeat:
                num -= 1

            time.sleep(1)

            if not self.ai.board.ships_left():
                print("*" * 29)
                print("Пользователь выиграл!")
                break

            if not self.us.board.ships_left():
                print("*" * 29)
                print("Компьютер выиграл!")
                break

            print()
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()
