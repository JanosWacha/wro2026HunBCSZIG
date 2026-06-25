def startserver(picam2=None):
    import io
    import socketserver
    from http import server
    from threading import Condition

    if not picam2:
        from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    import libcamera

    class StreamingOutput(io.BufferedIOBase):
        def __init__(self):
            self.frame = None
            self.condition = Condition()

        def write(self, buf):
            with self.condition:
                self.frame = buf
                self.condition.notify_all()

    class StreamingHandler(server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/stream.mjpg":
                self.send_response(200)
                self.send_header(
                    "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
                )
                self.send_header("Cache-Control", "no-cache, private")
                self.end_headers()
                try:
                    while True:
                        with output.condition:
                            output.condition.wait()
                            frame = output.frame
                        self.wfile.write(b"--FRAME\r\n")
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b"\r\n")
                except Exception as e:
                    print(e.args)
            else:
                self.send_error(404)

    if not picam2:
        picam2 = Picamera2()
        picam2.configure(
            picam2.create_video_configuration(
                main={"format": "XRGB8888", "size": (320, int(1080 / 1920 * 320))}
            )
        )
    output = StreamingOutput()
    picam2.start_recording(JpegEncoder(), FileOutput(output))

    class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
        allow_reuse_address = True
        daemon_threads = True

    try:
        server = StreamingServer(("0.0.0.0", 8000), StreamingHandler)
        server.serve_forever()
    finally:
        picam2.stop_recording()


if __name__ == "__main__":
    startserver()
