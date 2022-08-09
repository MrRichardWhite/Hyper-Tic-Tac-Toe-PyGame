# ---------------------------------------------------------------- #

import pygame as pg
import numpy as np

from widgets.single import *

# ---------------------------------------------------------------- #

def draw(widgets):
    for widget in widgets:
        if "draw" in dir(widget):
            widget.draw()

def update(widgets, event):
    for widget in widgets:
        if "update" in dir(widget):
            widget.update(event)

# ---------------------------------------------------------------- #

def draw_line_dashed(surface, color, position_start, position_end, width=1, dash_length=10, exclude_corners=True):

    # convert tuples to numpy arrays
    position_start = np.array(position_start)
    position_end   = np.array(position_end)

    # get euclidian distance between position_start and position_end
    length = np.linalg.norm(position_end - position_start)

    # get amount of pieces that line will be split up in (half of it are amount of dashes)
    dash_amount = int(length / dash_length)

    # x-y-value-pairs of where dashes start (and on next, will end)
    dash_knots = np.array([np.linspace(position_start[i], position_end[i], dash_amount) for i in range(2)]).transpose()

    return [pg.draw.line(surface, color, tuple(dash_knots[n]), tuple(dash_knots[n+1]), width)
            for n in range(int(exclude_corners), dash_amount - int(exclude_corners), 2)]

# ---------------------------------------------------------------- #

class Grid(Box):

    def __init__(self, surface, name=None, x=0, y=0, width=None, height=None,
                 scale_width=1, scale_height=1, anchor="north west",
                 amount_rows=1, amount_columns=1,
                 drawing_style=None, drawing_color=pg.Color("black"), drawing_nudge=None):

        if width is None:  width  = surface.get_width()
        if height is None: height = surface.get_height()

        super().__init__(surface, name, x, y, width, height,
                         scale_width, scale_height, anchor)

        self.amount = {"rows" : amount_rows, "columns": amount_columns}
        self.drawing = {"style": drawing_style, "color": drawing_color, "nudge": drawing_nudge}

    @property
    def shape(self):
        return self.amount["rows"], self.amount["columns"]

    @shape.setter
    def shape(self, shape):
        self.amount["rows"], self.amount["columns"] = shape

    @property
    def size(self):
        return self.amount["rows"] * self.amount["columns"]

    @property
    def inner(self):

        name = self.name + " " + "inner"

        if self.amount["rows"] > 1 and self.amount["columns"] > 1:
            x, y = (self[0, 0]   + self[1, 1])   // 2
            a, b = (self[-1, -1] + self[-2, -2]) // 2
            amount_rows = self.amount["rows"]-1
            amount_columns = self.amount["columns"]-1
        if self.amount["rows"] > 1 and self.amount["columns"] == 1:
            x, y = (self[0][0]  + self[1][0])  // 2
            a, b = (self[-1][0] + self[-2][0]) // 2
            amount_rows = self.amount["rows"]-1
            amount_columns = self.amount["columns"]
        if self.amount["rows"] == 1 and self.amount["columns"] > 1:
            x, y = (self[0][0]  + self[0][1])  // 2
            a, b = (self[0][-1] + self[0][-2]) // 2
            amount_rows = self.amount["rows"]
            amount_columns = self.amount["columns"]-1

        grid_inner = Grid(self.surface, name, x, y, self.width, self.height,
                          self.scale["width"], self.scale["height"], "north west",
                          amount_rows=amount_rows, amount_columns=amount_columns,
                          drawing_style=self.drawing["style"], drawing_color=self.drawing["color"], drawing_nudge=self.drawing["nudge"])

        grid_inner.bound = (a, b)

        return grid_inner

    @property
    def outer(self):

        assert self.amount["rows"] > 1
        assert self.amount["columns"] > 1

        name = self.name + " " + "outer"

        x, y = self[0][0]   - (self[1][1]   - self[0][0])   // 2
        a, b = self[-1][-1] + (self[-1][-1] - self[-2][-2]) // 2

        grid_outer = Grid(self.surface, name, x, y, self.width, self.height,
                          self.scale["width"], self.scale["height"], self.anchor,
                          amount_rows=self.amount["rows"]+1, amount_columns=self.amount["columns"]+1,
                          drawing_style=self.drawing["style"], drawing_color=self.drawing["color"], drawing_nudge=self.drawing["nudge"])

        grid_outer.bound_actually = (a, b)

        return grid_outer

    @property
    def points(self):

        coordinates = [np.linspace(self.x_actually, self.a_actually, self.amount["columns"]),
                       np.linspace(self.y_actually, self.b_actually, self.amount["rows"])]

        return np.array([[(int(x), int(y)) for x in coordinates[0]] for y in coordinates[1]])

    def __getitem__(self, i, j=None):

        if j is None:
            if type(i) in [list, tuple, np.ndarray]:
                j, i = i
            else:
                return self.points[i]

        return self.points[i][j]

    def draw(self):

        if self.drawing["nudge"] is None:

            if self.drawing["style"] is None:
                pass

            elif self.drawing["style"] == "dots":
                for i in range(self.amount["rows"]):
                    for j in range(self.amount["columns"]):
                        pg.draw.circle(self.surface, self.drawing["color"], self[i][j], 4)

            elif self.drawing["style"] == "lines":

                for i in range(self.amount["rows"]):
                    pg.draw.line(self.surface, self.drawing["color"], self[i][0], self[i][-1], 4)

                for j in range(self.amount["columns"]):
                    pg.draw.line(self.surface, self.drawing["color"], self[0][j], self[-1][j], 4)

            elif self.drawing["style"] == "lines inner":

                for i in range(1, self.amount["rows"]-1):
                    pg.draw.line(self.surface, self.drawing["color"], self[i][0], self[i][-1], 4)

                for j in range(1, self.amount["columns"]-1):
                    pg.draw.line(self.surface, self.drawing["color"], self[0][j], self[-1][j], 4)

            elif self.drawing["style"] == "lines dashed":
        
                for i in range(self.amount["rows"]):
                    draw_line_dashed(self.surface, self.drawing["color"], self[i][0], self[i][-1], 4)

                for j in range(self.amount["columns"]):
                    draw_line_dashed(self.surface, self.drawing["color"], self[0][j], self[-1][j], 4)

            elif self.drawing["style"] == "lines inner dashed":

                for i in range(1, self.amount["rows"]-1):
                    draw_line_dashed(self.surface, self.drawing["color"], self[i][0], self[i][-1], 4)

                for j in range(1, self.amount["columns"]-1):
                    draw_line_dashed(self.surface, self.drawing["color"], self[0][j], self[-1][j], 4)

        elif self.drawing["nudge"] == "inner":
            drawing = self.inner
            drawing.drawing["nudge"] = None
            drawing.draw()
        
        elif self.drawing["nudge"] == "outer":
            drawing = self.outer
            drawing.drawing["nudge"] = None
            drawing.draw()

# ---------------------------------------------------------------- #
