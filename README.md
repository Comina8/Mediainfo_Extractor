**MediaInfo Extractor**

The MediaInfo Extractor is a Python application that extracts detailed information about media files such as videos and audios. It utilizes the MediaInfo library to parse the media files and retrieve various metadata.

**Features**<br>
- Drag and drop support: You can drag and drop files or folders onto the application window to extract media info.<br>
- Supported file formats: The application supports media file formats including AVI, MP4, MKV, MOV, FLV, and MXF.<br>
- Output to CSV: The extracted media information is saved to a CSV (Comma-Separated Values) file.<br>
- Multi-threaded processing: The extraction process is performed in a separate worker thread to avoid blocking the user interface.<br>

**Usage**<br>

Launch the application.<br>
Drag and drop media files or folders containing media files onto the application window.<br>
The application will start extracting media information from the dropped files.<br>
A progress bar will indicate the progress of the extraction process.<br>
Once the extraction is complete, a dialog will prompt you to save the extracted information as a CSV file.<br>
Choose a location and filename for the CSV file and click "Save."<br>
The CSV file will contain detailed information about the media files, including general information, video tracks, audio tracks, and other tracks.<br>

**Requirements**<br>

Python 3.x<br>
PyQt5 library<br>
pymediainfo library<br>
