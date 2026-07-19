import socket
import subprocess
import time
import tempfile
import shutil

from os.path import abspath, dirname, join
from pynes.cart import Cart
from neslib.library import lib
from neslib.font import font_chr

HEADER_SIZE = 16
PRG_SIZE = 16384

SCRIPT_DIR = abspath(dirname(__file__))


class MemoryProxy:
    """Helper class to allow bracket and slice access to CPU RAM."""

    def __init__(self, runner):
        self.runner = runner

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start or 0
            stop = key.stop or 0x800
            step = key.step or 1
            return [
                self.runner._read_cpu_byte(addr)
                for addr in range(start, stop, step)
            ]
        return self.runner._read_cpu_byte(key)


class VramProxy:
    """Helper class to allow bracket and slice access to PPU VRAM."""

    def __init__(self, runner):
        self.runner = runner

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start or 0
            stop = key.stop or 0x4000
            step = key.step or 1
            return [
                self.runner._read_ppu_vram_byte(addr)
                for addr in range(start, stop, step)
            ]
        return self.runner._read_ppu_vram_byte(key)


class FCEUXRunner:
    def __init__(
        self, source, host='127.0.0.1', port=8888, fceux_path='fceux'
    ):
        self.host = host
        self.port = port
        self.fceux_path = fceux_path
        self.process = None
        self.conn = None

        # 1. Compile the source artifact identically to your original architecture
        cart = Cart(libraries=[lib], chr_banks=1, chr_data=font_chr())
        self.rom = cart.to_nes(source)

        prg = self.rom[HEADER_SIZE : HEADER_SIZE + PRG_SIZE]

        # Extract vectors to coordinate manual NMI triggers over the socket
        self.nmi_vector = prg[0x3FFA] | (prg[0x3FFB] << 8)

        # Wire structural proxy layers to match original headless syntax expectations
        self.cpu = type("ProxyCPU", (), {"memory": MemoryProxy(self)})()
        self.ppu = type("ProxyPPU", (), {"vram": VramProxy(self)})()

    def start_fceux(self, lua_script_path="fceux_runner.lua"):
        # with tempfile.TemporaryDirectory() as tmp:
        #     rom_path = join(tmp, 'test.nes')
        #     with open(rom_path, 'wb') as f:
        #         f.write(self.rom)
        rom_path = join('/tmp', 'test.nes')
        with open(rom_path, 'wb') as f:
            f.write(self.rom)
        """Launches FCEUX as a server and connects the Python client socket."""
        abs_lua_path = join(SCRIPT_DIR, lua_script_path)
        # Command configurations to invoke FCEUX headlessly with the server script
        cmd = [
            shutil.which('fceux'),
            # "--sound", "0",            # Disable audio processing
            # "--frameskip", "0",        # Enforce frame-by-frame lock step
            "--loadlua",
            abs_lua_path,  # Load the TCP socket server script
            # "--winsound", "0"
            rom_path,
        ]
        print(rom_path)
        self.stdout_log = open("fceux_stdout.log", "a", encoding="utf-8")
        self.stderr_log = open("fceux_stderr.log", "a", encoding="utf-8")

        # Start the background process running the server
        self.process = subprocess.Popen(
            cmd, stdout=self.stdout_log, stderr=self.stderr_log
        )

        # Allow FCEUX a moment to start and bind its listening port
        time.sleep(0.8)

        # Create a client socket and dial the emulator
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        retries = 5
        while retries > 0:
            try:
                self.conn.connect((self.host, self.port))
                break
            except ConnectionRefusedError:
                print(f"Connection refused, retries left: {retries}")
                time.sleep(0.5)
                retries -= 1

        if retries == 0:
            self.close_fceux()
            raise TimeoutError(
                "[RUNNER ERROR] Failed to connect to FCEUX server instance."
            )

        # Stream the compiled ROM data over to the server immediately after connecting
        # self.conn.sendall(f"LOAD:{len(self.rom)}\n".encode())
        # self.conn.sendall(self.rom)
        # print(self.conn.recv(4))
        # assert self.conn.recv(4) == b'ACK\n'

    def close_fceux(self):
        """Safely tears down the client socket connection and kills the FCEUX process."""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None

        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

        if self.stdout_log:
            self.stdout_log.close()
        if self.stderr_log:
            self.stderr_log.close()

    def _read_cpu_byte(self, address):
        """Dispatches an atomic CPU RAM byte query to FCEUX."""
        self.conn.sendall(f"READ:{address}\n".encode())
        return int.from_bytes(self.conn.recv(1), byteorder='big')

    def _read_ppu_vram_byte(self, address):
        """Dispatches an atomic PPU VRAM byte query to FCEUX (read
        through the PPU registers at the frame boundary)."""
        self.conn.sendall(f"VRAM:{address}\n".encode())
        return self._recv_exact(1)[0]

    def read_pixels(self, x, y, width, height):
        """Reads an RGB block of the rendered screen: bytes in
        r, g, b order, row by row."""
        self.conn.sendall(f"PIXELS:{x},{y},{width},{height}\n".encode())
        return self._recv_exact(width * height * 3)

    def _recv_exact(self, size):
        data = b''
        while len(data) < size:
            chunk = self.conn.recv(size - len(data))
            if not chunk:
                raise ConnectionError('FCEUX closed the connection')
            data += chunk
        return data

    def press(self, buttons):
        """Applies the target button mask on the first controller layout."""
        self.conn.sendall(f"PADS:{buttons & 0xFF}\n".encode())
        assert self.conn.recv(4) == b'ACK\n'

    def release(self):
        """Releases all active keys on the pad layout."""
        self.press(0x00)

    def _run(self):
        """Tells FCEUX to execute instruction steps until a JMP-to-self loop parks."""
        self.conn.sendall(b"RUN_IDLE\n")
        status = self.conn.recv(10).decode().strip()
        if status == "RUNAWAY":
            raise RuntimeError('runaway execution (no idle loop reached)')
        if status != 'OK':
            raise RuntimeError('Not OK')

    def run_reset(self):
        """Runs the RESET vector execution block until the main loop parks."""
        self._run()

    def run_frames(self, frames):
        """Advances whole frames synchronously by force injecting NMIs."""
        for _ in range(frames):
            self.conn.sendall(b"NMI_ENABLED\n")
            if self.conn.recv(2).decode().strip() == "0":
                continue

            self.conn.sendall(f"NMI:{self.nmi_vector}\n".encode())
            status = self.conn.recv(10).decode().strip()
            if status == "RUNAWAY":
                raise RuntimeError('runaway execution (no idle loop reached)')
