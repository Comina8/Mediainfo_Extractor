import sys
import os
import re
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFileDialog, QProgressBar
from pymediainfo import MediaInfo
from PyQt5.QtCore import Qt
from typing import Tuple
from multiprocessing import Pool, cpu_count


class VideoAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.file_info_list = []
        self.skipped_files = []

    def initUI(self):
        self.setWindowTitle('Video Analyzer')
        self.setGeometry(500, 500, 400, 200)

        # Add label to display messages
        self.label = QLabel(self)
        self.label.setText('Drag and drop a video file here')
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # Create a progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        self.setLayout(layout)

        # Enable drag and drop
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        event.accept()
        urls = event.mimeData().urls()
        if urls:
            file_paths = []
            for url in urls:
                path = url.toLocalFile()
                if os.path.isdir(path):
                    for foldername, subfolders, filenames in os.walk(path):
                        for filename in filenames:
                            file_paths.append(os.path.join(foldername, filename))
                elif os.path.isfile(path):
                    file_paths.append(path)
                else:
                    self.skipped_files.append(path)

            self.progressBar.setMaximum(len(file_paths))
            self.progressBar.setValue(0)

            pool = Pool(cpu_count())
            results = pool.map(get_frame_rate, file_paths)
            pool.close()
            pool.join()

            for i, result in enumerate(results):
                if result is None:
                    self.skipped_files.append(file_paths[i])
                else:
                    filename = os.path.basename(file_paths[i])
                    result = (filename,) + result
                    self.file_info_list.append(result)
                    self.write_to_csv(result)
                    self.progressBar.setValue(i + 1)

            if self.skipped_files:
                message = f'{len(file_paths)} items processed. {len(self.skipped_files)} items skipped. Results saved to "results.csv".'
            else:
                message = f'{len(file_paths)} items processed. Results saved to "results.csv".'
            self.label.setText(message)
        else:
            self.label.setText('Please drop files or folders')

    def write_to_csv(self, result: Tuple[str, str, str, str, str, str, str, str]):
        with open('results.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(result)

    def closeEvent(self, event):
        # Write skipped files to a separate file
        if self.skipped_files:
            with open('skipped_files.txt', 'w') as f:
                for item in self.skipped_files:
                    f.write("%s\n" % item)


def get_frame_rate(filename: str) -> Tuple[str, str, str, str, str]:
    try:
        media_info = MediaInfo.parse(filename)
    except Exception:
        return None

    video_frame_rate = "N/A"
    audio_frame_rate = "N/A"
    mxf_frame_rate = "N/A"
    sdti_frame_rate = "N/A"
    timecode_frame_rate = "N/A"
    other1_frame_rate = "N/A"
    other2_frame_rate = "N/A"
    other3_frame_rate = "N/A"

    other_tracks = []
    for track in media_info.tracks:
        if track.track_type == 'Video':
            video_frame_rate = f"{track.frame_rate}/1"
        elif track.track_type == 'Audio':
            audio_frame_rate = f"{track.sampling_rate}/1"
        elif track.track_type == 'Other':
            other_tracks.append(track.frame_rate)
        elif track.track_type == 'Data':
            # Extract SDTI frame rate from track name, if possible
            sdti_match = track.track_name and re.search(r'(\d+)i_SDTI', track.track_name)
            if sdti_match:
                sdti_frame_rate = f"{sdti_match.group(1)}/1"
        elif track.track_type == 'Time code':
            if track.format == 'MXF TC':
                if track.time_code_settings == 'Material Package' or track.time_code_settings == 'Source Package':
                    timecode_frame_rate = f"{track.frame_rate}/1"
                    break
            elif track.format == 'SMPTE TC' and track.muxing_mode == 'SDTI':
                timecode_frame_rate = f"{track.frame_rate}/1"
                break

    if len(other_tracks) >= 1:
        other1_frame_rate = f"{other_tracks[0]}/1"
    if len(other_tracks) >= 2:
        other2_frame_rate = f"{other_tracks[1]}/1"
    if len(other_tracks) >= 3:
        other3_frame_rate = f"{other_tracks[2]}/1"

    return video_frame_rate, audio_frame_rate, mxf_frame_rate, sdti_frame_rate, timecode_frame_rate, other1_frame_rate, other2_frame_rate, other3_frame_rate


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    ex = VideoAnalyzer()
    ex.show()
    sys.exit(app.exec_())