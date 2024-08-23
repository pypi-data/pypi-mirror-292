from ffmpeg import FFmpeg, Progress
import ctypes
import subprocess
import os
import sys
import numpy as np
import time
import threading

if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

def run_server():
    dll_path = os.path.join(base_path, 'atommedia.dll')
    dll = ctypes.CDLL(dll_path)
    yml_path = os.path.join(base_path, 'atomconfig.yml')

    result = dll.RunMediaServer(yml_path.encode('utf-8'))

class RTSPStreamer:
    def __init__(self, width, height, output_postfix, quality):
        self.width = width
        self.height = height
        self.output_postfix = output_postfix
        self.running = True

        current_path = os.path.dirname(os.path.abspath(__file__))
        self.path_to_ffmpeg = os.path.join(current_path, 'decoder.exe')

        self.ffmpeg_command = [
            self.path_to_ffmpeg,
            '-y',
            '-f', 'rawvideo',
            '-fflags', 'nobuffer',
            '-flags', 'low_delay',
            '-probesize', '32',
            '-analyzeduration', '0',
            '-pix_fmt', 'bgra',
            '-s', f'{self.width}x{self.height}',
            '-i', 'pipe:0',
            '-c:v', 'mpeg4',
            '-qscale:v', f'{quality}',
            '-b:v', '20M',
            '-maxrate', '20M',
            '-bufsize', '40M',
            '-g', '1',
            '-f', 'rtsp',
            f'rtsp://localhost:8554/{self.output_postfix}'
        ]

        self.dark_frame = np.zeros((
                self.width,
                self.height,
                4
            ), dtype=np.uint8)

        self.process = None

    def start(self, conn, _):
        self.process = subprocess.Popen(self.ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        while conn.poll():
            conn.recv()

        data = self.dark_frame
        
        while self.running:
            try:
                if conn.poll():
                    while conn.poll():
                        data = conn.recv()
                    if str(data) == "Stop":
                        self.stop()
                        break
                self.send_frame_to_ffmpeg(data)
                time.sleep(0.04)

            except EOFError:
                break
            except BrokenPipeError:
                break

    def stop(self):
        self.running = False
        self.process.stdin.close()
        self.process.wait()

    def send_frame_to_ffmpeg(self, frame):
        self.process.stdin.write(frame.tobytes())
    