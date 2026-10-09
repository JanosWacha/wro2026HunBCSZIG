#!/usr/bin/env python3
"""
Picamera2 MJPEG streaming + változó szöveg a HTML oldalon.

Futtatás:   python3 picam_stream.py
Megnyitás:  http://<raspberry-ip>:8000/

Szöveg módosítása futás közben (böngészőből vagy curl-lal):
    http://<raspberry-ip>:8000/set?text=Szia%20vilag
"""

import io
import json
import socketserver
import threading
import time
from http import server
from threading import Condition, Event
from urllib.parse import parse_qs, urlparse

from libcamera import Transform
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
readout = None
get_z_tengely = None
picam2 = None
output = None

def kanyar(r):
    if r[3] / (a:=r[3] + r[0]) < 0.33333 and a > 1000:
        return 'End'
    if r[3] / (a:=r[3] + r[0]) > 0.66666 and a > 1000:
        # Egyenes elejen vagyunk
        return 'Start'
def servo():
    return "-"
event=Event()
event.clear()
thread = None
ser = None
def start_server(pic2=None, ro=None, gr=None, kn=None, sv=None):
    global readout, picam2, get_z_tengely, output, kanyar, servo, thread, ser
    if not ro:
        from Uart_Disctance_Sensor import readout as ro
    readout = ro
    if not pic2:
        from picamera2 import Picamera2
        pic2 = Picamera2()
        lores = 16
        pic2.configure(pic2.create_video_configuration(
                main={"size": (pic2.sensor_resolution[0]//lores, pic2.sensor_resolution[1]//lores)}, raw={"size": pic2.sensor_resolution},
                transform=Transform(hflip=True, vflip=True),  # 180 fokos forgatás
            ))
    picam2 = pic2
    output = StreamingOutput()
    picam2.start_recording(JpegEncoder(), FileOutput(output))
    if not gr:
        from giroszkop import get_z_tengely as gr
    get_z_tengely = gr

    if kn:
        kanyar = kn

    if sv:
        servo = sv

    thread = threading.Thread(target=status_loop, daemon=False)
    thread.start()
    ser=StreamingServer(("", PORT), StreamingHandler)
    try:
        print(f"Stream elindult: http://raspi-robot:{PORT}/")
        ser.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop_recording()

def stop_server():
    event.set()
    thread.join()

PORT = 8000
RESOLUTION = (250, 154)
STATUS_INTERVAL = 0   # mp; ennyi szünet van két adatlekérdezés között

# ---------------------------------------------------------------------------
# Megosztott állapot: ezt olvassa a /status végpont, a weboldal pedig
# folyamatosan (SSE, /events) megkapja és kiírja a kép mellé.
# ---------------------------------------------------------------------------
state_lock = threading.Lock()
custom_text = "Raspi-robot"
start_time = time.time()


def build_status():
    """Itt állítod össze a változó szöveget. Bármit beleírhatsz."""
    with state_lock:
        text = custom_text
    uptime = int(time.time() - start_time)
    r = readout()
    return {
        "uptime": f"{uptime // 60} perc {uptime % 60} mp",
        "tav": f"elöl {r[3]}\nhátul {r[0]}\njobbra {r[2]}\nbalra {r[1]}\nj-b {abs(r[1]-r[2])}\ne+h {r[0]+r[3]}",
        "gyro": f"{get_z_tengely()}",
        "kanyar": kanyar(r),
        "servo": servo(),
    }


# Egyetlen háttérszál olvassa az adatokat (szenzor, giroszkóp, ...), és minden
# változást azonnal elküld az összes csatlakozott böngészőnek.
status_cond = Condition()
status_json = None
status_seq = 0


def status_loop():
    global status_json, status_seq
    last = None
    while not event.is_set():
        try:
            data = json.dumps(build_status(), ensure_ascii=False)
        except Exception as e:
            print("Status hiba:", repr(e))
            time.sleep(1)
            continue
        if data != last:
            with status_cond:
                status_json = data
                status_seq += 1
                status_cond.notify_all()
            last = data
        time.sleep(STATUS_INTERVAL)
    ser.server_close()
    print("Szerver leállt")


PAGE = """<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Raspi-robot stream</title>
<style>
  body { font-family: sans-serif; background: #fff; color: #000; margin: 0; padding: 16px; }
  .wrap { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start; }
  img { max-width: 100%; background: #000; }
  .panel { background: #fff; padding: 16px; min-width: 260px; }
  .panel h2 { margin-top: 0; }
  .row { margin: 6px 0; }
  .row span {white-space: pre-line;}
  .label { color: #000; }
</style>
</head>
<body>
<h1>Picamera2 élő kép</h1>
<div class="wrap">
  <img id="cam" width="640" height="480" alt="stream">
  <div class="panel">
    <h2>Adatok</h2>
    <div class="row"><span class="label">Képkocka/mp:</span> <span id="fps">-</span></div>
    <div class="row"><span class="label">Futási idő:</span> <span id="uptime">-</span></div>
    <div class="row"><span id="tav">-</span></div>
    <div class="row"><span class="label">Giroszkóp:</span> <span id="gyro">-</span></div>
    <div class="row"><span class="label">Hely:</span> <span id="kanyar">-</span></div>
    <div class="row"><span class="label">Szervó:</span> <span id="servo">-</span></div>
  </div>
</div>
<script>
// --- Az adatokat a szerver folyamatosan küldi (SSE), újracsatlakozás automatikus ---
const kulcsok = ['uptime', 'tav', 'gyro', 'kanyar', 'servo'];
let legujabb = null;
const es = new EventSource('/events');
es.onmessage = (e) => { legujabb = JSON.parse(e.data); };

function kirajzol() {
  if (legujabb) {
    for (const k of kulcsok) {
      document.getElementById(k).textContent = legujabb[k] ?? '-';
    }
    legujabb = null;
  }
  requestAnimationFrame(kirajzol);
}
kirajzol();

// --- Az MJPEG streamet a böngésző olvassa be, így az fps-t is itt számoljuk ---
const camImg = document.getElementById('cam');
let frameCount = 0;
let t0 = performance.now();
setInterval(() => {
  const now = performance.now();
  const fps = frameCount * 1000 / (now - t0);
  document.getElementById('fps').textContent = fps.toFixed(1);
  frameCount = 0;
  t0 = now;
}, 1000);

function findHeaderEnd(buf) {
  for (let i = 0; i + 3 < buf.length; i++) {
    if (buf[i] === 13 && buf[i + 1] === 10 && buf[i + 2] === 13 && buf[i + 3] === 10) return i + 4;
  }
  return -1;
}

async function stream() {
  const dec = new TextDecoder();
  let lastUrl = null;
  while (true) {
    try {
      const resp = await fetch('/stream.mjpg', {cache: 'no-store'});
      const reader = resp.body.getReader();
      let buf = new Uint8Array(0);
      while (true) {
        const {value, done} = await reader.read();
        if (done) break;
        const tmp = new Uint8Array(buf.length + value.length);
        tmp.set(buf);
        tmp.set(value, buf.length);
        buf = tmp;
        while (true) {
          const he = findHeaderEnd(buf);
          if (he < 0) break;
          const m = /Content-Length: *([0-9]+)/i.exec(dec.decode(buf.subarray(0, he)));
          if (!m) { buf = buf.subarray(he); continue; }
          const len = parseInt(m[1], 10);
          if (buf.length < he + len) break;
          const url = URL.createObjectURL(new Blob([buf.subarray(he, he + len)], {type: 'image/jpeg'}));
          camImg.src = url;
          if (lastUrl) URL.revokeObjectURL(lastUrl);
          lastUrl = url;
          frameCount++;
          buf = buf.subarray(he + len);
        }
      }
    } catch (e) { /* kapcsolati hiba: újracsatlakozunk */ }
    await new Promise(r => setTimeout(r, 1000));
  }
}
stream();
</script>
</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        if event.is_set():return
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        if event.is_set():return
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def _send(self, code, ctype, body):
        if event.is_set(): return
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if event.is_set():return
        global custom_text
        url = urlparse(self.path)

        if url.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))

        elif url.path == "/status":
            body = json.dumps(build_status(), ensure_ascii=False).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", body)

#        elif url.path == "/set":
#            params = parse_qs(url.query)
#            if "text" in params:
#                with state_lock:
#                    custom_text = params["text"][0][:200]
#            self._send(200, "text/plain; charset=utf-8", b"OK")

        elif url.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            seq = -1
            try:
                while True:
                    with status_cond:
                        status_cond.wait_for(lambda: status_seq != seq, timeout=15)
                        changed = status_seq != seq
                        seq = status_seq
                        data = status_json
                    if changed and data is not None:
                        self.wfile.write(("data: " + data + "\n\n").encode("utf-8"))
                    else:
                        self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass  # a kliens bezárta a kapcsolatot
            except Exception as e:
                print("Events hiba:", repr(e))

        elif url.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                pass  # a kliens bezárta a kapcsolatot
            except Exception as e:
                print("Stream hiba:", repr(e))

        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")

    def log_message(self, *args):
        if event.is_set():return
        pass  # ne spammelje a konzolt


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = False

if __name__ == "__main__":
    start_server()