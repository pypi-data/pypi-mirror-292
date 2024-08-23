# ViCodePy - A video coder for Experimental Psychology
#
# Copyright (C) 2024 Esteban Milleret
# Copyright (C) 2024 Rafael Laboissière
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.


from PySide6.QtCore import (
    Qt,
    QRectF,
    QLine,
    QPointF,
    QSizeF,
)
from PySide6.QtGui import (
    QColor,
    QPolygonF,
)
from PySide6.QtWidgets import QGraphicsItem


class Cursor(QGraphicsItem):

    PEN_COLOR = Qt.GlobalColor.black
    BRUSH_COLOR = QColor(0, 0, 0, 100)
    HANDLE_HEIGHT = 25
    HANDLE_WIDTH = 10

    def __init__(self, parent):
        super().__init__(parent)
        if parent.time_pane:
            self.time_pane = parent.time_pane
        self.pressed = False
        self.poly: QPolygonF = QPolygonF(
            [
                QPointF(-self.HANDLE_WIDTH, 0),
                QPointF(self.HANDLE_WIDTH, 0),
                QPointF(0, self.HANDLE_HEIGHT),
            ]
        )
        self.line: QLine = QLine(0, self.HANDLE_HEIGHT, 0, 10000)

        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(101)

    def paint(self, painter, option, widget=...):
        painter.setPen(self.PEN_COLOR)
        painter.setBrush(self.BRUSH_COLOR)
        painter.drawLine(self.line)
        painter.drawPolygon(self.poly)

    def calculate_size(self):
        min_x: float = self.poly[0].x()
        max_x: float = self.poly[0].x()

        for i, point in enumerate(self.poly):
            if point.x() < min_x:
                min_x = point.x()
            if point.x() > max_x:
                max_x = point.x()

        return QSizeF(max_x - min_x, self.HANDLE_HEIGHT)

    def boundingRect(self):
        size: QSizeF = self.calculate_size()
        return QRectF(-10, 0, size.width(), size.height())

    def focusInEvent(self, event):
        self.pressed = True
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event):
        self.pressed = False
        super().focusOutEvent(event)
        self.update()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        pos: QPointF = event.scenePos()
        if self.pressed:
            time = int(
                pos.x()
                * self.time_pane.duration
                / self.parentItem().rect().width()
            )

            # During creation of a new occurrence
            if self.time_pane and self.time_pane.occurrence_in_creation:
                occurrence = self.time_pane.occurrence_in_creation
                if time != occurrence.get_time_from_bounding_interval(time):
                    # Stop player at the lower or upper bound when they
                    # are passed over
                    self.setPos(self.x(), 0)
                    return

            self.time_pane.video.set_position(time)

            if pos.x() < 0:
                self.setPos(0, 0)
            elif pos.x() > self.parentItem().rect().width():
                self.setPos(self.parentItem().rect().width(), 0)
            else:
                self.setPos(pos.x(), 0)

        self.update()
