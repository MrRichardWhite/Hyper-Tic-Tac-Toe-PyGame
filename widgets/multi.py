# ---------------------------------------------------------------- #

from msilib.schema import Error
import pygame as pg
import numpy  as np

from widgets.single import *
from widgets.utils  import *

# ---------------------------------------------------------------- #

class Boxes(Box):

    def __init__(self, surface, name, x=0, y=0, width=None, height=None,
                 scale_width=1, scale_height=1, anchor="north west",
                 grid_amount_rows=1, grid_amount_columns=1, grid_nudge=None,
                 grid_drawing_style=None, grid_drawing_color=pg.Color("black"), grid_drawing_nudge=None,
                 members=None, mapping_position=None, mapping_bound=None, mapping_nudge=None):

        if members is None: members = []
        if mapping_position is None: mapping_position = {}
        if mapping_bound is None: mapping_bound = {}

        super().__init__(surface, name, x, y, width, height,
                         scale_width, scale_height, anchor)

        self.grid = {"amount": {"rows" : grid_amount_rows, "columns": grid_amount_columns},
                     "nudge": grid_nudge,
                     "drawing": {"style": grid_drawing_style, "color": grid_drawing_color, "nudge": grid_drawing_nudge}}

        self.members = list(members)
        self.mapping = {"position": mapping_position, "bound": mapping_bound, "nudge": mapping_nudge}


    @property
    def grid_actually(self):

        if self.grid["nudge"] is None:
            return Grid(self.surface, self.name + " " + "grid", self.x, self.y, self.width, self.height,
                        self.scale["width"], self.scale["height"], self.anchor,
                        self.grid["amount"]["rows"], self.grid["amount"]["columns"],
                        self.grid["drawing"]["style"], self.grid["drawing"]["color"], self.grid["drawing"]["nudge"])

        if self.grid["nudge"] == "inner":
            return Grid(self.surface, self.name + " " + "grid", self.x, self.y, self.width, self.height,
                        self.scale["width"], self.scale["height"], self.anchor,
                        self.grid["amount"]["rows"]+1, self.grid["amount"]["columns"]+1,
                        self.grid["drawing"]["style"], self.grid["drawing"]["color"], self.grid["drawing"]["nudge"]).inner

        if self.grid["nudge"] == "outer":
            return Grid(self.surface, self.name + " " + "grid", self.x, self.y, self.width, self.height,
                        self.scale["width"], self.scale["height"], self.anchor,
                        self.grid["amount"]["rows"]-1, self.grid["amount"]["columns"]-1,
                        self.grid["drawing"]["style"], self.grid["drawing"]["color"], self.grid["drawing"]["nudge"]).outer

    @property
    def amount(self):
        return len(self.members)

    def update_members_position(self, mapping_position=None):

        if mapping_position is None:
            if self.mapping["nudge"] == None:
                mapping_position = {key: self.grid_actually[j][i] for key, (i, j) in self.mapping["position"].items()}
            elif self.mapping["nudge"] == "inner":
                mapping_position = {key: self.grid_actually.inner[j][i] for key, (i, j) in self.mapping["position"].items()}
            elif self.mapping["nudge"] == "outer":
                mapping_position = {key: self.grid_actually.outer[j][i] for key, (i, j) in self.mapping["position"].items()}

        for key, value in mapping_position.items():
            self[key].position = value

        for member in self.members:
            if "update_members_position" in dir(member):
                member.update_members_position()

    def update_members_bound(self, mapping_bound=None):

        if mapping_bound is None:
            mapping_bound = {key: self.grid_actually[j][i] for key, (i, j) in self.mapping["bound"].items()}

        for key, value in mapping_bound.items():
            self[key].bound = value

        for member in self.members:
            if "update_members_bound" in dir(member):
                member.update_members_bound()

    def __getitem__(self, key):

        if type(key) in [int, np.int32]:
            return self.members[key]

        if type(key) == str:
            for member in self.members:
                if member.name == key:
                    return member

        raise IndexError(f"{key} could not be found")

    def __setitem__(self, key, value):

        if type(key) in [int, np.int32]:
            self.members[key] = value

        if type(key) == str:
            for n, member in enumerate(self.members):
                if member.name == key:
                    self.members[n] = value

    def draw(self):
        self.grid_actually.draw()
        draw(self.members)

    def update(self, event):
        self.update_members_position()
        self.update_members_bound()
        update(self.members, event)

class Labels(Boxes, Label):

    def __init__(self, surface, name, x=0, y=0, width=None, height=None,
                 scale_width=1, scale_height=1, anchor="north west",
                 grid_amount_rows=1, grid_amount_columns=1, grid_nudge=None,
                 grid_drawing_style=None, grid_drawing_color=pg.Color("black"), grid_drawing_nudge=None,
                 members=None, mapping_position=None, mapping_bound=None, mapping_nudge=None,
                 filling_color=pg.Color("white"),
                 border_thickness=0, border_radius=0, border_color=pg.Color("black"),
                 text_string="", text_color=pg.Color("black"),
                 font_type="arial", font_size=24,
                 drawing=False):

        Boxes.__init__(self, surface, name, x, y, width, height,
                       scale_width, scale_height, anchor,
                       grid_amount_rows, grid_amount_columns, grid_nudge,
                       grid_drawing_style, grid_drawing_color, grid_drawing_nudge,
                       members, mapping_position, mapping_bound, mapping_nudge)

        Label.__init__(self, surface, name, x, y, width, height,
                       scale_width, scale_height, anchor,
                       filling_color,
                       border_thickness, border_radius, border_color,
                       text_string, text_color,
                       font_type, font_size)

        self.drawing = drawing

    def draw(self):
        if self.drawing: Label.draw(self)
        Boxes.draw(self)

class Buttons(Labels, Button):

    def __init__(self, surface, name, x=0, y=0, width=None, height=None,
                 scale_width=1, scale_height=1, anchor="north west",
                 grid_amount_rows=1, grid_amount_columns=1, grid_nudge=None,
                 grid_drawing_style=None, grid_drawing_color=pg.Color("black"), grid_drawing_nudge=None,
                 members=None, mapping_position=None, mapping_bound=None, mapping_nudge=None,
                 filling_color=pg.Color("white"),
                 border_thickness=0, border_radius=0, border_color=pg.Color("black"),
                 text_string="", text_color=pg.Color("black"),
                 font_type="arial", font_size=24,
                 drawing=False,
                 response="toggle", status="unclicked",
                 filling_color_unclicked=None, filling_color_semiclicked=None, filling_color_clicked=None,
                 border_color_unclicked=None, border_color_semiclicked=None, border_color_clicked=None,
                 text_color_unclicked=None, text_color_semiclicked=None, text_color_clicked=None,
                 text_string_unclicked=None, text_string_semiclicked=None, text_string_clicked=None,
                 font_type_unclicked=None, font_type_semiclicked=None, font_type_clicked=None,
                 font_size_unclicked=None, font_size_semiclicked=None, font_size_clicked=None,
                 unclickable_inside=False, unclickable_outside=True,
                 member_clicked_index=None, tab_active=True, tab_reverse=False):

        Labels.__init__(self, surface, name, x, y, width, height,
                        scale_width, scale_height, anchor,
                        grid_amount_rows, grid_amount_columns, grid_nudge,
                        grid_drawing_style, grid_drawing_color, grid_drawing_nudge,
                        members, mapping_position, mapping_bound, mapping_nudge,
                        filling_color,
                        border_thickness, border_radius, border_color,
                        text_string, text_color,
                        font_type, font_size,
                        drawing)

        Button.__init__(self, surface, name, x, y, width, height,
                        scale_width, scale_height, anchor,
                        filling_color,
                        border_thickness, border_radius, border_color,
                        text_string, text_color,
                        font_type, font_size,
                        response, status,
                        filling_color_unclicked, filling_color_semiclicked, filling_color_clicked,
                        border_color_unclicked, border_color_semiclicked, border_color_clicked,
                        text_color_unclicked, text_color_semiclicked, text_color_clicked,
                        text_string_unclicked, text_string_semiclicked, text_string_clicked,
                        font_type_unclicked, font_type_semiclicked, font_type_clicked,
                        font_size_unclicked, font_size_semiclicked, font_size_clicked,
                        unclickable_inside, unclickable_outside)

        self._member_clicked_index = member_clicked_index
        self.tab = {"active": tab_active, "reverse": tab_reverse}

    @property
    def member_clicked_index(self):
        return self._member_clicked_index

    @member_clicked_index.setter
    def member_clicked_index(self, member_clicked_index):

        self._member_clicked_index = member_clicked_index

        for i, member in enumerate(self.members):
            if self.member_clicked_index == i:
                member.status = "clicked"
            else:
                if member.status == "clicked":
                    member.status = "unclicked"

    @property
    def member_clicked(self):
        return self.members[self.member_clicked_index]

    @property
    def tab_active(self):
        return self.tab["active"] and self.status == "clicked"

    @property
    def targeted(self):
        return True in [member.targeted for member in self.members]

    def update_member_clicked_index(self, event):

        for i, member in enumerate(self.members):
            if member.clicked(event):
                if self.member_clicked_index not in [None, i]:
                    self.member_clicked.status = "unclicked"
                self.member_clicked_index = i

        if "clicked" not in [member.status for member in self.members]:
            self.member_clicked_index = None

    def update_tab_reverse(self, event):

        if event.type == pg.KEYDOWN:
            if event.key in {pg.K_RSHIFT, pg.K_LSHIFT}:
                self.tab["reverse"] = True

        if event.type == pg.KEYUP:
            if event.key in {pg.K_RSHIFT, pg.K_LSHIFT}:
                self.tab["reverse"] = False

    def update_tab(self, event):

        if self.tab_active:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_TAB:
                    if self.member_clicked_index is not None:
                        if self.members[self.member_clicked_index].status == "clicked":

                            member_clicked_index_old = self.member_clicked_index
                            tab_reverse_to_int = -1 if self.tab["reverse"] else 1
                            member_clicked_index_new = (member_clicked_index_old + tab_reverse_to_int) % self.amount

                            self.members[member_clicked_index_old].status = "unclicked"
                            self.members[member_clicked_index_new].status = "clicked"

                            self.member_clicked_index = member_clicked_index_new

    def update(self, event):

        Labels.update(self, event)
        Button.update(self, event)

        self.update_member_clicked_index(event)
        self.update_tab_reverse(event)
        self.update_tab(event)

    def clicked(self, event):
        return True in [member.clicked(event) for member in self.members]

class TextBoxes(Buttons):

    def entered(self, event):
        return True in [member.entered(event) for member in self.members]

    def content(self):
        return {member.name: member.content for member in self.members}

# ---------------------------------------------------------------- #
