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

import platform
from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QAction,
    QKeySequence,
)
from PySide6.QtWidgets import QStyle

from .about import About, open_repository_url, open_pypi_url


class Menu:

    def __init__(self, window):

        self.window = window
        self.menu_bar = window.menuBar()
        self.style = self.window.style()

        self.create_file_menu()
        self.create_play_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_help_menu()

    def create_file_menu(self):
        menu = self.menu_bar.addMenu("&File")

        # Add actions to file menu
        open_action = QAction(
            self.style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon),
            "&Open video",
            self.window,
            shortcut=QKeySequence.StandardKey.Open,
            triggered=self.window.files.open_video,
        )

        open_project_action = QAction(
            self.style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon),
            "Open &project",
            self.window,
            shortcut=QKeySequence(
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_O
            ),
            triggered=self.window.files.open_project,
        )

        icon = self.style.standardIcon(
            QStyle.StandardPixmap.SP_DialogSaveButton
        )
        self.save_project_action = QAction(
            icon,
            "Save project",
            self.window,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S),
            triggered=self.window.files.save_project,
            enabled=False,
        )

        export_action = QAction(
            icon,
            "Export Data",
            self.window,
            shortcut=QKeySequence(
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_S
            ),
            triggered=self.window.files.export_data_file,
        )

        close_action = QAction(
            "Quit",
            self.window,
            shortcut=(
                QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Q)
                if platform.system() == "Windows"
                else QKeySequence.StandardKey.Quit
            ),
            triggered=self.window.close,
        )

        menu.addAction(open_action)
        menu.addAction(open_project_action)
        menu.addAction(self.save_project_action)
        menu.addAction(export_action)
        menu.addAction(close_action)

    def create_play_menu(self):
        # Add actions to play menu
        menu = self.menu_bar.addMenu("&Play")
        icon = self.style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.play_action = QAction(
            icon,
            "Play/Pause",
            self.window,
            shortcut=Qt.Key.Key_Space,
            triggered=self.window.video.play_pause,
            enabled=False,
        )

        icon = self.style.standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        self.stop_action = QAction(
            icon,
            "Stop",
            self.window,
            shortcut=Qt.Key.Key_S,
            triggered=self.window.video.stop,
            enabled=False,
        )

        icon = self.style.standardIcon(
            QStyle.StandardPixmap.SP_MediaSkipBackward
        )
        self.previous_frame_action = QAction(
            icon,
            "Go to the previous frame",
            self.window,
            shortcut=Qt.Key.Key_Left,
            triggered=partial(self.window.video.move_to_frame, -1),
            enabled=False,
        )
        self.fifth_previous_frame_action = QAction(
            icon,
            "Go to the fifth previous frame",
            self.window,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Left),
            triggered=partial(self.window.video.move_to_frame, -5),
            enabled=False,
        )
        self.tenth_previous_frame_action = QAction(
            icon,
            "Go to the tenth previous frame",
            self.window,
            shortcut=QKeySequence(
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Left
            ),
            triggered=partial(self.window.video.move_to_frame, -10),
            enabled=False,
        )

        icon = self.style.standardIcon(
            QStyle.StandardPixmap.SP_MediaSkipForward
        )
        self.next_frame_action = QAction(
            icon,
            "Go to the next frame",
            self.window,
            shortcut=Qt.Key.Key_Right,
            triggered=partial(self.window.video.move_to_frame, 1),
            enabled=False,
        )
        self.fifth_next_frame_action = QAction(
            icon,
            "Go to the fifth next frame",
            self.window,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Right),
            triggered=partial(self.window.video.move_to_frame, 5),
            enabled=False,
        )
        self.tenth_next_frame_action = QAction(
            icon,
            "Go to the tenth next frame",
            self.window,
            shortcut=QKeySequence(
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Right
            ),
            triggered=partial(self.window.video.move_to_frame, 10),
            enabled=False,
        )

        for action in [
            self.play_action,
            self.stop_action,
            self.previous_frame_action,
            self.fifth_previous_frame_action,
            self.tenth_previous_frame_action,
            self.next_frame_action,
            self.fifth_next_frame_action,
            self.tenth_next_frame_action,
        ]:
            menu.addAction(action)

    def create_edit_menu(self):
        menu = self.menu_bar.addMenu("&Edit")

        # Edit Timeline submenu
        edit_timeline_menu = menu.addMenu("&Timeline")

        self.add_timeline_action = QAction(
            "Add Timeline",
            self.window,
            triggered=self.window.time_pane.handle_timeline,
            enabled=False,
        )
        self.add_timeline_action.setShortcuts(
            [
                QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Return),
                QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Enter),
            ]
        )
        edit_timeline_menu.addAction(self.add_timeline_action)

        select_next_timeline_action = QAction(
            "Select Next TimeLine",
            self.window,
            triggered=partial(self.window.time_pane.select_cycle_timeline, 1),
            enabled=True,
        )
        select_next_timeline_action.setShortcuts([Qt.Key.Key_Down])
        edit_timeline_menu.addAction(select_next_timeline_action)

        select_previous_timeline_action = QAction(
            "Select Previous TimeLine",
            self.window,
            triggered=partial(self.window.time_pane.select_cycle_timeline, -1),
            enabled=True,
        )
        select_previous_timeline_action.setShortcuts([Qt.Key.Key_Up])
        edit_timeline_menu.addAction(select_previous_timeline_action)

        # Edit Occurrence submenu
        edit_occurrence_menu = menu.addMenu("&Occurrence")

        self.add_occurrence_action = QAction(
            "Start Occurrence",
            self.window,
            triggered=self.window.time_pane.handle_occurrence,
            enabled=False,
        )
        self.add_occurrence_action.setShortcuts(
            [Qt.Key.Key_Return, Qt.Key.Key_Enter]
        )
        edit_occurrence_menu.addAction(self.add_occurrence_action)

        self.abort_occurrence_creation_action = QAction(
            "Abort Current Occurrence",
            self.window,
            triggered=self.window.time_pane.abort_occurrence_creation,
            enabled=False,
        )
        self.abort_occurrence_creation_action.setShortcuts([Qt.Key.Key_Escape])
        edit_occurrence_menu.addAction(self.abort_occurrence_creation_action)

        delete_occurrence_action = QAction(
            "Delete Occurrence",
            self.window,
            triggered=self.window.time_pane.delete_occurrence,
            enabled=True,
        )
        delete_occurrence_action.setShortcuts(
            [Qt.Key.Key_Backspace, Qt.Key.Key_Delete]
        )
        edit_occurrence_menu.addAction(delete_occurrence_action)

    def create_view_menu(self):
        # Add actions to view menu
        menu = self.menu_bar.addMenu("&View")
        self.fullscreen_action = QAction(
            self.style.standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton),
            "Toggle Fullscreen",
            self.window,
            shortcut=Qt.Key.Key_F11,
            triggered=self.window.on_fullscreen,
        )

        menu.addAction(self.fullscreen_action)

    def create_help_menu(self):
        # Help menu
        menu = self.menu_bar.addMenu("&Help")

        self.about_action = QAction(
            "About ViCodePy",
            self.window,
            triggered=self.about,
        )
        menu.addAction(self.about_action)

        self.visit_pypi_action = QAction(
            "Visit PyPI project",
            self.window,
            triggered=open_pypi_url,
        )
        menu.addAction(self.visit_pypi_action)

        self.visit_repository_action = QAction(
            "Visit Git repository",
            self.window,
            triggered=open_repository_url,
        )
        menu.addAction(self.visit_repository_action)

    def about(self):
        About().exec()
