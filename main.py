from rtsp_webcam_server import WebcamStreamServer

def main():
    # Create and start the RTSP server
    server = WebcamStreamServer(
        camera_id=0,  # Use default webcam
        rtsp_port=8554,  # Standard RTSP port
        stream_path='/webcam'
    )
    
    try:
        print("Starting RTSP server...")
        print("Stream will be available at: rtsp://localhost:8554/webcam")
        server.start()
        
        # Keep the main thread running
        while True:
            input("Press Enter to stop the server...")
            break
            
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.stop()
        print("Server stopped")

if __name__ == "__main__":
    main() 