# ---------------------------------------------------------------- #

import csv
import webbrowser
import pygame as pg

from widgets.single import *
from widgets.utils  import *
from widgets.multi  import *

from classes import *

from colors import *

# ---------------------------------------------------------------- #

SCREEN_MIN_WIDTH = 1920 // 2
SCREEN_MIN_HEIGHT = 1080 // 2
SCREEN_MIN_DIMENSIONS = (SCREEN_MIN_WIDTH, SCREEN_MIN_HEIGHT)

COLOR_BG = colors["light light grey"]

FONT_TYPE = "ClearSans-Bold.ttf"

DELAY = 10

# ---------------------------------------------------------------- #

pg.init()

pg.display.set_caption("Tic-Tac-Toe")

screen = pg.display.set_mode(SCREEN_MIN_DIMENSIONS, pg.RESIZABLE)
screen.fill(COLOR_BG)

icon = pg.image.load("icon.png")
pg.display.set_icon(icon)

# ---------------------------------------------------------------- #

def statistics(screen):

    statistics_dict = {}
    with open("statistics.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for line in csv_reader:
            key = tuple(line)
            if key not in statistics_dict.keys():
                statistics_dict[key] = 1
            else:
                statistics_dict[key] += 1

    pages = []
    page = []
    counter = 0
    for (winner, loser, dimension), multiplicity in statistics_dict.items():

        if counter % 5 == 0:
            page = ["winner", "loser", "dimension", "multiplicity"]

        page += [winner, loser, str(dimension), str(multiplicity)]

        if counter % 5 == 4:
            pages.append(page)
            page = []

        counter += 1

    if page != []: pages.append(page)

    button_menu = Button(screen, "button menu", width=256, height=64,
                         filling_color=colors[128],
                         border_radius=4,
                         text_string="Menu", text_color=colors["white"],
                         font_type=FONT_TYPE, font_size=40,
                         response="hold",
                         filling_color_semiclicked=colors["green"],
                         unclickable_outside=False)

    boxes_statistics = Boxes(screen, name="boxes statistics",
                             grid_amount_rows=12, grid_amount_columns=4,
                             members=[button_menu],
                             mapping_position={"button menu": (1, 9)},
                             mapping_nudge="inner")

    page_index = 0

    if len(pages) > 0:

        members = [
            Label(screen, name, width=0, height=0,
                    text_string=name.capitalize(), text_color=colors["white"],
                    font_type=FONT_TYPE, font_size=32)
            for name in pages[page_index]
        ]
        mapping_position = {n: (n % 4, n // 4) for n in range(len(pages[page_index]))}

        table = Labels(screen, "table", width=512+256, height=512-128,
                       anchor="center",
                       grid_amount_rows=7, grid_amount_columns=5,
                       grid_drawing_style="lines inner dashed", grid_drawing_color=COLOR_BG,
                       members=members, mapping_position=mapping_position,
                       mapping_nudge="inner", filling_color=colors["dark grey"],
                       border_radius=4,
                       drawing=True)

        button_next = Button(screen, "button next", width=256, height=64,
                            filling_color=colors[128],
                            border_radius=4,
                            text_string=f"Next to 1", text_color=colors["white"],
                            font_type=FONT_TYPE, font_size=40,
                            response="hold",
                            filling_color_semiclicked=colors["green"],
                            unclickable_outside=False)

        button_back = Button(screen, "button back", width=256, height=64,
                            filling_color=colors[128],
                            border_radius=4,
                            text_string=f"Back to 0", text_color=colors["white"],
                            font_type=FONT_TYPE, font_size=40,
                            response="hold",
                            filling_color_semiclicked=colors["green"],
                            unclickable_outside=False)

        boxes_statistics.members += [button_back, button_next, table]
        boxes_statistics.mapping["position"].update({"button back": (0, 9), "button next": (2, 9), "table": (1, 4)})

    back_active = False
    next_active = len(pages) > 1
    table_active = len(pages) > 0

    boxes_statistics.width = screen.get_width()
    boxes_statistics.height = screen.get_height()

    boxes_statistics.update_members_position()
    boxes_statistics.update_members_bound()

    if table_active:
        table.update_members_position()
        table.update_members_bound()

    run = True
    while run:

        pg.time.delay(DELAY)

        pg.display.update()
        screen.fill(COLOR_BG)

        button_menu.draw()
        if back_active: button_back.draw()
        if next_active: button_next.draw()
        if table_active:
            table.draw()
            pg.draw.line(screen, COLOR_BG, table.grid_actually[0, 1], table.grid_actually[4, 1], 4)

        for event in pg.event.get():

            if event.type == pg.QUIT: run = False

            if event.type == pg.VIDEORESIZE:

                    width, height = event.size

                    if width < SCREEN_MIN_WIDTH: width = SCREEN_MIN_WIDTH
                    if height < SCREEN_MIN_HEIGHT: height = SCREEN_MIN_HEIGHT

                    screen = pg.display.set_mode((width, height), pg.RESIZABLE)

                    boxes_statistics.width = screen.get_width()
                    boxes_statistics.height = screen.get_height()

                    boxes_statistics.update_members_position()
                    boxes_statistics.update_members_bound()

                    if table_active:
                        table.update_members_position()
                        table.update_members_bound()

            button_menu.update(event)
            if back_active: button_back.update(event)
            if next_active: button_next.update(event)

            if button_menu.clicked(event):
                return run, screen

            if next_active:
                if button_next.clicked(event):

                    page_index += 1

                    table.members = [
                        Label(screen, name, width=0, height=0,
                                text_string=name.capitalize(), text_color=colors["white"],
                                font_type=FONT_TYPE, font_size=32)
                        for name in pages[page_index]
                    ]
                    table.mapping["position"] = {n: (n % 4, n // 4) for n in range(len(pages[page_index]))}
                    table.update_members_position()

                    button_back.text_string = f"Back to {page_index-1}"
                    button_next.text_string = f"Next to {page_index+1}"

                    if page_index == 0:
                        back_active = False
                        next_active = True
                        button_next.draw()
                    else:
                        if page_index == len(pages)-1:
                            back_active = True
                            next_active = False
                            button_back.draw()
                        else:
                            back_active = True
                            next_active = True
                            button_back.draw()
                            button_next.draw()

            if back_active:
                if button_back.clicked(event):

                    page_index -= 1

                    table.members = [
                        Label(screen, name, width=0, height=0,
                                text_string=name.capitalize(), text_color=colors["white"],
                                font_type=FONT_TYPE, font_size=32)
                        for name in pages[page_index]
                    ]
                    table.mapping["position"] = {n: (n % 4, n // 4) for n in range(len(pages[page_index]))}
                    table.update_members_position()

                    button_back.text_string = f"Back to {page_index-1}"
                    button_next.text_string = f"Next to {page_index+1}"

                    if page_index == 0:
                        back_active = False
                        next_active = True
                        button_next.draw()
                    else:
                        if page_index == len(pages)-1:
                            back_active = True
                            next_active = False
                            button_back.draw()
                        else:
                            back_active = True
                            next_active = True
                            button_back.draw()
                            button_next.draw()

    return run, screen

def award_ceremony(screen, dimension, players):

    winner = None
    first = False
    if players[0].score["amount"] > players[1].score["amount"]: winner = 0
    if players[0].score["amount"] < players[1].score["amount"]: winner = 1
    if players[0].score["amount"] == players[1].score["amount"]:
        for i in [0, 1]:
            if players[i].score["first"]:
                winner = i
                first = True

    if winner == None: text_string = "The game was a draw."
    else:

        loser = 1 - winner
        text_string = f"{players[winner].name} won against {players[loser].name} in {dimension} dimensions!"
        if dimension in [3, 4]:
            text_string = text_string.replace("!", f" {players[winner].score['amount']} to {players[loser].score['amount']}!")
        if first:
            text_string += ("\n" + f"{players[winner].name} scored first!")

        with open("statistics.csv", "a") as csv_file:
            csv_file.write("\n" + ",".join([players[winner].name, players[loser].name, str(dimension)]))

    label_anouncement = Label(screen, "label anouncement", width=256, height=128,
                              filling_color=COLOR_BG,
                              text_string=text_string, font_size=40,
                              font_type=FONT_TYPE)

    buttons_move = Buttons(screen, "buttons move",
                           grid_amount_columns=2,
                           members=[Button(screen, name, width=256, height=64,
                                           filling_color=colors[128],
                                           border_radius=4,
                                           text_string=name.capitalize(), text_color=colors["white"],
                                           font_type=FONT_TYPE, font_size=40,
                                           response="hold",
                                           filling_color_semiclicked=colors["green"],
                                           unclickable_outside=False)
                                       for name in ["menu", "statistics"]],
                           mapping_position={0: (0, 0), 1: (1, 0)})

    boxes_award_ceremony = Boxes(screen, name="boxes award ceremony",
                                 grid_amount_rows=4, grid_amount_columns=5,
                                 members=[label_anouncement, buttons_move],
                                 mapping_position={"label anouncement": (2, 1), "buttons move": (1, 2)},
                                 mapping_bound={"buttons move": (3, 2)})

    boxes_award_ceremony.width = screen.get_width()
    boxes_award_ceremony.height = screen.get_height()

    boxes_award_ceremony.update_members_position()
    boxes_award_ceremony.update_members_bound()

    for member in boxes_award_ceremony.members:
        if "update_members_position" in dir(member):
            member.update_members_position()
        if "update_members_bound" in dir(member):
            member.update_members_bound()

    run = True
    while run:

        pg.time.delay(DELAY)

        pg.display.update()
        screen.fill(COLOR_BG)

        boxes_award_ceremony.draw()

        for event in pg.event.get():

            if event.type == pg.QUIT: run = False

            if event.type == pg.VIDEORESIZE:

                    width, height = event.size

                    if width < SCREEN_MIN_WIDTH: width = SCREEN_MIN_WIDTH
                    if height < SCREEN_MIN_HEIGHT: height = SCREEN_MIN_HEIGHT

                    screen = pg.display.set_mode((width, height), pg.RESIZABLE)

                    boxes_award_ceremony.width = screen.get_width()
                    boxes_award_ceremony.height = screen.get_height()

                    boxes_award_ceremony.update_members_position()
                    boxes_award_ceremony.update_members_bound()

            buttons_move.update(event)

            if buttons_move["menu"].clicked(event):
                return run, screen

            if buttons_move["statistics"].clicked(event):
                return statistics(screen)

    return run, screen

def play(screen, dimension, players):

    board = Board(screen, "board", dimension=dimension)
    game = Game(board, players)

    quit_game = Button(screen, "quit game", width=256, height=64,
                       border_radius=4,
                       text_string="Quit Game", text_color=colors["white"],
                       font_type=FONT_TYPE, font_size=36,
                       response="hold",
                       filling_color_unclicked=colors["grey"], filling_color_semiclicked=colors[32])

    if dimension == 2:
        text_strings = [players[i].name for i in [0, 1]]
    if dimension in [3, 4]:
        text_strings = [players[i].score_string for i in [0, 1]]

    player_labels = [
        Label(screen, f"player {i} label", width=256, height=64,
              filling_color=COLOR_BG,
              text_string=text_strings[i], font_type=FONT_TYPE, font_size=36)
        for i in [0, 1]
    ]

    if dimension in [2, 3]:
        grid_amount_rows = 8
        grid_amount_columns = 4
        members = [board, quit_game, player_labels[0], player_labels[1]]
        mapping_position = {0: (1, 2), 1: (1, 5), 2: (0, 5), 3: (2, 5)}

    if dimension == 4:
        # screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        grid_amount_rows = 4
        grid_amount_columns = 32
        members = [board, quit_game, player_labels[0], player_labels[1]]
        mapping_position = {0: (10, 1), 1: (26, 1), 2: (26, 0), 3: (26, 2)}

    boxes_play = Boxes(screen, "boxes play",
                       grid_amount_rows=grid_amount_rows, grid_amount_columns=grid_amount_columns,
                       members=members, mapping_position=mapping_position,
                       mapping_nudge="inner")

    boxes_play.width = screen.get_width()
    boxes_play.height = screen.get_height()

    boxes_play.update_members_position()
    boxes_play.update_members_bound()

    for member in boxes_play.members:
        if "update_members_position" in dir(member):
            member.update_members_position()
        if "update_members_bound" in dir(member):
            member.update_members_bound()

    run = True
    while run:

        pg.time.delay(DELAY)

        pg.display.update()
        screen.fill(COLOR_BG)

        draw(boxes_play)

        for event in pg.event.get():

            if event.type == pg.QUIT: run = False

            if event.type == pg.VIDEORESIZE:

                    width, height = event.size

                    if width < SCREEN_MIN_WIDTH: width = SCREEN_MIN_WIDTH
                    if height < SCREEN_MIN_HEIGHT: height = SCREEN_MIN_HEIGHT

                    screen = pg.display.set_mode((width, height), pg.RESIZABLE)

                    boxes_play.width = screen.get_width()
                    boxes_play.height = screen.get_height()

                    boxes_play.update_members_position()
                    boxes_play.update_members_bound()

            quit_game.update(event)
            field = game.update(event)
            if field is not None: field.draw()

            for i in [0, 1]:

                if dimension == 2:
                    player_labels[i].text_string = players[i].name
                if dimension in [3, 4]:
                    player_labels[i].text_string = players[i].score_string

                if i == game.turn:
                    player_labels[i].text_color = colors["green"]
                else:
                    player_labels[i].text_color = colors[32]

            if not game.run:
                return award_ceremony(screen, dimension, players)

            if quit_game.clicked(event):
                return run, screen

    return run, screen

def setup(screen):

    description_names = Label(screen, "description names", width=400, height=20,
                              filling_color=COLOR_BG,
                              text_string="Please enter your player names ...", text_color=colors["grey"],
                              font_type=FONT_TYPE, font_size=40)

    text_boxes_players = TextBoxes(screen, "text boxes players",
                                   grid_amount_columns=2,
                                   members=[TextBox(screen, f"text box player {i}",  width=256, height=64,
                                                    filling_color=COLOR_BG,
                                                    border_radius=4, border_thickness=6,
                                                    font_type=FONT_TYPE, font_size=36,
                                                    border_color_unclicked=colors[32], border_color_semiclicked=colors[128], border_color_clicked=colors["green"],
                                                    text_color_unclicked=colors[32], text_color_semiclicked=colors[128], text_color_clicked=colors["green"])
                                               for i in [0, 1]],
                                   mapping_position={0: (0, 0), 1: (1, 0)})

    description_dimension = Label(screen, "description dimension", width=400, height=20,
                                  filling_color=COLOR_BG,
                                  text_string="Please select the dimension that you want to play with ...", text_color=colors["grey"],
                                  font_type=FONT_TYPE, font_size=40)

    buttons_dimension = Buttons(screen, "buttons dimension",
                                grid_amount_columns=3,
                                members=[Button(screen, f"button dimension {n}", width=64, height=64,
                                                border_radius=4,
                                                text_string=str(n), text_color=colors["white"],
                                                font_type=FONT_TYPE, font_size=40,
                                                filling_color_unclicked=colors[32], filling_color_semiclicked=colors[128], filling_color_clicked=colors["green"],
                                                unclickable_outside=False)
                                        for n in [2, 3, 4]],
                                mapping_position={n: (n, 0) for n in range(3)})

    buttons_move = Buttons(screen, "buttons move",
                           grid_amount_columns=2,
                           members=[Button(screen, f"button move {direction}", width=256, height=64,
                                           filling_color=colors[128],
                                           border_radius=4,
                                           text_string=direction.capitalize(), text_color=colors["white"],
                                           font_type=FONT_TYPE, font_size=40,
                                           response="hold",
                                           filling_color_semiclicked=colors["green"],
                                           unclickable_outside=False)
                                       for direction in ["back", "next"]],
                           mapping_position={0: (0, 0), 1: (1, 0)})

    boxes_setup = Boxes(screen, name="boxes setup",
                        grid_amount_rows=14, grid_amount_columns=7,
                        members=[description_names, text_boxes_players, description_dimension, buttons_dimension, buttons_move],
                        mapping_position={
                                                          "description names":     (3, 2),
                            "text boxes players": (2, 4),
                                                          "description dimension": (3, 6),
                            "buttons dimension": (2, 8),
                            "buttons move":      (2, 11),
                        },
                        mapping_bound={
                            "text boxes players": (4, 4),
                            "buttons dimension":  (4, 8),
                            "buttons move":       (4, 11),
                        })

    boxes_setup.width = screen.get_width()
    boxes_setup.height = screen.get_height()

    boxes_setup.update_members_position()
    boxes_setup.update_members_bound()

    for member in boxes_setup.members:
        if "update_members_position" in dir(member):
            member.update_members_position()
        if "update_members_bound" in dir(member):
            member.update_members_bound()

    buttons_dimension.member_clicked_index = 0

    run = True
    while run:

        pg.time.delay(DELAY)

        pg.display.update()
        screen.fill(COLOR_BG)

        boxes_setup.draw()

        for event in pg.event.get():

            if event.type == pg.QUIT: run = False

            if event.type == pg.VIDEORESIZE:

                    width, height = event.size

                    if width < SCREEN_MIN_WIDTH: width = SCREEN_MIN_WIDTH
                    if height < SCREEN_MIN_HEIGHT: height = SCREEN_MIN_HEIGHT

                    screen = pg.display.set_mode((width, height), pg.RESIZABLE)

                    boxes_setup.width = screen.get_width()
                    boxes_setup.height = screen.get_height()

                    boxes_setup.update_members_position()
                    boxes_setup.update_members_bound()

            boxes_setup.update(event)

            if buttons_move["button move back"].clicked(event):
                return run, screen

            if buttons_move["button move next"].clicked(event):

                player_names = [
                    text_boxes_players[i].text_string
                    for i in [0, 1]
                ]

                if player_names[0] == "" and player_names[1] == "":
                    player_names = ["Alice", "Bob"]

                if "" not in player_names:
                    players = [Player(player_names[i]) for i in [0, 1]]
                    return play(screen, buttons_dimension.member_clicked_index+2, players)
    
    return run, screen

def menu(screen):

    title = Label(screen, "title", width=400, height=40,
                  filling_color=COLOR_BG,
                  text_string="Tic-Tac-Toe", text_color=colors["dark grey"],
                  font_type=FONT_TYPE, font_size=80)

    sub_title = Label(screen, "sub title", width=400, height=20,
                filling_color=COLOR_BG,
                text_string="... in 2, 3 and 4 dimensions", text_color=colors["light grey"],
                font_type=FONT_TYPE, font_size=40)

    menu_buttons = Buttons(screen, "menu buttons",
                           grid_amount_rows=2, grid_amount_columns=2,
                           members=[Button(screen, button_name.lower(), width=256, height=64,
                                           filling_color=colors[128],
                                           border_radius=4,
                                           text_string=button_name.capitalize(), text_color=colors["white"],
                                           filling_color_semiclicked=colors["green"],
                                           font_type=FONT_TYPE, font_size=36,
                                           response="hold")
                                    for i, button_name in enumerate(["play", "tutorial", "statistics", "toggle screen"])],
                           mapping_position={0: (0, 0), 1: (0, 1), 2: (1, 0), 3: (1, 1)})

    quit = Button(screen, "quit", width=256, height=64,
                  border_radius=4,
                  text_string="Quit", text_color=colors["white"],
                  font_type=FONT_TYPE, font_size=36,
                  response="hold",
                  filling_color_unclicked=colors["grey"], filling_color_semiclicked=colors[32])

    boxes_menu = Boxes(screen, name="boxes menu",
                       grid_amount_rows=12, grid_amount_columns=7,
                       members=[title, sub_title, menu_buttons, quit],
                       mapping_position={
                                           "title":     (3, 2),
                                           "sub title": (3, 3),
                           "menu buttons": (2, 5),
                                           "quit": (3, 9),
                       },
                       mapping_bound={"menu buttons": (4, 7)})

    boxes_menu.update_members_position()
    boxes_menu.update_members_bound()

    menu_buttons.update_members_position()
    menu_buttons.update_members_bound()

    screen_state = "small"

    run = True
    while run:

        pg.time.delay(DELAY)

        pg.display.update()
        screen.fill(COLOR_BG)

        boxes_menu.draw()

        for event in pg.event.get():

            if event.type == pg.QUIT or quit.clicked(event): run = False

            if event.type == pg.VIDEORESIZE:

                    width, height = event.size
                    
                    if width < SCREEN_MIN_WIDTH: width = SCREEN_MIN_WIDTH
                    if height < SCREEN_MIN_HEIGHT: height = SCREEN_MIN_HEIGHT

                    screen = pg.display.set_mode((width, height), pg.RESIZABLE)

                    boxes_menu.width = screen.get_width()
                    boxes_menu.height = screen.get_height()

                    boxes_menu.update_members_position()
                    boxes_menu.update_members_bound()

            boxes_menu.update(event)

            if menu_buttons["tutorial"].clicked(event):
                link = r"https://www.overleaf.com/read/mppftycggjyj"
                webbrowser.open(link)

            if menu_buttons["toggle screen"].clicked(event):

                if screen_state == "small":
                    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
                    screen_state = "full"
                elif screen_state == "full":
                    screen = pg.display.set_mode(SCREEN_MIN_DIMENSIONS, pg.RESIZABLE)
                    screen_state = "small"

                boxes_menu.width = screen.get_width()
                boxes_menu.height = screen.get_height()

                boxes_menu.update_members_position()
                boxes_menu.update_members_bound()

                menu_buttons.update_members_position()
                menu_buttons.update_members_bound()

                break

            for button_name, function in zip(["play", "statistics"],
                                             [setup, statistics]):
                if menu_buttons[button_name].clicked(event):

                    run = function(screen)

                    boxes_menu.width = screen.get_width()
                    boxes_menu.height = screen.get_height()

                    boxes_menu.update_members_position()
                    boxes_menu.update_members_bound()

                    menu_buttons.update_members_position()
                    menu_buttons.update_members_bound()

                    break

    pg.quit()

# ---------------------------------------------------------------- #

if __name__ == "__main__":
    menu(screen)

# ---------------------------------------------------------------- #
