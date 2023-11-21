import csv
import os
import re
import time
import multiprocessing
import sys
from datetime import timedelta
from pymediainfo import MediaInfo
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot


class Worker(QThread):
    progress_signal = pyqtSignal(int)
    row_signal = pyqtSignal(list)

    def __init__(self, filenames, output_file):
        super().__init__()
        self.filenames = filenames
        self.output_file = output_file

    def run(self):
        for filename in self.filenames:
            try:
                media_info = MediaInfo.parse(filename)
            except Exception:
                continue

            general_track = media_info.tracks[0]
            video_track = next((track for track in media_info.tracks if track.track_type == 'Video'), None)
            audio_tracks = [track for track in media_info.tracks if track.track_type == 'Audio']
            other_tracks = [track for track in media_info.tracks if track.track_type not in ['General', 'Video', 'Audio']][:3]

            row = [
                os.path.abspath(filename),
                general_track.format,
                str(timedelta(milliseconds=general_track.duration)),
                general_track.bit_rate,
                general_track.writing_application,
                video_track.format if video_track else '',
                video_track.commercial_name if video_track else '',
                video_track.format_profile if video_track else '',
                video_track.gop if video_track else '',
                str(timedelta(milliseconds=video_track.duration)) if video_track else '',
                video_track.bit_rate if video_track else '',
                video_track.width if video_track else '',
                video_track.height if video_track else '',
                video_track.display_aspect_ratio if video_track else '',
                video_track.frame_rate if video_track else '',
                video_track.color_space if video_track else '',
                video_track.chroma_subsampling if video_track else '',
                video_track.bit_depth if video_track else '',
                video_track.scan_type if video_track else '',
                video_track.scan_order if video_track else '',
                video_track.time_code_of_first_frame if video_track else '',
                video_track.gop_structure if video_track else '',
                audio_tracks[0].format if audio_tracks else '',
                str(timedelta(milliseconds=audio_tracks[0].duration)) if audio_tracks else '',
                audio_tracks[0].bit_rate if audio_tracks else '',
                audio_tracks[0].channel_s if audio_tracks else '',
                audio_tracks[0].sampling_rate if audio_tracks else '',
                other_tracks[0].track_type if other_tracks else '',
                other_tracks[0].frame_rate if other_tracks else '',
                other_tracks[0].time_code_of_first_frame if other_tracks else '',
                other_tracks[0].time_code_of_last_frame if other_tracks else ''
            ]

            self.row_signal.emit(row)

            time.sleep(0.1)

            self.progress_signal.emit(100 * (self.filenames.index(filename) + 1) // len(self.filenames))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('MediaInfo Extractor')
        self.setFixedSize(520, 160)

        self.setAcceptDrops(True)  # Enable drag and drop

        self.file_label = QLabel('Drag and drop files or folders here', self)
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setGeometry(0, 0, 500, 100)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(20, 100, 500, 50)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.worker = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        filenames = []
        for url in event.mimeData().urls():
            if os.path.isfile(url.toLocalFile()):
                filenames.append(url.toLocalFile())
            elif os.path.isdir(url.toLocalFile()):
                for root, dirs, files in os.walk(url.toLocalFile()):
                    for file in files:
                        filenames.append(os.path.join(root, file))
        filenames = [filename for filename in filenames if re.match(r'.*\.(avi|mp4|mkv|mov|flv|mxf)$', filename, re.IGNORECASE)]

        if filenames:
            self.file_label.setText('Extracting media info...')
            self.progress_bar.setValue(0)

            output_file, _ = QFileDialog.getSaveFileName(self, 'Save CSV', '', 'CSV Files (*.csv)')

            if output_file:
                self.worker = Worker(filenames, output_file)
                self.worker.progress_signal.connect(self.update_progress_bar)
                self.worker.row_signal.connect(self.write_row_to_csv)
                self.worker.start()

    @pyqtSlot(int)
    def update_progress_bar(self, progress):
        self.progress_bar.setValue(progress)

    @pyqtSlot(list)
    def write_row_to_csv(self, row):
        with open(self.worker.output_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())