import cv2
import threading
import time
import subprocess
import os
import signal
import tempfile
import sys
import platform
import requests
import tarfile
import shutil

class WebcamStreamServer:
    def __init__(self, camera_id=0, rtsp_port=8554, stream_path='/webcam'):
        self.camera_id = camera_id
        self.rtsp_port = rtsp_port
        self.stream_path = stream_path
        self.is_running = False
        self.rtsp_process = None
        self.ffmpeg_process = None
        
        # List available devices first
        self._list_devices()
        
        # Setup mediamtx if not present
        if not os.path.exists('./mediamtx'):
            self._setup_mediamtx()
        
        # Check if ffmpeg is installed
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: ffmpeg not found. Please install it using:")
            print("brew install ffmpeg")
            sys.exit(1)
    
    def _list_devices(self):
        """List available video devices"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', ''],
                stderr=subprocess.PIPE,
                text=True
            )
            print("\nAvailable devices:")
            print(result.stderr)
        except Exception as e:
            print(f"Error listing devices: {e}")
    
    def _setup_mediamtx(self):
        print("Downloading and setting up mediamtx...")
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Download mediamtx
            url = "https://github.com/bluenviron/mediamtx/releases/download/v1.0.0/mediamtx_v1.0.0_darwin_amd64.tar.gz"
            print(f"Downloading from: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, allow_redirects=True)
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Save the tar file
            tar_path = os.path.join(temp_dir, "mediamtx.tar.gz")
            with open(tar_path, "wb") as f:
                f.write(response.content)
            
            print("Download complete, extracting...")
            
            # Extract the tar file
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # Move the mediamtx binary to current directory
            binary_path = os.path.join(temp_dir, "mediamtx")
            shutil.move(binary_path, "./mediamtx")
            
            # Make the binary executable
            os.chmod("mediamtx", 0o755)
            
            # Clean up
            shutil.rmtree(temp_dir)
            print("mediamtx setup completed successfully")
            
        except Exception as e:
            print(f"Error setting up mediamtx: {str(e)}")
            print("\nTrying alternative download method...")
            try:
                # Try direct download using curl
                subprocess.run([
                    'curl', '-L',
                    'https://github.com/bluenviron/mediamtx/releases/download/v1.0.0/mediamtx_v1.0.0_darwin_amd64.tar.gz',
                    '-o', 'mediamtx.tar.gz'
                ], check=True)
                
                subprocess.run(['tar', '-xzf', 'mediamtx.tar.gz'], check=True)
                subprocess.run(['chmod', '+x', 'mediamtx'], check=True)
                os.remove('mediamtx.tar.gz')
                print("mediamtx setup completed successfully using alternative method")
                
            except Exception as e2:
                print(f"Error with alternative method: {str(e2)}")
                print("\nPlease try downloading manually from the browser:")
                print("1. Visit: https://github.com/bluenviron/mediamtx/releases")
                print("2. Find the latest release for darwin_amd64")
                print("3. Download and extract it")
                print("4. Place the 'mediamtx' binary in this directory")
                sys.exit(1)
        
    def start(self):
        self.is_running = True
        
        # Create mediamtx configuration file
        config_content = f"""
paths:
  {self.stream_path[1:]}:
    source: publisher
    sourceProtocol: tcp
    publishUser: ""
    publishPass: ""
    readUser: ""
    readPass: ""

rtspAddress: :{self.rtsp_port}
protocols: [tcp]
rtspTransport: tcp
readTimeout: 30s
writeTimeout: 30s
"""
        with open('mediamtx.yml', 'w') as f:
            f.write(config_content)
        
        # Start mediamtx with config file
        mediamtx_path = os.path.abspath('./mediamtx')
        self.rtsp_process = subprocess.Popen(
            [mediamtx_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("\nStarting RTSP server...")
        time.sleep(5)  # Give more time for the server to start
        
        # Start FFmpeg process to capture webcam and stream to RTSP
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'avfoundation',
            '-framerate', '30',
            '-video_size', '1280x720',
            '-i', '"FaceTime HD Camera":none',  # Use camera name instead of index
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-pix_fmt', 'yuv420p',
            '-g', '30',
            '-f', 'rtsp',
            '-rtsp_transport', 'tcp',
            f'rtsp://localhost:{self.rtsp_port}{self.stream_path}'
        ]
        
        print("\nStarting FFmpeg stream...")
        print(f"Command: {' '.join(ffmpeg_cmd)}")
        
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Check if FFmpeg started successfully
        time.sleep(2)
        if self.ffmpeg_process.poll() is not None:
            error_output = self.ffmpeg_process.stderr.read().decode()
            print(f"\nFFmpeg failed to start. Error output:\n{error_output}")
            print("\nTrying alternative command...")
            
            # Try alternative command with device index
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'avfoundation',
                '-framerate', '30',
                '-video_size', '1280x720',
                '-i', '0:none',  # Use index 0 instead of name
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-tune', 'zerolatency',
                '-pix_fmt', 'yuv420p',
                '-g', '30',
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                f'rtsp://localhost:{self.rtsp_port}{self.stream_path}'
            ]
            
            print(f"Alternative command: {' '.join(ffmpeg_cmd)}")
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            if self.ffmpeg_process.poll() is not None:
                error_output = self.ffmpeg_process.stderr.read().decode()
                print(f"\nAlternative command also failed. Error output:\n{error_output}")
                self.stop()
                sys.exit(1)
        
        print(f"\nRTSP stream started at rtsp://localhost:{self.rtsp_port}{self.stream_path}")
        print("You can view it using VLC Media Player")
        
        # Monitor FFmpeg process
        monitor_thread = threading.Thread(target=self._monitor_ffmpeg)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def _monitor_ffmpeg(self):
        while self.is_running:
            if self.ffmpeg_process.poll() is not None:
                error_output = self.ffmpeg_process.stderr.read().decode()
                print(f"\nFFmpeg process died. Error output:\n{error_output}")
                print("Restarting FFmpeg...")
                self._restart_ffmpeg()
            time.sleep(1)
    
    def _restart_ffmpeg(self):
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except:
                pass
            
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'avfoundation',
            '-framerate', '30',
            '-video_size', '1280x720',
            '-i', '0:none',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-pix_fmt', 'yuv420p',
            '-g', '30',
            '-f', 'rtsp',
            '-rtsp_transport', 'tcp',
            f'rtsp://localhost:{self.rtsp_port}{self.stream_path}'
        ]
        
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    def stop(self):
        self.is_running = False
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except:
                pass
        if self.rtsp_process:
            try:
                self.rtsp_process.terminate()
                self.rtsp_process.wait(timeout=5)
            except:
                pass 