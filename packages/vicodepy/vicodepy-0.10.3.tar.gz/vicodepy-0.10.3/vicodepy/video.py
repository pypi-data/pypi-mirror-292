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

from math import floor
from pathlib import Path
from functools import partial

from PySide6.QtCore import (
    Qt,
    QSize,
    QTimer,
)
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import (
    QAudioOutput,
    QMediaMetaData,
    QMediaPlayer,
)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from .assets import Assets
from .utils import (
    milliseconds_to_formatted_string,
)

with open(Path(__file__).parent.joinpath("images.py")) as f:
    exec(f.read())


class Video(QWidget):
    """A simple Media Player using Qt"""

    def __init__(self, window):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.media = None
        self.mfps = None
        self.window = window

        self.create_ui()

        self.setup_timer()

    def create_ui(self):
        """Set up the user interface, signals & slots"""
        # Create the video widget
        video_widget = QVideoWidget()

        # Create the time box
        time_box = QHBoxLayout()

        # Create the time label
        self.time_label = QLabel()
        self.time_label.setText(milliseconds_to_formatted_string(0))
        self.time_label.setFixedHeight(24)
        time_box.addWidget(self.time_label)

        # Create the position slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.position_slider.setToolTip("Position")
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        # Add the position slider to the time box
        time_box.addWidget(self.position_slider)

        # Create the duration time box
        self.duration_label = QLabel()
        self.duration_label.setText(milliseconds_to_formatted_string(0))
        self.duration_label.setFixedHeight(24)
        time_box.addWidget(self.duration_label)

        # Create the button layout
        button_box = QHBoxLayout()

        # Create Assets object
        assets = Assets()

        # Create the -10 frame button
        backward_10_frames = self.add_player_button(
            QIcon(assets.get("minus10.png")),
            "10th Previous Frame",
            partial(self.move_to_frame, -10),
            button_box,
        )

        # Create the -5 frame button
        backward_5_frames = self.add_player_button(
            QIcon(assets.get("minus5.png")),
            "5th Previous Frame",
            partial(self.move_to_frame, -5),
            button_box,
        )

        # Create the previous frame button
        previous_frame = self.add_player_button(
            QIcon(assets.get("minus1.png")),
            "Previous Frame",
            partial(self.move_to_frame, -1),
            button_box,
        )

        # Create the play/pause button
        self.play_button = self.add_player_button(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            "Play",
            self.play_pause,
            button_box,
        )

        # Create the stop button
        self.stop_button = self.add_player_button(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop),
            "Stop",
            self.stop,
            button_box,
        )

        # Create the next frame button
        next_frame = self.add_player_button(
            QIcon(assets.get("plus1.png")),
            "Next Frame",
            partial(self.move_to_frame, 1),
            button_box,
        )

        # Create the +5 frame button
        forward_5_frames = self.add_player_button(
            QIcon(assets.get("plus5.png")),
            "5th Next Frame",
            partial(self.move_to_frame, 5),
            button_box,
        )

        # Create the +10 frame button
        forward_10_frames = self.add_player_button(
            QIcon(assets.get("plus10.png")),
            "10th Next Frame",
            partial(self.move_to_frame, 10),
            button_box,
        )

        self.frame_buttons = [
            backward_10_frames,
            backward_5_frames,
            previous_frame,
            next_frame,
            forward_5_frames,
            forward_10_frames,
        ]

        button_box.addStretch(1)

        # Create the volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.setToolTip("Volume")
        # Add the volume slider to the button layout
        button_box.addWidget(self.volume_slider)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # Create the main layout and add the button layout and video widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(video_widget)
        self.layout.addLayout(time_box)
        self.layout.addLayout(button_box)

        # Setup the media player
        self.media_player.setVideoOutput(video_widget)
        self.media_player.playbackStateChanged.connect(
            self.playback_state_changed
        )
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        # Setup the audio output
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Prevent the individual UIs from getting the focus
        for ui in [
            self.play_button,
            self.stop_button,
            self.volume_slider,
            self.position_slider,
            video_widget,
        ] + self.frame_buttons:
            ui.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Add the main layout to the main window
        self.setLayout(self.layout)

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_time_label)

    def play_pause(self):
        """Toggle play/pause status"""
        if (
            self.media_player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        ):
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop(self):
        """Stop player"""
        self.media_player.stop()
        self.play_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )

    def set_volume(self, volume):
        """Set the volume"""
        self.audio_output.setVolume(volume / 100)

    def playback_state_changed(self, state):
        """Set the button icon when media changes state"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.timer.start()
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.timer.stop()
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            # Fix : stop to the write frame
            self.set_position(self.media_player.position())

        self.stop_button.setEnabled(
            state != QMediaPlayer.PlaybackState.StoppedState
        )
        self.window.menu.stop_action.setEnabled(
            state != QMediaPlayer.PlaybackState.StoppedState
        )
        for ui in self.frame_buttons:
            ui.setEnabled(state == QMediaPlayer.PlaybackState.PausedState)

        for action in [
            self.window.menu.previous_frame_action,
            self.window.menu.next_frame_action,
            self.window.menu.fifth_previous_frame_action,
            self.window.menu.tenth_previous_frame_action,
            self.window.menu.fifth_next_frame_action,
            self.window.menu.tenth_next_frame_action,
            self.window.menu.add_timeline_action,
            self.window.menu.add_occurrence_action,
        ]:
            action.setEnabled(state == QMediaPlayer.PlaybackState.PausedState)

    def media_status_changed(self, state):
        if state == QMediaPlayer.MediaStatus.LoadedMedia:
            # Enable play button
            self.window.menu.play_action.setEnabled(True)
            # Enable save project button
            self.window.menu.save_project_action.setEnabled(True)
            # Check if metadata is available
            metadata = self.media_player.metaData()
            if metadata:
                # If metadata is available, set the frame rate
                fps = metadata.value(QMediaMetaData.Key.VideoFrameRate)
                self.mfps = int(1000 / fps)
            else:
                self.mfps = None

        if state == QMediaPlayer.MediaStatus.BufferedMedia:
            if self.window.files.data_to_load:
                self.window.files.load_data_file(self.window.files.data_to_load)
                self.window.time_pane.changed = False

    def position_changed(self, position):
        """Update the position slider"""
        self.position_slider.setValue(position)
        self.window.time_pane.time = position
        self.update_time_label()
        self.window.time_pane.update()

    def duration_changed(self, duration):
        """Update the duration slider"""
        self.position_slider.setRange(0, duration)
        self.window.time_pane.duration = duration
        self.duration_label.setText(milliseconds_to_formatted_string(duration))
        self.window.time_pane.update()

    def set_position(self, position):
        """Set the position"""
        position = int(self.mfps * floor(position / self.mfps) + self.mfps / 2)
        if position < 0:
            position = int(self.mfps / 2)
        self.window.time_pane.view.set_position(position)

    def move_to_frame(self, nb_frame, checked=False):
        state = self.media_player.playbackState()
        if self.mfps is None or state != QMediaPlayer.PlaybackState.PausedState:
            return
        self.set_position(self.media_player.position() + (self.mfps * nb_frame))

    def update_time_label(self):
        """Update the time label"""
        self.time_label.setText(
            milliseconds_to_formatted_string(self.media_player.position())
        )

    def add_player_button(self, icon, tooltip, cbfunc, hbox):
        ui = QPushButton()
        ui.setEnabled(False)
        ui.setFixedHeight(24)
        ui.setIconSize(QSize(16, 16))
        ui.setIcon(icon)
        ui.setToolTip(tooltip)
        ui.clicked.connect(cbfunc)
        hbox.addWidget(ui)
        return ui
