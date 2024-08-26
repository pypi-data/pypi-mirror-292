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
    QPointF,
)
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGraphicsRectItem,
    QGraphicsItem,
    QLineEdit,
    QMenu,
    QMessageBox,
)

from .constants import (
    TIMELINE_TITLE_HEIGHT,
    TIMELINE_TITLE_ON_BG_COLOR,
    TIMELINE_TITLE_OFF_BG_COLOR,
    TIMELINE_TITLE_ON_FG_COLOR,
    TIMELINE_TITLE_OFF_FG_COLOR,
)
from .event import (
    EventCollection,
    ChangeEvent,
    ChooseEvent,
)
from .textedit import TextEdit


class Timeline(QGraphicsRectItem):

    def __init__(self, name: str, time_pane):
        super().__init__()
        self.name = name
        self.time_pane = time_pane
        self.occurrences = []
        self.event_collection = EventCollection()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.title = TimelineTitle(self.name, self)
        self._select = False
        self.description = None

    @property
    def select(self):
        return self._select

    @select.setter
    def select(self, select):
        if select != self._select:
            self._select = select

    def add_occurrence(self, occurrence):
        """Add an occurrence to the timeline"""
        self.occurrences.append(occurrence)
        self.occurrences.sort(key=lambda x: x.begin_time)

    def remove_occurrence(self, occurrence):
        """Remove an occurrence from the timeline"""
        if occurrence in self.occurrences:
            self.occurrences.remove(occurrence)
            self.time_pane.scene.removeItem(occurrence)
            self.time_pane.data_needs_save = True

    def update_rect_width(self, new_width: float):
        """Update the width of the timeline"""
        rect = self.rect()
        rect.setWidth(new_width)
        self.setRect(rect)
        self.title.update_rect_width(new_width)

    def on_remove(self):
        if self.occurrences:
            answer = QMessageBox.question(
                self.time_pane,
                "Confirmation",
                "There are occurrences present. "
                "Do you want to remove this timeline?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                while self.occurrences:
                    self.occurrences[0].remove()
        # The following does not yet work, since there is no provision for
        # adjusting the positions of the timelines inside the time pane.
        # self.time_pane.scene.removeItem(self)
        # if self in self.time_pane.timelines:
        #     self.time_pane.timelines.remove(self)
        # del self

    def edit_properties(self):
        dialog = QDialog(self.time_pane)
        dialog.setWindowTitle("Timeline properties")

        layout = QFormLayout(self.time_pane)
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.title.text)
        self.name_edit.returnPressed.connect(dialog.accept)
        layout.addRow("Name: ", self.name_edit)
        layout.addRow("Description:", None)
        self.description_edit = TextEdit(self, self.description)
        layout.addRow(self.description_edit)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self.time_pane,
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        dialog.exec()
        if dialog.result() == dialog.DialogCode.Accepted:
            is_changed = False
            name = self.name_edit.text()
            if self.title.text != name:
                self.title.text = name
                is_changed = True
            description = self.description_edit.toPlainText()
            if self.description != description:
                self.description = description
                self.title.setToolTip(self.description)
                is_changed = True
            if is_changed:
                self.time_pane.data_needs_save = True

    def update_occurrences(self):
        for occurrence in self.occurrences:
            occurrence.update_style()

    def edit_events(self):
        while True:
            events_dialog = ChooseEvent(self.event_collection, self.time_pane)
            events_dialog.exec()
            if events_dialog.result() == QMessageBox.DialogCode.Accepted:
                e = events_dialog.get_chosen()
                name = e.name
                color = e.color
                description = e.description
                ChangeEvent(e, self.time_pane).exec()
                if (
                    name != e.name
                    or description != e.description
                    or color != e.color
                ):
                    self.update_occurrences()
                    self.time_pane.data_needs_save = True
            if events_dialog.result() == QMessageBox.DialogCode.Rejected:
                break
        if self.event_collection.is_changed():
            self.time_pane.data_needs_save = True

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            menu.addAction("Add new timeline").triggered.connect(
                self.time_pane.handle_timeline
            )
            menu.addAction(
                "Delete timeline (not yet fully implemented)"
            ).triggered.connect(self.on_remove)
            menu.addAction("Edit timeline properties").triggered.connect(
                self.edit_properties
            )
            menu.addAction("Edit events").triggered.connect(self.edit_events)
            menu.exec(event.screenPos())
        else:
            super().mousePressEvent(event)
        return


class TimelineTitle(QGraphicsRectItem):

    def __init__(self, text: str, parent: Timeline = None):
        super().__init__(parent)
        self.text = text
        rect = self.parentItem().rect()
        rect.setHeight(TIMELINE_TITLE_HEIGHT)
        self.setRect(rect)
        self.parent = parent

    def paint(self, painter, option, widget=...):
        # Draw the rectangle
        self.draw_rect(painter)

        # Draw the text
        self.draw_text(painter)

    def draw_rect(self, painter):
        """Draw the timeline title rectangle"""
        # Set Pen and Brush for rectangle
        if self.parent.select:
            color = TIMELINE_TITLE_ON_BG_COLOR
        else:
            color = TIMELINE_TITLE_OFF_BG_COLOR
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawRect(self.rect())

    def draw_text(self, painter):
        """Draw the timeline title text"""
        if self.parent.select:
            color = TIMELINE_TITLE_ON_FG_COLOR
        else:
            color = TIMELINE_TITLE_OFF_FG_COLOR
        painter.setPen(color)
        painter.setBrush(color)

        font = painter.font()
        fm = QFontMetrics(font)

        text_width = fm.boundingRect(self.text).width()
        text_height = fm.boundingRect(self.text).height()
        text_descent = fm.descent()

        # Get timeline polygon based on the viewport
        timeline_in_viewport_pos = self.parentItem().time_pane.view.mapToScene(
            self.rect().toRect()
        )

        bounding_rect = timeline_in_viewport_pos.boundingRect()

        # Get the viewport rect
        viewport_rect = self.parentItem().time_pane.view.viewport().rect()

        # Compute the x position for the text
        x_alignCenter = bounding_rect.x() + viewport_rect.width() / 2

        # No idea why the "-2", in the vertical position, is needed here
        text_position = QPointF(
            x_alignCenter - text_width / 2,
            TIMELINE_TITLE_HEIGHT / 2 + text_height / 2 - text_descent - 2
        )

        painter.drawText(text_position, self.text)

    def update_rect_width(self, new_width):
        rect = self.rect()
        rect.setWidth(new_width)
        self.setRect(rect)
