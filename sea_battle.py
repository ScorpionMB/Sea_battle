from random import randint, choice
import os
import time

# Для работы цвета в консоли Windows
import ctypes
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


# здесь просто задаем цвета. Они не соответствуют своим названиям, но главное всё сгруппировано в одном месте
# при желании цвета можно легко поменять не колупаясь во всей логике приложения
class Color:
    yellow2 = '\033[1;35m'
    reset = '\033[0m'
    blue = '\033[1;36m'
    yellow = '\033[1;33m'
    red = '\033[1;31m'
    miss = '\033[1;33m'
    faded = '\033[2;37m'


# функция которая окрашивает текст в заданный цвет.
def set_color(text, color):
    return color + text + Color.reset


# класс "клетка". Здесь мы задаем и визуальное отображение клеток и их цвет.
# по визуальному отображению мы проверяем какого типа клетка. Уж такая реализация.
# По этой причине нельзя обозначать одним символом два разных типа. Иначе в логике возникнет путаница.
class Cell:
    ship_cell = set_color('■', Color.blue)
    destroyed_ship = set_color('X', Color.yellow)
    damaged_ship = set_color('□', Color.yellow)
    miss_cell = set_color('•', Color.miss)
    grid = set_color('•', Color.faded)


class Board:
    """
    класс полей
    """
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

    def __init__(self):
        self.board = []
        self.sequence = []
        for n in range(10):
            self.board.append([Cell.grid] * 10)
            self.sequence.append([1] * 10)

    def print_board(self):
        # печать поля коэффициентов
        # (разкомметировать для вывода на экран)
        # print('\n\t\033[1;4;33m* В Е С  Я Ч Е Е К *\033[0m'.expandtabs(), '\n')
        # print('  ', end=' ')
        # for j in range(10):
        #     print('\033[1;4;36m', f'{j}', end=' ')
        # print('\033[0m')
        # for i, row in zip(self.letters, game.field_weight.sequence):
        #     print(f'\033[1;35m{i}|', '\033[0m', '  '.join(list(map(str, row))))
        # print('')

        # печать полей игроков
        print('\n\t\033[1;4;33m* К О М П Ь Ю Т Е Р *\033[0m'.expandtabs(tabsize=7),
              '\t\033[1;4;33m* И Г Р О К *\033[0m'.expandtabs(tabsize=28), '\n')
        print('  ', end=' ')
        for j in range(10):
            print('\033[1;4;36m', f'{j}', end=' ')
        print('\033[0m\t'.expandtabs(tabsize=16), end='')
        print('   ', end=' ')
        for j in range(10):
            print('\033[1;4;36m', f'{j}', end=' ')
        print('\033[0m\t'.expandtabs(tabsize=16), end='')
        print('   ')
        for i, row1, row2 in zip(self.letters, game.field_radar.board, game.field_user.board):
            print(f'\033[1;35m{i}|', '\033[0m', '  '.join(list(map(str, row1))), '\t'.expandtabs(tabsize=12),
                  f'\033[1;35m{i}|', '\033[0m', '  '.join(list(map(str, row2))), '\t'.expandtabs(tabsize=12))
        print('')

    # случайный выбор координат ячеек
    def random_row(self):
        return randint(0, len(self.board) - 1)

    def random_col(self):
        return randint(0, len(self.board[0]) - 1)

    # отметка убитых кораблей и ячеек вокруг них
    @staticmethod
    def mark_destroyed_ship(player, ship):

        if not player.auto:
            field = game.field_user.board
        else:
            field = game.field_radar.board

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(field) or p_y < 0 or p_y >= len(field):
                    continue
                field[p_x][p_y] = Cell.miss_cell

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                field[p_x][p_y] = Cell.destroyed_ship


class Ship:
    """
    Класс кораблей
    """
    ships_rules = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]  # список длин кораблей

    def __init__(self, len_ship):
        self.x = game.field_user.random_row()
        self.y = game.field_user.random_col()
        self.height = None
        self.width = None
        self.len_ship = len_ship
        self.direction = randint(0, 1)
        self.set_ship()
        self.setup = True

    def __str__(self):
        return Cell.ship_cell

    def set_ship(self):
        if self.direction == 0:
            self.height = 1
            self.width = self.len_ship

        if self.direction == 1:
            self.height = self.len_ship
            self.width = 1

    def print_ship(self):
        print(self.x, self.y, self.len_ship, self.direction)

    # метод установки кораблей на поле
    def install_ship(self, field, occupied, ship, player):

        if self.checking_placement(field, occupied, ship.x, ship.y):
            for _ in range(self.len_ship):
                if self.direction == 0:
                    field.board[self.x][self.y + _] = ship
                if self.direction == 1:
                    field.board[self.x + _][self.y] = ship
            player.list_ships.append(ship)
        else:
            self.setup = False
            return

    # проверка места для установки корабля
    def checking_placement(self, field, occupied, x, y):
        s_x = x
        s_y = y

        if s_x + self.height < 11 and s_y + self.width < 11 and field.board[s_x][s_y] == Cell.grid \
                and (s_x + max(0, self.height - 3), s_y + max(0, self.width - 3)) not in occupied \
                and (s_x + max(0, self.height - 2), s_y + max(0, self.width - 2)) not in occupied \
                and (s_x + max(0, self.height - 1), s_y + max(0, self.width - 1)) not in occupied:
            return True

    # заполнение списка занятых ячеек
    def occupied_board(self, field, occupied):
        for o_x in range(self.x - 1, self.x + self.height + 1):
            for o_y in range(self.y - 1, self.y + self.width + 1):
                if o_x < 0 or o_x >= len(field.board) or o_y < 0 or o_y >= len(field.board):
                    continue
                if str(field.board[o_x][o_y]) != Cell.ship_cell:
                    occupied.append((o_x, o_y))

    @staticmethod
    def print_occupied(field, occupied):
        for x, y in occupied:
            field.board[x][y] = Cell.miss_cell


class Shot:
    """
    Класс выстрелов
    """
    def __init__(self):
        self.x = None
        self.y = None
        self.weights = []  # список вариантов для выстрела
        self.occupied_field = []  # спсик занятых ячеек для поля коэффициентов
        self.success_rate = False  # логическая переменная возможности размещения корабля

    # метод выстрела при ручном вводе координат
    def shot_by_ships(self, player, field):
        xy = input('\033[1;32mВаш выстрел (например, d3): ')
        if len(xy) == 2:
            input_x = xy[0]
            if xy[1].isdigit():
                input_y = int(xy[1])
            else:
                input_y = 10
            if input_x in Board.letters and 0 <= input_y < 10:
                self.x = Board.letters.index(input_x)
                self.y = int(xy[1])
                if game.field_radar.board[self.x][self.y] in (Cell.miss_cell, Cell.damaged_ship, Cell.destroyed_ship):
                    print('Эта клетка занята! Еще разок...')
                    self.shot_by_ships(player, field)
                self.receive_shot(player, field)
            else:
                print('Неправильный ввод. Еще разок... ')
                return self.shot_by_ships(player, field)
        else:
            print('Должно быть две координаты. Еще разок...')
            return self.shot_by_ships(player, field)

    # метод выстрела при автоматическом вводе координат
    def shot_by_ships_auto(self, player, field):
        self.get_weights()
        while True:
            if self.weights:
                self.x, self.y = choice(self.weights)
            else:
                self.x = game.field_user.random_row()
                self.y = game.field_user.random_col()
            if not field.board[self.x][self.y] in (Cell.miss_cell, Cell.damaged_ship, Cell.destroyed_ship) \
                    or game.field_weight.sequence[self.x][self.y] == 2:
                self.weights = []
                print(str(Board.letters[self.x] + str(self.y)))
                time.sleep(3)
                self.receive_shot(player, field)
                self.recalculate_weight_map()
                break

    # метод обработки результатов выстрела
    def receive_shot(self, player, field):
        sx = self.x
        sy = self.y

        if str(field.board[sx][sy]) == Cell.ship_cell:
            ship = field.board[sx][sy]
            ship.len_ship -= 1

            if ship.len_ship <= 0:
                if player.auto:
                    game.field_radar.mark_destroyed_ship(player, ship)
                else:
                    field.mark_destroyed_ship(player, ship)
                player.list_ships.remove(ship)
                game.message = 'kill'
                return 'kill'
            if player.auto:
                game.field_radar.board[sx][sy] = Cell.damaged_ship
            else:
                field.board[sx][sy] = Cell.damaged_ship
            game.message = 'get'
            return 'get'

        else:
            if player.auto:
                game.field_radar.board[sx][sy] = Cell.miss_cell
            else:
                field.board[sx][sy] = Cell.miss_cell
            game.message = 'miss'
            return 'miss'

    # метод пересчета коэффициентов
    def recalculate_weight_map(self):

        # Для начала мы выставляем всем клеткам 1.
        # нам не обязательно знать какой вес был у клетки в предыдущий раз:
        # эффект веса не накапливается от хода к ходу.
        game.field_weight.sequence = [[1 for _ in range(10)] for _ in range(10)]

        # Пробегаем по всем полю.
        # Если находим раненый корабль - ставим клеткам выше ниже и по бокам
        # коэффициенты умноженные на 2, т.к. логично что корабль имеет продолжение в одну из сторон.
        # По диагоналям от раненой клетки ничего не может быть - туда вписываем нули
        self.occupied_field = []
        for x in range(10):
            for y in range(10):
                if game.field_user.board[x][y] in (Cell.miss_cell, Cell.damaged_ship, Cell.destroyed_ship):
                    self.occupied_field.append((x, y))

        for x in range(10):
            for y in range(10):
                self.success_rate = False
                for ship in game.next_player.list_ships:
                    res = ship.checking_placement(game.field_user, self.occupied_field, x, y)
                    # print(str(x) + str(y), 'res: ', res)
                    if res or str(game.field_user.board[x][y]) == Cell.ship_cell:
                        self.success_rate = True
                # print('\n', str(x) + str(y), self.success_rate, '\n')
                if not self.success_rate:
                    game.field_weight.sequence[x][y] = 2

        for x in range(10):
            for y in range(10):

                if game.field_user.board[x][y] == Cell.damaged_ship:

                    game.field_weight.sequence[x][y] = 0

                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            game.field_weight.sequence[x - 1][y - 1] = 0
                        game.field_weight.sequence[x - 1][y] *= 3
                        if y + 1 < 10:
                            game.field_weight.sequence[x - 1][y + 1] = 0
                    if y - 1 >= 0:
                        game.field_weight.sequence[x][y - 1] *= 3
                    if y + 1 < 10:
                        game.field_weight.sequence[x][y + 1] *= 3
                    if x + 1 < 10:
                        if y - 1 >= 0:
                            game.field_weight.sequence[x + 1][y - 1] = 0
                        game.field_weight.sequence[x + 1][y] *= 3
                        if y + 1 < 10:
                            game.field_weight.sequence[x + 1][y + 1] = 0

    # метод возвращает список координат с самым большим коэффициентом шанса попадения
    def get_weights(self):
        self.weights = []
        # просто пробегаем по всем клеткам и заносим в список клетки с коэффициентом больше 3
        for x in range(10):
            for y in range(10):
                if game.field_weight.sequence[x][y] >= 3:
                    self.weights.append((x, y))
        return self.weights


class Player:
    """
    Класс игроков
    """
    def __init__(self, name, auto):
        self.name = name
        self.auto = auto
        self.list_ships = []  # список кораблей игрока
        self.occupied = []  # список занятых ячеек

    def __str__(self):
        return self.name


class Game:
    """
    Класс игры
    """
    def __init__(self, player1, player2):
        self.current_player = player1
        self.next_player = player2
        self.field_radar = Board()
        self.field_user = Board()
        self.field_comp = Board()
        self.field_weight = Board()
        self.message = 'test'

    def start_game(self):
        self.clear_screen()
        print('\n\n\n\t\033[1;033m"Морской бой"'.expandtabs(tabsize=30))
        print('\tРасстановка кораблей игроков автоматическая.\n\n\n'.expandtabs(tabsize=15))
        start = input('Начать игру (y), выйти (n): \033[0m')
        if start == 'y':
            self.clear_screen()
            self.install_ship_by_player()
            self.game_shot()
        elif start == 'n':
            self.clear_screen()
            print('\n\nВы вышли из игры.\033[0m')
        else:
            print('\033[1;033m\n\nПовторите выбор режима.\033[0m')
            time.sleep(2)
            self.start_game()

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    def install_ship_by_player(self):

        # установка кораблей первого игрока
        for len_ship in Ship.ships_rules:
            while True:
                ship = Ship(len_ship)
                ship.install_ship(self.field_user, self.current_player.occupied, ship, self.current_player)
                if ship.setup:
                    ship.occupied_board(self.field_user, self.current_player.occupied)
                    break

        # установка кораблей второго игрока
        for len_ship in Ship.ships_rules:
            while True:
                ship = Ship(len_ship)
                ship.install_ship(self.field_comp, self.next_player.occupied, ship, self.next_player)
                if ship.setup:
                    ship.occupied_board(self.field_comp, self.next_player.occupied)
                    break

        # печать игровых полей
        self.field_radar.print_board()

    # метод для производства выстрела и обработки результатов
    def game_shot(self):

        shot = Shot()

        if not self.current_player.auto:
            while len(self.next_player.list_ships) > 0:
                print('\033[1;36mХод:', self.current_player)
                shot.shot_by_ships(self.next_player, self.field_comp)
                if game.message == 'miss':
                    print('\033[1;33mПромах!', 'Переход хода...')
                    game.field_radar.print_board()
                    self.switch_players()
                    return self.game_shot()
                if game.message == 'get':
                    print('\033[1;33mПопадание!', 'Еще выстрел...')
                if game.message == 'kill':
                    print('\033[1;33mКорабль уничтожен!', 'Ура!')
                game.field_radar.print_board()
            print('\033[1;31mВсе корабли потоплены. Вы выиграли!\033[0m')

        elif self.current_player.auto:
            while len(self.next_player.list_ships) > 0:
                print('\033[1;36mХод:', str(self.current_player) + ': ', end='')
                shot.shot_by_ships_auto(self.next_player, self.field_user)
                if game.message == 'miss':
                    print('\033[1;33mПромах!', 'Переход хода...')
                    game.field_radar.print_board()
                    self.switch_players()
                    return self.game_shot()
                if game.message == 'get':
                    print('\033[1;33mПопадание!', 'Еще выстрел...')
                if game.message == 'kill':
                    print('\033[1;33mВаш корабль уничтожен!', 'Соболезную...')

                game.field_radar.print_board()
            print('\033[1;31mВсе корабли потоплены. Выиграл компьютер!\033[0m')

    # метод для смены хода игроков
    def switch_players(self):
        self.current_player, self.next_player = self.next_player, self.current_player


if __name__ == "__main__":
    players = [Player(name='User', auto=False), Player(name='Computer', auto=True)]
    # print(players[0], players[1])

    game = Game(players[0], players[1])
    game.start_game()
