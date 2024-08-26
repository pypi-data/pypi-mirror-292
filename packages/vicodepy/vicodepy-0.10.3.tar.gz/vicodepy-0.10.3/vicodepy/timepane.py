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

import pandas as pd
from math import inf

from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QAbstractSlider,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QMessageBox,
    QScrollBar,
    QVBoxLayout,
    QStyle,
    QWidget,
)
from PySide6.QtGui import QFontMetrics

from .constants import (
    CSV_HEADERS,
    EVENT_DEFAULT_COLOR,
    MINIMUM_ZOOM_FACTOR,
    OCCURRENCE_PEN_WIDTH_OFF_CURSOR,
    OCCURRENCE_PEN_WIDTH_ON_CURSOR,
    TIMELINE_HEIGHT,
    TIME_SCALE_HEIGHT,
    ZOOM_STEP,
)
from .cursor import Cursor
from .dialog import (
    ConfirmMessageBox,
    DialogCode,
    TimelineDialog,
)
from .event import (
    ChooseEvent,
    Event,
    EventCollection,
)
from .occurrence import (
    Occurrence,
    OccurrenceHandle,
)
from .ticklocator import TickLocator
from .timeline import Timeline


class ZoomableGraphicsView(QGraphicsView):

    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.zoom_factor = 1.0
        self.zoom_step = ZOOM_STEP
        self.zoom_shift = None
        self.minimum_zoom_factor = MINIMUM_ZOOM_FACTOR

        self.create_ui()

    def create_ui(self):
        vertical_scrollbar = QScrollBar(Qt.Orientation.Vertical, self)
        vertical_scrollbar.valueChanged.connect(
            self.on_vertical_scroll_value_changed
        )
        self.setVerticalScrollBar(vertical_scrollbar)

        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if not self.parent().video.media:
                return
            mouse_pos = self.mapToScene(event.position().toPoint()).x()
            if event.angleDelta().y() > 0:
                self.zoom_shift = mouse_pos * (1 - self.zoom_step)
                self.zoom_in()
            else:
                self.zoom_shift = mouse_pos * (1 - 1 / self.zoom_step)
                self.zoom_out()
            self.zoom_shift = None
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            if event.angleDelta().y() > 0:
                action = QAbstractSlider.SliderSingleStepAdd
            else:
                action = QAbstractSlider.SliderSingleStepSub
            self.horizontalScrollBar().triggerAction(action)
        else:
            super().wheelEvent(event)

    def on_vertical_scroll_value_changed(self, value):
        if self.parent().time_pane_scale:
            self.parent().time_pane_scale.setPos(0, value)

    def zoom_in(self):
        self.zoom_factor *= self.zoom_step
        self.update_scale()

    def zoom_out(self):
        if self.zoom_factor / self.zoom_step >= self.minimum_zoom_factor:
            self.zoom_factor /= self.zoom_step
            self.update_scale()

    def update_scale(self):
        # Update the size of the scene with zoom_factor
        self.scene().setSceneRect(
            0,
            0,
            self.width() * self.zoom_factor,
            self.scene().height(),
        )

        if self.zoom_shift:
            previous_anchor = self.transformationAnchor()
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.translate(self.zoom_shift, 0)
            self.setTransformationAnchor(previous_anchor)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)

        # Get the position click from the scene
        map = self.mapToScene(self.scene().sceneRect().toRect())
        x = map.boundingRect().x()

        # Compute the time of the position click
        time = int(
            (x + event.scenePosition().x())
            * self.parent().duration
            / self.scene().width()
        )

        self.parent().video.set_position(time)

    def set_position(self, time):
        # During the creation of a new occurrence
        if self.parent().occurrence_in_creation:
            occurence = self.parent().occurrence_in_creation
            time = occurence.get_time_from_bounding_interval(time)

        # Cope with selected occurrence
        for i in self.parent().scene.selectedItems():
            if isinstance(i, Occurrence):
                time = i.get_time_from_bounding_interval(time)
                break

        # Set time of the video player
        self.parent().window.video.media_player.setPosition(int(time))

    def keyPressEvent(self, event):
        pass


class TimePane(QWidget):

    def __init__(self, window):
        """Initializes the timeline widget"""
        super().__init__(window)
        self._duration = 0
        self._time = 0

        self.selected_timeline = None
        self.occurrence_in_creation: Occurrence = None
        self.window = window
        self.video = window.video
        self.timelines: list[Timeline] = []
        self.cursor = None
        self.time_pane_scale = None
        self.data_needs_save = False
        self.scrollbar_width = self.window.style().pixelMetric(
            QStyle.PM_ScrollBarExtent
        )

        self.setMouseTracking(True)

        self.create_ui()

    def create_ui(self):
        self.scene = QGraphicsScene()
        self.scene.sceneRectChanged.connect(self.on_scene_changed)
        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.view = ZoomableGraphicsView(self.scene, self)
        self.scene.setSceneRect(0, 0, self.view.width(), self.view.height())

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def on_scene_changed(self, rect):
        # Update occurrences
        for timeline in self.timelines:
            timeline.update_rect_width(rect.width())
            for occurrence in timeline.occurrences:
                occurrence.update_rect()

        if self.occurrence_in_creation:
            self.occurrence_in_creation.update_rect()

        # Update time_pane_scale display
        if self.time_pane_scale:
            # Update cursor
            if self.duration:
                self.time_pane_scale.cursor.setX(
                    self.time * rect.width() / self.duration
                )
            self.time_pane_scale.update_rect()

    def on_selection_changed(self):
        selected_items = self.scene.selectedItems()
        selected = None
        if len(selected_items) == 1:
            selected = selected_items[0]
            if isinstance(selected, Timeline):
                self.selected_timeline = selected
        for s in self.timelines:
            s.select = s == selected

    def select_cycle_timeline(self, delta, checked=False):
        i, n = self.find_selected_timeline()
        self.timelines[i].select = False
        if delta > 0:
            if i == n - 1:
                i = -1
        else:
            if i == 0:
                i = n
        i += delta
        self.select_timeline(self.timelines[i])

    def find_selected_timeline(self):
        n = len(self.timelines)
        for i in range(n):
            if self.timelines[i].select:
                break
        return i, n

    def select_timeline(self, line):
        for tl in self.timelines:
            tl.select = False
        line.select = True
        self.selected_timeline = line
        line.update()

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        if time != self._time:
            self._time = time
            self.on_time_changed(time)

    def on_time_changed(self, new_time):
        # First, update the current occurrence, if it exists. If the cursor
        # time goes beyond the allowed bounds, bring it back and do not update
        # the other widgets.
        if self.occurrence_in_creation:
            if (
                self.occurrence_in_creation.lower_bound
                and new_time < self.occurrence_in_creation.lower_bound
            ):
                new_time = self.occurrence_in_creation.lower_bound
            elif (
                self.occurrence_in_creation.upper_bound
                and new_time > self.occurrence_in_creation.upper_bound
            ):
                new_time = self.occurrence_in_creation.upper_bound
                if (
                    self.video.media_player.playbackState()
                    == QMediaPlayer.PlaybackState.PlayingState
                ):
                    self.video.media_player.pause()
            begin_time = self.occurrence_in_creation.begin_time
            end_time = self.occurrence_in_creation.end_time
            mfps = self.video.mfps
            if begin_time < end_time:
                if new_time >= begin_time:
                    self.occurrence_in_creation.update_end_time(
                        new_time + int(mfps / 2)
                    )
                else:
                    self.occurrence_in_creation.update_begin_time(end_time)
                    self.occurrence_in_creation.update_end_time(
                        begin_time - mfps
                    )
            else:
                if new_time <= begin_time:
                    self.occurrence_in_creation.update_end_time(
                        new_time - int(mfps / 2)
                    )
                else:
                    self.occurrence_in_creation.update_begin_time(end_time)
                    self.occurrence_in_creation.update_end_time(
                        begin_time + mfps
                    )

        # Cope with selected occurrence
        for i in self.scene.selectedItems():
            if isinstance(i, Occurrence):
                new_time = i.get_time_from_bounding_interval(new_time)
                break

        # Update cursor position
        if self.time_pane_scale and self.time_pane_scale.cursor:
            self.time_pane_scale.cursor.setX(
                new_time * self.scene.width() / self.duration
            )

        if isinstance(self.scene.focusItem(), OccurrenceHandle):
            occurrence_handle: OccurrenceHandle = self.scene.focusItem()
            occurrence_handle.change_time(new_time)

        # Change appearance of occurrence under the cursor
        # (Brute force approach; this ought to be improved)
        if not self.occurrence_in_creation:
            for t in self.timelines:
                for a in t.occurrences:
                    a.penWidth = OCCURRENCE_PEN_WIDTH_OFF_CURSOR
            if self.selected_timeline:
                for a in self.selected_timeline.occurrences:
                    if a.begin_time <= new_time and a.end_time >= new_time:
                        a.penWidth = OCCURRENCE_PEN_WIDTH_ON_CURSOR
                        break

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        if duration != self._duration:
            self._duration = duration
            self.load_common()
            self.update()

    def load_common(self):
        # Recreate timeline
        self.time_pane_scale = TimePaneScale(self)

    def clear(self):
        # Clear timelineScene
        self.scene.clear()
        self.timelines = []

    # FIXME: [CREATION] move into occurrence.py
    def handle_occurrence(self):
        """Handle the occurrence"""
        if self.occurrence_in_creation is None:
            # FIXME: This bugs when there is no occurrences in timeline!!!
            can_be_initiate, lower_bound, upper_bound, occurrence = (
                Occurrence.can_be_initiated(
                    self.selected_timeline.occurrences, self.time
                )
            )
            if can_be_initiate:
                mfps = self.video.mfps
                self.occurrence_in_creation = Occurrence(
                    self.selected_timeline,
                    self.time - int(mfps / 2),
                    self.time + int(mfps / 2),
                    lower_bound,
                    upper_bound,
                )
            self.window.menu.add_occurrence_action.setText("Finish occurrence")
            self.window.menu.abort_occurrence_creation_action.setEnabled(True)
            if occurrence:
                occurrence.setSelected(not occurrence.isSelected())
                occurrence.get_bounds()

        else:
            # Finish the current occurrence
            events_dialog = ChooseEvent(
                self.selected_timeline.event_collection, self
            )
            events_dialog.exec()
            if events_dialog.result() == QMessageBox.DialogCode.Accepted:
                event = events_dialog.get_chosen()
                self.occurrence_in_creation.set_event(event)
                self.update()
                self.occurrence_in_creation.end_creation()
                self.occurrence_in_creation = None
                self.on_time_changed(self.time)
            menu = self.window.menu
            menu.add_occurrence_action.setText("Start occurrence")
            menu.abort_occurrence_creation_action.setEnabled(False)
            self.data_needs_save = True
            self.update()

    def handle_timeline(self):
        dialog = TimelineDialog(self)
        dialog.exec()
        if dialog.result() == DialogCode.Accepted:
            name = dialog.get_text()
            if name == "":
                QMessageBox.warning(
                    self, "Warning", "Timeline name cannot be empty"
                )
                return
            self.add_timeline(Timeline(name, self))
            self.data_needs_save = True

    def resizeEvent(self, a0):
        if self.time_pane_scale:
            origin = self.view.mapToScene(0, 0).x()
            width_before = self.scene.width() / self.view.zoom_factor
            width_after = self.view.width()
            shift = origin * (1 - width_after / width_before)
            self.view.update_scale()
            previous_anchor = self.view.transformationAnchor()
            self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.view.translate(shift, 0)
            self.view.setTransformationAnchor(previous_anchor)
        else:
            self.scene.setSceneRect(
                0,
                0,
                self.view.width(),
                TIME_SCALE_HEIGHT + TIMELINE_HEIGHT,
            )

        self.update()

    def abort_occurrence_creation(self):
        if self.occurrence_in_creation is not None:
            confirm_box = ConfirmMessageBox("Abort creation of occurrence?")
            if confirm_box.result() == ConfirmMessageBox.DialogCode.Accepted:
                self.occurrence_in_creation.remove()
                self.occurrence_in_creation = None
                self.update()
                menu = self.window.menu
                menu.abort_occurrence_creation_action.setEnabled(False)

    def add_timeline(self, timeline):
        self.timelines.append(timeline)
        self.add_to_scene(timeline)

        # Compute the new height of the scene
        new_height = TIME_SCALE_HEIGHT + len(self.timelines) * TIMELINE_HEIGHT
        scene_rect = self.scene.sceneRect()
        scene_rect.setHeight(new_height)
        self.scene.setSceneRect(scene_rect)

        # Set maximum height of the widget
        self.setMaximumHeight(int(new_height) + self.scrollbar_width + 2)

        # Select the new timeline
        for i in self.timelines:
            i.select = False
        timeline.select = True

    def add_to_scene(self, timeline):
        """Add the timeline to the scene"""
        # Set Y of the timeline based on the timescale height and the timeline
        # lines heights present on the scene
        timeline.setPos(
            0,
            TIME_SCALE_HEIGHT + (len(self.timelines) - 1) * TIMELINE_HEIGHT,
        )

        # Set the right rect based on the scene width and the height constant
        timeline.setRect(
            0,
            0,
            self.scene.width(),
            TIMELINE_HEIGHT,
        )

        # Add line to the scene
        self.scene.addItem(timeline)

    def add_timelines(self, data):
        for _, row in data.data.iterrows():
            # Search for timeline
            timeline = self.get_timeline_by_name(row["timeline"])

            # If timeline from csv doesn't exist in TimePane,
            # escape row
            if not timeline:
                continue

            # Search for event
            event = timeline.event_collection.get_event(row["event"])

            # If event from csv doesn't exist in timeline,
            # then add it
            if not event:
                continue

            occurrence = Occurrence(
                timeline,
                int(row["begin"]),
                int(row["end"]),
            )

            occurrence.set_event(event)
            occurrence.end_creation()

    def get_timeline_by_name(self, name):
        """Get the timeline by name"""
        return next((x for x in self.timelines if x.name == name), None)

    def has_occurrences(self) -> bool:
        return any(len(line.occurrences) for line in self.timelines)

    def delete_occurrence(self):
        for i in self.scene.selectedItems():
            if isinstance(i, Occurrence):
                i.on_remove()
                break

    def timelines_from_config(self, config):
        if "timelines" in config:

            # Set all absent order fields with Inf
            for k, v in config["timelines"].items():
                if not v:
                    v = dict()
                    config["timelines"][k] = v
                if "order" not in v:
                    v["order"] = -inf
                if "description" not in v:
                    v["description"] = ""

            # Sort according to order first and alphabetically from
            # timeline name, otherwise
            for item in sorted(
                config["timelines"].items(),
                key=lambda x: (x[1]["order"], x[0]),
            ):
                # Get name and properties of the timeline
                name = item[0]
                properties = item[1]

                # Create timeline
                line = Timeline(name, self)

                # Check description
                description = properties["description"]
                if description == "":
                    description = "(no description)"
                line.title.setToolTip(description)
                line.description = description

                # Add the timeline to the TimePane
                self.add_timeline(line)

                # Loop over events of the timeline
                event_collection = EventCollection()
                if "events" in properties:
                    for k, v in properties["events"].items():
                        event = Event(k)
                        try:
                            event.color = QColor(v["color"])
                        except KeyError:
                            event.color = EVENT_DEFAULT_COLOR
                        try:
                            event.description = v["description"]
                        except KeyError:
                            event.description = ""
                        event_collection.add_event(event)
                    line.event_collection = event_collection

    def timelines_to_dataframe(self):
        df = pd.DataFrame(columns=CSV_HEADERS)
        for timeline in sorted(
            self.window.time_pane.timelines, key=lambda x: x.name
        ):
            for occurrence in timeline.occurrences:
                comment = occurrence.comment.replace('"', '\\"')
                row = [
                    timeline.name,
                    occurrence.event.name,
                    occurrence.begin_time,
                    occurrence.end_time,
                    comment,
                ]
                df.loc[len(df.index)] = row
        return df


class TimePaneScale(QGraphicsRectItem):

    def __init__(self, time_pane: TimePane):
        super().__init__()
        self.time_pane = time_pane
        self.time_pane.scene.addItem(self)
        self.cursor = Cursor(self)
        self.setRect(
            QRectF(0, 0, self.time_pane.scene.width(), TIME_SCALE_HEIGHT)
        )

    def paint(self, painter, option, widget=...):
        self.draw_rect(painter)

        if self.time_pane.duration != 0:
            self.draw_scale(painter)

    def update_rect(self):
        self.setRect(
            QRectF(0, 0, self.time_pane.scene.width(), TIME_SCALE_HEIGHT)
        )
        self.update()

    def draw_rect(self, painter):
        """Draw the background rectangle of the timeline scale"""
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.lightGray)
        self.setRect(
            QRectF(0, 0, self.time_pane.scene.width(), TIME_SCALE_HEIGHT)
        )
        painter.drawRect(self.rect())

    def draw_scale(self, painter):
        tl = TickLocator()
        dur = self.time_pane.duration
        wid = self.time_pane.scene.width()
        font = painter.font()
        fm = QFontMetrics(font)
        loc = tl.find_locations(0, dur / 1000, wid, fm)
        # Compute the height of the text
        font_height = fm.height()
        line_height = 5
        y = self.rect().height()

        for p in loc:

            i = 1000 * (p[0] * wid / dur)

            # Compute the position of the text
            text_width = fm.boundingRect(p[1]).width()
            text_position = QPointF(i - text_width / 2, font_height)

            # Draw the text
            painter.drawText(text_position, p[1])

            # Compute the position of the line
            painter.drawLine(QPointF(i, y), QPointF(i, y - line_height))

    def mousePressEvent(self, event):
        return

    def mouseReleaseEvent(self, event):
        return
