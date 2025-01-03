
# RTSP Webcam Server

A Python-based RTSP server that streams your webcam feed. This project uses FFmpeg for video capture and MediaMTX (formerly rtsp-simple-server) for RTSP streaming.

## Features

- Stream webcam feed over RTSP
- Support for multiple video devices
- Automatic device detection
- TCP transport for reliable streaming
- Auto-recovery from stream interruptions
- Configurable video quality and resolution

## Prerequisites

- Python 3.x
- FFmpeg
- macOS (currently optimized for macOS's AVFoundation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RTVLABS/RTSP-SERVER-PUPPET.git
cd RTSP-SERVER-PUPPET
```

2. Install required Python packages:
```bash
pip install opencv-python requests
```

3. Install FFmpeg:
```bash
brew install ffmpeg
```

## Usage

1. Start the RTSP server:
```bash
python main.py
```

2. The server will:
   - List available video devices
   - Download and set up MediaMTX (first run only)
   - Start the RTSP server
   - Begin streaming from your webcam

3. Connect to the stream using any RTSP-capable player (e.g., VLC):
   - Stream URL: `rtsp://localhost:8554/webcam`

### Using VLC to View the Stream

1. Open VLC Media Player
2. Go to Media -> Open Network Stream
3. Enter the URL: `rtsp://localhost:8554/webcam`
4. Click Play

## Configuration

The server can be configured by modifying the following parameters in `main.py`:

- `camera_id`: Camera device index (default: 0)
- `rtsp_port`: RTSP server port (default: 8554)
- `stream_path`: Stream path (default: /webcam)

Video settings can be adjusted in `rtsp_webcam_server.py`:
- Resolution: 1280x720 (default)
- Framerate: 30 fps (default)
- Video codec: H.264
- Preset: ultrafast
- Transport: TCP

## Troubleshooting

1. **No video devices found:**
   - Check if your webcam is properly connected
   - Try listing devices using: `ffmpeg -f avfoundation -list_devices true -i ""`

2. **Connection refused:**
   - Make sure no other service is using port 8554
   - Check if MediaMTX is running properly

3. **Stream not working:**
   - Verify your webcam works in other applications
   - Check the FFmpeg error output
   - Try restarting the server

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [MediaMTX](https://github.com/bluenviron/mediamtx) for the RTSP server
- [FFmpeg](https://ffmpeg.org/) for video capture and encoding
- [OpenCV](https://opencv.org/) for Python video capabilities

