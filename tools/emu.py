"""Minimal headless libretro frontend (snes9x core) for scripted testing of DKC.

Usage from Python:
    from emu import Emu
    e = Emu("roms/dkc_orig.sfc")
    e.run(60)                      # run 60 frames
    e.press(1, "START"); e.run(1)  # hold START on player 1 for one frame
    e.ram[0x500]                   # read WRAM ($7E0000 + offset)
    e.screenshot("shot.png")
"""
import ctypes as C
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(HERE, os.environ.get("CORE", "snes9x") + "_libretro.so")

BTN = dict(B=0, Y=1, SELECT=2, START=3, UP=4, DOWN=5, LEFT=6, RIGHT=7, A=8, X=9, L=10, R=11)


class retro_game_info(C.Structure):
    _fields_ = [("path", C.c_char_p), ("data", C.c_void_p), ("size", C.c_size_t), ("meta", C.c_char_p)]


class retro_memory_descriptor(C.Structure):
    _fields_ = [("flags", C.c_uint64), ("ptr", C.c_void_p), ("offset", C.c_size_t), ("start", C.c_size_t),
                ("select", C.c_size_t), ("disconnect", C.c_size_t), ("len", C.c_size_t), ("addrspace", C.c_char_p)]


class retro_memory_map(C.Structure):
    _fields_ = [("descriptors", C.POINTER(retro_memory_descriptor)), ("num_descriptors", C.c_uint)]


class retro_system_av_info(C.Structure):
    _fields_ = [("base_width", C.c_uint), ("base_height", C.c_uint), ("max_width", C.c_uint),
                ("max_height", C.c_uint), ("aspect_ratio", C.c_float),
                ("fps", C.c_double), ("sample_rate", C.c_double)]


ENV_CB = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO_CB = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO_CB = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
AUDIOB_CB = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL_CB = C.CFUNCTYPE(None)
STATE_CB = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)
LOG_CB = C.CFUNCTYPE(None, C.c_int, C.c_char_p)      # (variadica en C; ignoramos el resto)


class retro_log_callback(C.Structure):
    _fields_ = [("log", LOG_CB)]


class Emu:
    def __init__(self, rom, core=CORE, skip_splash=True):
        self.lib = C.CDLL(core)
        self.held = {1: set(), 2: set()}
        self.frame = None
        self.pixfmt = 0  # 0=0RGB1555, 1=XRGB8888, 2=RGB565
        self.frames = 0
        self.wram_ptr = None
        self._log_cb = LOG_CB(lambda lvl, msg: None)
        self._log_struct = retro_log_callback(self._log_cb)             # via RETRO_ENVIRONMENT_SET_MEMORY_MAPS (bsnes)
        self._sysdir = C.c_char_p(HERE.encode())
        self._cbs = [ENV_CB(self._env), VIDEO_CB(self._video), AUDIO_CB(lambda l, r: None),
                     AUDIOB_CB(lambda d, n: n), POLL_CB(lambda: None), STATE_CB(self._state)]
        L = self.lib
        L.retro_set_environment(self._cbs[0])
        L.retro_set_video_refresh(self._cbs[1])
        L.retro_set_audio_sample(self._cbs[2])
        L.retro_set_audio_sample_batch(self._cbs[3])
        L.retro_set_input_poll(self._cbs[4])
        L.retro_set_input_state(self._cbs[5])
        L.retro_init()
        self.romdata = open(rom, "rb").read()
        self._rombuf = C.create_string_buffer(self.romdata, len(self.romdata))
        gi = retro_game_info(os.path.abspath(rom).encode(), C.cast(self._rombuf, C.c_void_p), len(self.romdata), None)
        if not L.retro_load_game(C.byref(gi)):
            raise RuntimeError("load_game failed")
        L.retro_get_memory_data.restype = C.c_void_p
        L.retro_get_memory_size.restype = C.c_size_t
        L.retro_serialize_size.restype = C.c_size_t
        ptr = L.retro_get_memory_data(2)  # SYSTEM_RAM = WRAM 128KB
        size = L.retro_get_memory_size(2)
        if not ptr and self.wram_ptr:     # bsnes: WRAM via mapas de memoria
            ptr, size = self.wram_ptr, 0x20000
        if not ptr:
            raise RuntimeError('el nucleo no expone la WRAM (RETRO_MEMORY_SYSTEM_RAM)')
        self.ram = (C.c_uint8 * size).from_address(ptr)
        if skip_splash:
            self.skip_splash()

    def skip_splash(self):
        """Si la ROM tiene la pantalla inicial (patch/splash.asm: JML en el reset), la salta con START
        para que el arranque quede igual que en la ROM original (self.frames vuelve a 0)."""
        if self.romdata[0x8000] != 0x5C:
            return
        for _ in range(300):
            self.run(1)
            if self.ram[0x4C0] == 0x5A:
                break
        self.run(50)                                  # tiempo minimo antes de aceptar botones
        self.set_buttons(1, "START")
        while self.ram[0x4C0] == 0x5A:
            self.run(1)
        self.set_buttons(1)
        self.frames = 0

    # --- callbacks ---
    def _env(self, cmd, data):
        cmd &= 0xFFFF
        if cmd == 10:  # SET_PIXEL_FORMAT
            self.pixfmt = C.cast(data, C.POINTER(C.c_int))[0]
            return True
        if cmd in (9, 31):  # GET_SYSTEM_DIRECTORY / GET_SAVE_DIRECTORY
            C.cast(data, C.POINTER(C.c_char_p))[0] = self._sysdir.value
            return True
        if cmd == 36:  # SET_MEMORY_MAPS: buscar la WRAM ($7E0000, 128 KB)
            mm = C.cast(data, C.POINTER(retro_memory_map))[0]
            for i in range(mm.num_descriptors):
                d = mm.descriptors[i]
                if d.ptr and d.start == 0x7E0000 and d.len >= 0x20000:
                    self.wram_ptr = d.ptr + d.offset
            return True
        if cmd == 27:  # GET_LOG_INTERFACE
            C.cast(data, C.POINTER(retro_log_callback))[0] = self._log_struct
            return True
        if cmd == 3:  # GET_CAN_DUPE
            C.cast(data, C.POINTER(C.c_bool))[0] = True
            return True
        return False

    def _video(self, data, w, h, pitch):
        if data:
            self.frame = (C.string_at(data, pitch * h), w, h, pitch)

    def _state(self, port, device, index, id_):
        if device != 1:
            return 0
        return 1 if id_ in self.held.get(port + 1, ()) else 0

    # --- API ---
    def set_buttons(self, player, *names):
        self.held[player] = {BTN[n] for n in names}

    def run(self, n=1):
        for _ in range(n):
            self.lib.retro_run()
            self.frames += 1

    def tap(self, player, name, hold=2, after=10):
        self.set_buttons(player, name)
        self.run(hold)
        self.set_buttons(player)
        self.run(after)

    def r8(self, a):
        return self.ram[a & 0x1FFFF]

    def r16(self, a):
        a &= 0x1FFFF
        return self.ram[a] | (self.ram[a + 1] << 8)

    def w8(self, a, v):
        self.ram[a & 0x1FFFF] = v & 0xFF

    def w16(self, a, v):
        self.w8(a, v)
        self.w8(a + 1, v >> 8)

    def save_state(self):
        n = self.lib.retro_serialize_size()
        buf = C.create_string_buffer(n)
        assert self.lib.retro_serialize(buf, C.c_size_t(n))
        return buf.raw

    def load_state(self, raw):
        buf = C.create_string_buffer(raw, len(raw))
        assert self.lib.retro_unserialize(buf, C.c_size_t(len(raw)))
        if os.environ.get('COOP'):      # pruebas: forzar el modo "Two player team" (co-op)
            self.w16(0x42, 1)

    def image(self):
        from PIL import Image
        import numpy as np
        raw, w, h, pitch = self.frame
        if self.pixfmt == 1:
            a = np.frombuffer(raw, dtype=np.uint32).reshape(h, pitch // 4)[:, :w]
            rgb = np.stack([(a >> 16) & 255, (a >> 8) & 255, a & 255], -1).astype(np.uint8)
        else:
            a = np.frombuffer(raw, dtype=np.uint16).reshape(h, pitch // 2)[:, :w].astype(np.uint32)
            if self.pixfmt == 2:
                r, g, b = (a >> 11) & 31, (a >> 5) & 63, a & 31
                rgb = np.stack([r * 255 // 31, g * 255 // 63, b * 255 // 31], -1).astype(np.uint8)
            else:
                r, g, b = (a >> 10) & 31, (a >> 5) & 31, a & 31
                rgb = np.stack([r * 255 // 31, g * 255 // 31, b * 255 // 31], -1).astype(np.uint8)
        return Image.fromarray(rgb)

    def screenshot(self, path):
        self.image().save(path)
