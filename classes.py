# ---------------------------------------------------------------- #

import pygame as pg
import numpy  as np

from widgets.single import *
from widgets.utils  import *
from widgets.multi  import *

from colors import *

# ---------------------------------------------------------------- #

COLOR_BG = colors["light light grey"]
FONT_TYPE = "ClearSans-Bold.ttf"

# ---------------------------------------------------------------- #

class Board(Labels):

    def __init__(self, surface, name, x=0, y=0,
                 scale_width=1, scale_height=1, anchor="center",
                 dimension=2):

        self.dimension = dimension

        if self.dimension == 2:

            width = height = 256
            border_radius = 4
            grid_amount_columns = 4
            grid_amount_rows = 4
            grid_drawing_style = "lines inner dashed"
            grid_drawing_color = COLOR_BG
            filling_color = colors["grey"]
            members = [
                Button(surface, f"field ({n // 3}, {n % 3})", width=64, height=64,
                       border_radius=4,
                       filling_color=colors["light grey"],
                       text_color=colors["white"], font_type=FONT_TYPE, font_size=64,
                       response="hold")
                for n in range(9)
            ]
            mapping_position = {n: (n // 3, n % 3) for n in range(9)}
            mapping_nudge = "inner"
            drawing = True

        if self.dimension == 3:

            width = 1024 - 128 - 64
            height = 256 + 16 + 4
            border_radius = 4
            grid_amount_columns = 4
            grid_amount_rows = 2
            grid_drawing_style = "lines inner dashed"
            grid_drawing_color = COLOR_BG
            filling_color = colors["dark grey"]
            members = [
                Board(surface, f"subboard {n}", dimension=2)
                for n in range(3)
            ]
            mapping_position = {n: (n, 0) for n in range(3)}
            mapping_nudge = "inner"
            drawing = True

        if self.dimension == 4:

            width = height = 1024 - 128 - 64
            border_radius = 4
            grid_amount_columns = 4
            grid_amount_rows = 4
            grid_drawing_style = "lines inner dashed"
            grid_drawing_color = COLOR_BG
            filling_color = colors["dark grey"]
            members = [
                Board(surface, f"subboard ({n // 3}, {n % 3})", dimension=2)
                for n in range(9)
            ]
            mapping_position = {n: (n // 3, n % 3) for n in range(9)}
            mapping_nudge = "inner"
            drawing = True

        super().__init__(surface, name, x, y, width, height,
                         scale_width, scale_height, anchor,
                         grid_amount_rows=grid_amount_rows, grid_amount_columns=grid_amount_columns, grid_nudge=None,
                         grid_drawing_style=grid_drawing_style, grid_drawing_color=grid_drawing_color, grid_drawing_nudge=None,
                         members=members, mapping_position=mapping_position, mapping_bound=None, mapping_nudge=mapping_nudge,
                         filling_color=filling_color,
                         border_thickness=0, border_radius=border_radius, border_color=pg.Color("black"),
                         text_string="", text_color=pg.Color("black"),
                         font_type="arial", font_size=24,
                         drawing=drawing)

    def get_field_coordinates(self, field, subboard=None):

        if self.dimension == 2:
            i = int(field.name[7])
            j = int(field.name[10])
            return i, j

        if self.dimension == 3:
            assert subboard is not None
            k = int(subboard.name[9])
            i, j = self[k].get_field_coordinates(field)
            return i, j, k

        if self.dimension == 4:
            assert subboard is not None
            k = int(subboard.name[10])
            l = int(subboard.name[13])
            i, j = self[k, l].get_field_coordinates(field)
            return i, j, k, l

    def __getitem__(self, coordinates):

        if type(coordinates) is int:
            return self.members[coordinates]

        if type(coordinates) in [list, tuple, np.ndarray]:

            if self.dimension == 2:
                i, j = coordinates
                return self.members[3*i + j]

            if self.dimension == 3:
                i, j, k = coordinates
                return self.members[k][i, j]

            if self.dimension == 4:
                if len(coordinates) == 2:
                    k, l = coordinates
                    return self.members[3*k + l]
                if len(coordinates) == 4:
                    i, j, k, l = coordinates
                    return self[k, l][i, j]

    def update(self, event):
        
        self.update_members_position()
        self.update_members_bound()

        for member in self.members:
            if not self.body["outer"].collidepoint(pg.mouse.get_pos()):
                member.update(event)

class Player(object):

    def __init__(self, name):
        self.name = name
        self.score = {"amount": 0, "first": False}

    @property
    def score_string(self):
        return f"{self.name}\'s score ... {self.score['amount']}" + "*" * self.score["first"]

class Game(object):

    atomic_lists = {
        "up":   [0, 1, 2],
        "down": [2, 1, 0],
        "constant 0": [0, 0, 0],
        "constant 1": [1, 1, 1],
        "constant 2": [2, 2, 2],
    }

    def __init__(self, board, players, symbols=None):

        if symbols is None: symbols = ["+", "-"]

        self.board = board
        self.players = players
        self.symbols = symbols

        self.turn = 0
        self.scored = False
        self.occupied_fields = 0

    @property
    def dimension(self):
        return self.board.dimension

    @property
    def run(self):
        if self.occupied_fields >= 3 ** self.dimension:
            return False
        if self.dimension == 2:
            return True not in [player.score["first"] for player in self.players]
        return True

    def switch_turn(self):
        self.turn = (self.turn + 1) % 2

    @property
    def symbol_turn(self):
        return self.symbols[self.turn]

    @property
    def player_turn(self):
        return self.players[self.turn]

    def increase_score(self):

        self.player_turn.score["amount"] += 1/2

        if not self.scored:
            self.player_turn.score["first"] = True
            self.scored = True

    def update_score_inner(self, field_coordinates, types, atomic_lists):
        if "up" in types or "down" in types:
            coordinates_list = list(zip(*atomic_lists))
            if field_coordinates in coordinates_list:

                increase_score = True

                for coordinates in coordinates_list:
                    if self.board[coordinates].text_string != self.symbol_turn:
                        increase_score = False

                if increase_score:
                    self.increase_score()

    def update_score(self, field_coordinates):
        
        if self.dimension == 2:
            for type_1, atomic_list_1 in Game.atomic_lists.items():
                for type_2, atomic_list_2 in Game.atomic_lists.items():
                    types = [type_1, type_2]
                    atomic_lists = [atomic_list_1, atomic_list_2]
                    self.update_score_inner(field_coordinates, types, atomic_lists)

        if self.dimension == 3:
            for type_1, atomic_list_1 in Game.atomic_lists.items():
                for type_2, atomic_list_2 in Game.atomic_lists.items():
                    for type_3, atomic_list_3 in Game.atomic_lists.items():
                        types = [type_1, type_2, type_3]
                        atomic_lists = [atomic_list_1, atomic_list_2, atomic_list_3]
                        self.update_score_inner(field_coordinates, types, atomic_lists)

        if self.dimension == 4:
            for type_1, atomic_list_1 in Game.atomic_lists.items():
                for type_2, atomic_list_2 in Game.atomic_lists.items():
                    for type_3, atomic_list_3 in Game.atomic_lists.items():
                        for type_4, atomic_list_4 in Game.atomic_lists.items():
                            types = [type_1, type_2, type_3, type_4]
                            atomic_lists = [atomic_list_1, atomic_list_2, atomic_list_3, atomic_list_4]
                            self.update_score_inner(field_coordinates, types, atomic_lists)
        
        self.player_turn.score["amount"] = int(self.player_turn.score["amount"])

    def update(self, event):

        if self.dimension == 2:
            for field in self.board.members:
                if field.clicked(event) and field.text_string == "":
                    field.text_string = self.symbol_turn
                    self.occupied_fields += 1
                    field_coordinates = self.board.get_field_coordinates(field)
                    self.update_score(field_coordinates)
                    self.switch_turn()
                    return field

        if self.dimension in [3, 4]:
            for subboard in self.board.members:
                if subboard.body["outer"].collidepoint(pg.mouse.get_pos()):
                    for field in subboard.members:
                        if field.clicked(event) and field.text_string == "":
                            field.text_string = self.symbol_turn
                            self.occupied_fields += 1
                            field_coordinates = self.board.get_field_coordinates(field, subboard)
                            self.update_score(field_coordinates)
                            self.switch_turn()
                            return field

# ---------------------------------------------------------------- #
