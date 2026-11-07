#!/usr/bin/env python3
# msfs_mw.py — Microsoft Flight Simulator 2024 "Multi Window" rotation offset
# degerlerini calisan oyunda duzeltir.
#
# Sorun: SU6 sonrasi Advanced Options > Multi Window ekranindaki
# Lateral / Vertical / Roll rotation offset alanlari kilitleniyor.
# Cozum: oyun bu uc degeri her karede bellekten okuyor; buradan yazinca
# hem ekran hem kamera aninda guncelleniyor.
#
# Bellek duzeni (yazilabilir .data icinde bitisik uc float):
#   +0 vertical rotation offset
#   +4 lateral rotation offset
#   +8 roll rotation offset
#
# Konum build'e gore degisir; bu yuzden sabit adres yerine calisma aninda
# aranir ve bulunan RVA bu makine icin onbellege alinir.

import ctypes, ctypes.wintypes as wt, glob, json, os, re, struct, sys
import numpy as np

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
PAGE_NOACCESS = 0x01
READABLE = {0x02, 0x04, 0x08, 0x20, 0x40, 0x80}
WRITABLE = {0x04, 0x08, 0x40, 0x80}
IMAGE = 0x1000000
LIST_MODULES_ALL = 0x03

EXE_NAMES = ('flightsimulator2024.exe', 'flightsimulator.exe')
FIELDS = ('vertical', 'lateral', 'roll')   # bellek sirasi: +0, +4, +8
ROW_ORDER = ('lateral', 'vertical', 'roll')  # ekranda oyunla ayni sirada
SPAN = 180

# Bu makinede dogrulanan build (module SizeOfImage -> RVA)
DEFAULT_CACHE = {0xE2AC400: 0xA80AF60}


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wt.DWORD), ("__a1", wt.DWORD),
                ("RegionSize", ctypes.c_size_t), ("State", wt.DWORD),
                ("Protect", wt.DWORD), ("Type", wt.DWORD), ("__a2", wt.DWORD)]


class MODULEINFO(ctypes.Structure):
    _fields_ = [("lpBaseOfDll", ctypes.c_void_p), ("SizeOfImage", wt.DWORD),
                ("EntryPoint", ctypes.c_void_p)]


k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
k32.OpenProcess.restype = wt.HANDLE
k32.CloseHandle.argtypes = [wt.HANDLE]
k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                  ctypes.POINTER(ctypes.c_size_t)]
k32.ReadProcessMemory.restype = wt.BOOL
k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.POINTER(ctypes.c_size_t)]
k32.WriteProcessMemory.restype = wt.BOOL
k32.QueryFullProcessImageNameW.argtypes = [wt.HANDLE, wt.DWORD, wt.LPWSTR, ctypes.POINTER(wt.DWORD)]
k32.QueryFullProcessImageNameW.restype = wt.BOOL
psapi.EnumProcesses.argtypes = [ctypes.POINTER(wt.DWORD), wt.DWORD, ctypes.POINTER(wt.DWORD)]
psapi.EnumProcesses.restype = wt.BOOL
psapi.EnumProcessModulesEx.argtypes = [wt.HANDLE, ctypes.POINTER(wt.HMODULE), wt.DWORD,
                                       ctypes.POINTER(wt.DWORD), wt.DWORD]
psapi.EnumProcessModulesEx.restype = wt.BOOL
psapi.GetModuleInformation.argtypes = [wt.HANDLE, wt.HMODULE, ctypes.POINTER(MODULEINFO), wt.DWORD]
psapi.GetModuleInformation.restype = wt.BOOL
psapi.GetModuleBaseNameW.argtypes = [wt.HANDLE, wt.HMODULE, wt.LPWSTR, wt.DWORD]
psapi.GetModuleBaseNameW.restype = wt.DWORD


# --------------------------------------------------------------------------- #
# surec / modul
# --------------------------------------------------------------------------- #
def open_proc(pid):
    access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION
    h = k32.OpenProcess(access, False, pid)
    if not h:
        raise OSError(ctypes.get_last_error(), 'OpenProcess basarisiz')
    return h


def find_pids():
    """Calisan tum Flight Simulator sureclerini dondurur (2024/2020, Store/Steam)."""
    arr = (wt.DWORD * 8192)()
    need = wt.DWORD()
    if not psapi.EnumProcesses(arr, ctypes.sizeof(arr), ctypes.byref(need)):
        return []
    out = []
    for i in range(need.value // 4):
        pid = arr[i]
        if not pid:
            continue
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            continue
        buf = ctypes.create_unicode_buffer(600)
        sz = wt.DWORD(600)
        ok = k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(sz))
        k32.CloseHandle(h)
        if ok and os.path.basename(buf.value).lower() in EXE_NAMES:
            out.append(pid)
    return out


def module_info(h):
    """(taban, SizeOfImage) — exe modulu."""
    mods = (wt.HMODULE * 2048)()
    need = wt.DWORD()
    if not psapi.EnumProcessModulesEx(h, mods, ctypes.sizeof(mods), ctypes.byref(need), LIST_MODULES_ALL):
        return 0, 0
    for i in range(min(need.value // ctypes.sizeof(wt.HMODULE), 2048)):
        name = ctypes.create_unicode_buffer(260)
        psapi.GetModuleBaseNameW(h, mods[i], name, 260)
        if name.value.lower() in EXE_NAMES:
            mi = MODULEINFO()
            if psapi.GetModuleInformation(h, mods[i], ctypes.byref(mi), ctypes.sizeof(mi)):
                return int(mi.lpBaseOfDll or 0), int(mi.SizeOfImage)
    return 0, 0


# --------------------------------------------------------------------------- #
# bellek
# --------------------------------------------------------------------------- #
def read_mem(h, addr, size):
    buf = ctypes.create_string_buffer(size)
    got = ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(got)):
        return None
    return buf.raw[:got.value]


def read_struct(pid, addr):
    """[vertical, lateral, roll] veya None."""
    try:
        h = open_proc(pid)
    except OSError:
        return None
    try:
        raw = read_mem(h, addr, 12)
    finally:
        k32.CloseHandle(h)
    if raw is None or len(raw) < 12:
        return None
    return [float(v) for v in np.frombuffer(raw, dtype=np.float32)]


def write_fields(pid, updates, addr):
    """[(alan, deger)] yaz, geri oku. Basarisizsa None."""
    try:
        h = open_proc(pid)
    except OSError:
        return None
    try:
        for name, val in updates:
            raw = np.array([val], dtype=np.float32).tobytes()
            got = ctypes.c_size_t(0)
            if not k32.WriteProcessMemory(h, ctypes.c_void_p(addr + FIELDS.index(name) * 4),
                                          ctypes.create_string_buffer(raw, 4), 4, ctypes.byref(got)):
                return None
        raw = read_mem(h, addr, 12)
    finally:
        k32.CloseHandle(h)
    if raw is None or len(raw) < 12:
        return None
    return [float(v) for v in np.frombuffer(raw, dtype=np.float32)]


def sane(vals):
    """Rotation offset'ler -180..180 derece araliginda olmali."""
    return all(-SPAN <= float(v) <= SPAN for v in vals)


# --------------------------------------------------------------------------- #
# adres bulma
# --------------------------------------------------------------------------- #
def config_path():
    root = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    return os.path.join(root, 'MSFS-MultiWindow-Fix', 'config.json')


def load_cache():
    try:
        with open(config_path(), encoding='utf-8') as f:
            raw = json.load(f)
        return {int(k): int(v) for k, v in raw.items()}
    except (OSError, ValueError, TypeError):
        return dict(DEFAULT_CACHE)


def save_cache(cache):
    try:
        os.makedirs(os.path.dirname(config_path()), exist_ok=True)
        with open(config_path(), 'w', encoding='utf-8') as f:
            json.dump({str(k): v for k, v in cache.items()}, f)
    except OSError:
        pass  # onbellek yazilamazsa her acilista yeniden tarariz


def scan_candidates(pid, base=None):
    """UserCfg.opt'taki pencere konumunu capa alip offset struct'ini arar.

    Oyun, WindowCustomN.PosX/PosY degerlerini bellekte tutuyor ve hemen
    ardindan (vertical, lateral, roll) uc float'i geliyor. Konum ciftini
    aramak, build'den bagimsiz ve neredeyse her zaman tek sonuc verir.
    """
    h = open_proc(pid)
    try:
        if base is None:
            base, size = module_info(h)
        else:
            base, size = base, module_info(h)[1]
        if not base:
            return []
        found = []   # (adres, uc float)
        for name, x, y, active, rot in read_windows():
            if x == 0 and y == 0:
                continue  # (0,0) her yerde var, ayirt edici degil
            needle = struct.pack('<ii', x, y)
            addr = base
            mbi = MBI()
            while addr < base + size:
                if k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                                      ctypes.sizeof(mbi)) == 0:
                    break
                b, s = int(mbi.BaseAddress or 0), int(mbi.RegionSize or 0)
                if s == 0:
                    break
                if (mbi.State == MEM_COMMIT and mbi.Type == IMAGE
                        and (mbi.Protect & 0xFF) in WRITABLE):
                    raw = read_mem(h, b, s)
                    if raw:
                        i = raw.find(needle)
                        while i != -1:
                            if i % 4 == 0:
                                hit = b + i
                                # konum ciftinden sonra kisa bir bosluk var;
                                # uc float genelde +12'de, sirasiyla dene
                                for off in (12, 8, 16):
                                    vals = read_struct(pid, hit + off)
                                    if plausible(vals):
                                        found.append((hit + off, vals))
                                        break
                            i = raw.find(needle, i + 1)
                addr = b + s
        if not found:
            # konum yok/sifir: UserCfg'deki aci degerlerini dogrudan ara
            for _n, _x, _y, _a, rot in read_windows():
                if rot:
                    found.extend((a, read_struct(pid, a))
                                 for a in scan_triple(h, base, size, rot))
                    break
        # UserCfg degeri eskiyebilir; eslesen varsa onu tercih et, yoksa hepsi
        rots = [rot for _n, _x, _y, _a, rot in read_windows() if rot]
        if rots:
            exact = [(a, v) for a, v in found if same(v, rots[0])]
            if exact:
                found = exact
        uniq = {}
        for a, v in found:
            uniq[a] = v
        return [(a, v[0], v[1], v[2]) for a, v in uniq.items()]
    finally:
        k32.CloseHandle(h)


def same(vals, rot, tol=0.01):
    return all(abs(v - r) <= tol for v, r in zip(vals, rot))


def plausible(vals):
    """Uc float gercekten rotation offset'e benziyor mu?

    Aci degerleri ya sifir ya da normal buyuklukte olur; denormal float'lar
    (or. 1.4e-45) rastgele bellek artigidir.
    """
    if not vals or not sane(vals) or all(v == 0 for v in vals):
        return False
    return all(v == 0 or abs(v) >= 0.001 for v in vals)


def scan_triple(h, base, size, rot):
    """Bellekte tam olarak (vertical, lateral, roll) uclusunu ara."""
    needle = np.array(rot, dtype=np.float32).tobytes()
    hits = []
    addr = base
    mbi = MBI()
    while addr < base + size:
        if k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                              ctypes.sizeof(mbi)) == 0:
            break
        b, s = int(mbi.BaseAddress or 0), int(mbi.RegionSize or 0)
        if s == 0:
            break
        if mbi.State == MEM_COMMIT and mbi.Type == IMAGE and (mbi.Protect & 0xFF) in WRITABLE:
            raw = read_mem(h, b, s)
            if raw:
                i = raw.find(needle)
                while i != -1:
                    if i % 4 == 0:
                        hits.append(b + i)
                    i = raw.find(needle, i + 1)
        addr = b + s
    return hits


def ucfg_paths():
    local = os.environ.get('LOCALAPPDATA', '')
    roam = os.environ.get('APPDATA', '')
    fixed = [
        os.path.join(local, 'Packages', 'Microsoft.Limitless_8wekyb3d8bbwe', 'LocalCache', 'UserCfg.opt'),
        os.path.join(local, 'Packages', 'Microsoft.FlightSimulator_8wekyb3d8bbwe', 'LocalCache', 'UserCfg.opt'),
        os.path.join(roam, 'Microsoft Flight Simulator 2024', 'UserCfg.opt'),
        os.path.join(roam, 'Microsoft Flight Simulator', 'UserCfg.opt'),
    ]
    found = [p for p in fixed if os.path.isfile(p)]
    if not found:
        pat = os.path.join(local, 'Packages', 'Microsoft.*', 'LocalCache', 'UserCfg.opt')
        found = glob.glob(pat)
    return found


def read_windows():
    """UserCfg.opt -> [(ad, PosX, PosY, aktif, [vertical, lateral, roll])]."""
    for path in ucfg_paths():
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                text = f.read()
        except OSError:
            continue
        wins = {}
        for m in re.finditer(r'^[ \t]*WindowCustom(\d+)\.(\w+)[ \t]+(.+?)[ \t]*$', text, re.M):
            wins.setdefault(m.group(1), {})[m.group(2)] = m.group(3)
        out = []
        for idx, d in wins.items():
            try:
                x, y = int(d.get('PosX', '')), int(d.get('PosY', ''))
            except ValueError:
                continue
            rot = None
            try:
                parts = [float(v) for v in d.get('CameraDegRotationAdd', '').split()]
                if len(parts) == 3:
                    rot = parts
            except ValueError:
                rot = None
            out.append((f'WindowCustom{idx}', x, y, d.get('WindowActive') == '1', rot))
        if out:
            return out
    return []


def adopt(pid, addr):
    """Secilen adresi bu build icin onbellege yaz."""
    h = open_proc(pid)
    try:
        base, size = module_info(h)
    finally:
        k32.CloseHandle(h)
    if not base:
        return None
    rva = addr - base
    cache = load_cache()
    cache[size] = rva
    save_cache(cache)
    return rva


def locate(pid, rescan=False):
    h = open_proc(pid)
    try:
        base, size = module_info(h)
    finally:
        k32.CloseHandle(h)
    if not base:
        return None, None, []
    cache = load_cache()
    if not rescan:
        rva = cache.get(size)
        if rva is not None:
            addr = base + rva
            vals = read_struct(pid, addr)
            if vals and sane(vals):
                return addr, rva, []
    cands = scan_candidates(pid)
    if len(cands) == 1:
        addr = cands[0][0]
        rva = addr - base
        cache[size] = rva
        save_cache(cache)
        return addr, rva, []
    return None, None, cands


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help', 'help'):
        print(__doc__ if __doc__ else '')
        print('komutlar: show | set <lateral|vertical|roll> <deger> ... | find')
        return
    pids = find_pids()
    if not pids:
        raise SystemExit('[!] Flight Simulator calismiyor.')
    pid = pids[0]
    if len(pids) > 1:
        print(f'[i] birden fazla surec, ilki kullaniliyor: {pids}')

    if args[0] == 'show':
        addr, rva, cands = locate(pid)
        if addr is None:
            print(f'[!] adres bulunamadi, {len(cands)} aday:')
            for a, v, l, r in cands[:20]:
                print(f'    0x{a:X}  vertical={v:g} lateral={l:g} roll={r:g}')
            return
        vals = read_struct(pid, addr)
        print(f'pid={pid}  base=0x{addr - rva:X}  rva=0x{rva:X}  addr=0x{addr:X}')
        for n, v in zip(FIELDS, vals):
            print(f'  {n:<9} {v:g}')

    elif args[0] == 'set':
        updates = parse_updates(args[1:])
        addr, _, cands = locate(pid)
        if addr is None:
            raise SystemExit(f'[!] adres bulunamadi ({len(cands)} aday)')
        back = write_fields(pid, updates, addr)
        if back is None:
            raise SystemExit('[!] yazilamadi (yonetici olarak calistir?)')
        print('[OK] ' + '  '.join(f'{n}={back[i]:g}' for i, n in enumerate(FIELDS)))

    elif args[0] == 'find':
        hits = scan_candidates(pid)
        h = open_proc(pid)
        try:
            base, _ = module_info(h)
        finally:
            k32.CloseHandle(h)
        for a, v, l, r in hits[:30]:
            print(f'  RVA 0x{a - base:X}   vertical={v:g} lateral={l:g} roll={r:g}')
        print(f'toplam {len(hits)} aday')

    else:
        print('bilinmeyen komut')


def parse_updates(args):
    if not args or len(args) % 2:
        raise SystemExit('kullanim: set <lateral|vertical|roll> <deger> [...]')
    out = []
    for i in range(0, len(args), 2):
        name = args[i].lower()
        if name not in FIELDS:
            raise SystemExit(f'[!] gecersiz alan: {name} ({", ".join(FIELDS)})')
        out.append((name, float(args[i + 1])))
    return out


def selftest():
    """Sim gerekmeden calisan kontroller: python msfs_mw.py selftest"""
    assert FIELDS == ('vertical', 'lateral', 'roll')          # bellek sirasi
    assert ROW_ORDER == ('lateral', 'vertical', 'roll')       # ekran sirasi
    assert FIELDS.index('roll') * 4 == 8                      # +8 roll
    assert parse_updates(['lateral', '92', 'roll', '-9']) == [('lateral', 92.0), ('roll', -9.0)]
    for bad in (['lateral'], ['bogus', '1'], ['lateral', 'x']):
        try:
            parse_updates(bad)
        except (SystemExit, ValueError):
            pass
        else:
            raise AssertionError(f'reddetmeliydi: {bad}')
    assert sane([-4.0, 90.0, 0.0]) and sane([0.0, 0.0, 9.0])
    assert not sane([0.0, -734288.0, 0.0])                    # rastgele bellek
    # plausible(): hakiki ucgen gecer, rastgele artefakt gecmez
    assert plausible([-4.0, 90.0, 0.0])
    assert plausible([0.0, 0.0, 9.0])
    assert not plausible([0.0, 0.0, 0.0])                     # hepsi sifir: ayirt edici degil
    assert not plausible([90.0, 0.0, 1.401298464324817e-45])  # denormal artik
    # ayni(): config degeri ile bellek degeri karsilastirmasi
    assert same([-4.0, 90.0, 0.0], [-4.0, 90.0, 0.0])
    assert not same([-4.0, 90.0, 0.0], [12.0, 90.0, 0.0])
    # konum cifti + 12 bayt = uc float (bu makinede dogrulanan duzen)
    blob = struct.pack('<ii', 2587, 309) + struct.pack('<f', 0.0) + \
        struct.pack('<3f', -4.0, 90.0, 0.0)
    assert first_offset(blob) == 12
    print('[OK] selftest gecti')


def first_offset(blob):
    """Yardimci: plausible ucgenin ilk bulundugu ofset; yoksa None."""
    for off in (12, 8, 16):
        if off + 12 <= len(blob):
            vals = [float(v) for v in np.frombuffer(blob[off:off + 12], dtype=np.float32)]
            if plausible(vals):
                return off
    return None


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    else:
        main()
