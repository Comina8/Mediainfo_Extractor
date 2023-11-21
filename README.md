MediaInfo Extractor
The MediaInfo Extractor is a Python application that extracts detailed information about media files such as videos and audios. It utilizes the MediaInfo library to parse the media files and retrieve various metadata.

Features
Drag and drop support: You can drag and drop files or folders onto the application window to extract media info.
Supported file formats: The application supports media file formats including AVI, MP4, MKV, MOV, FLV, and MXF.
Output to CSV: The extracted media information is saved to a CSV (Comma-Separated Values) file.
Multi-threaded processing: The extraction process is performed in a separate worker thread to avoid blocking the user interface.
Usage
Launch the application.
Drag and drop media files or folders containing media files onto the application window.
The application will start extracting media information from the dropped files.
A progress bar will indicate the progress of the extraction process.
Once the extraction is complete, a dialog will prompt you to save the extracted information as a CSV file.
Choose a location and filename for the CSV file and click "Save."
The CSV file will contain detailed information about the media files, including general information, video tracks, audio tracks, and other tracks.
Requirements
Python 3.x
PyQt5 library
pymediainfo library
