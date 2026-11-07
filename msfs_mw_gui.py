#!/usr/bin/env python3
# msfs_mw_gui.py — Flight Simulator 2024 Multi Window rotation offset editor.
# Cekirdek msfs_mw.py'de; bu dosya sadece arayuz.

import tkinter as tk
import i18n
import msfs_mw as core

BG, PANEL, FG, DIM = '#181a1d', '#22262b', '#e6e8eb', '#8b939c'
ACCENT, ERR, OK, FIELD = '#3b82f6', '#ef4444', '#22c55e', '#0e1013'


def _hex(c):
    return '#%02x%02x%02x' % c


def _mix(a, b, t):
    return _hex(tuple(int(x + (y - x) * t) for x, y in zip(a, b)))


class Slider(tk.Canvas):
    """Kalın, 3D görünümlü mavi slider. Oyun içi çubuklara benzer."""

    THUMB_W, THUMB_H = 24, 30

    def __init__(self, parent, lo, hi, on_change, height=40):
        super().__init__(parent, height=height, bg=PANEL, highlightthickness=0,
                         bd=0, cursor='hand2')
        self.lo, self.hi, self.on_change = lo, hi, on_change
        self.value = 0.0
        self._drag = False
        self.bind('<Configure>', lambda e: self._draw())
        self.bind('<Button-1>', self._press)
        self.bind('<B1-Motion>', self._drag_to)
        self.bind('<ButtonRelease-1>', self._release)

    # ---- geometri ----
    def _range(self):
        return self.THUMB_W / 2, max(self.winfo_width() - self.THUMB_W / 2, self.THUMB_W / 2 + 1)

    def _x_of(self, v):
        x0, x1 = self._range()
        t = (v - self.lo) / (self.hi - self.lo) if self.hi != self.lo else 0
        return x0 + (x1 - x0) * max(0.0, min(1.0, t))

    def _v_of(self, x):
        x0, x1 = self._range()
        t = max(0.0, min(1.0, (x - x0) / (x1 - x0)))
        return round(self.lo + (self.hi - self.lo) * t)

    # ---- cizim ----
    def _draw(self):
        self.delete('all')
        w, h = self.winfo_width(), self.winfo_height()
        if w < 20:
            return
        ty0, ty1 = h / 2 - 8, h / 2 + 8          # 16px kalin ray
        tx0, tx1 = 10, w - 10
        tx = self._x_of(self.value)

        # yuvaya gomulu ray: ust golge, alt isik
        self.create_rectangle(tx0, ty0, tx1, ty1, fill='#0a0c0f', width=0)
        self.create_line(tx0, ty0, tx1, ty0, fill='#05070a', width=2)
        self.create_line(tx0, ty1, tx1, ty1, fill='#33383f', width=1)

        # soluk taraf (degerin saginda kalan bos ray)
        self.create_rectangle(tx, ty0 + 2, tx1 - 1, ty1 - 1, fill='#15181c', width=0)

        # dolu kisim: yatay mavi gradyan + ust parlama
        steps = 48
        span = max(tx - tx0, 1)
        for i in range(steps):
            a = tx0 + span * i / steps
            b = tx0 + span * (i + 1) / steps + 1
            self.create_rectangle(a, ty0 + 1, b, ty1 - 1,
                                  fill=_mix((30, 64, 175), (96, 165, 250), i / (steps - 1)),
                                  width=0)
        self.create_line(tx0 + 1, ty0 + 2, tx - 1, ty0 + 2, fill='#93c5fd', width=1)
        self.create_line(tx0 + 1, ty1 - 2, tx - 1, ty1 - 2, fill='#1e3a8a', width=1)

        # thumb: dikey gradyanli, kabartma kenarli
        hw, hh = self.THUMB_W / 2, self.THUMB_H / 2
        cy = h / 2
        px0, px1 = tx - hw, tx + hw
        py0, py1 = cy - hh, cy + hh
        for i in range(self.THUMB_H):
            y = py0 + i
            t = i / (self.THUMB_H - 1)
            col = _mix((147, 197, 253), (37, 99, 235), t)
            self.create_line(px0 + 1, y, px1 - 1, y, fill=col, width=1)
        self.create_rectangle(px0, py0, px1, py1, outline='#1e40af', width=1)
        self.create_line(px0 + 2, py0 + 1, px1 - 2, py0 + 1, fill='#dbeafe', width=1)
        self.create_line(px0 + 2, py1 - 1, px1 - 2, py1 - 1, fill='#1e3a8a', width=1)

    # ---- etkilesim ----
    def _press(self, ev):
        self._drag = True
        self._drag_to(ev)

    def _drag_to(self, ev):
        v = self._v_of(ev.x)
        if v != self.value:
            self.value = v
            self._draw()
            self.on_change(v)

    def _release(self, ev):
        self._drag = False

    def set_value(self, v):
        self.value = float(v)
        self._draw()


class App:
    def __init__(self, root):
        self.root = root
        self.pid = None
        self.addr = None
        self.pending = {}
        self.flush_job = None
        self.writing = False
        self.locale = 'en-US'   # arayuz Ingilizce acilir; kullanici secerse degisir
        self.rows = {}          # alan -> (etiket, deger etiketi, scale, entry)
        self.retry_job = None

        root.title('MSFS Multi Window Rotation Fix')
        root.configure(bg=BG)
        root.geometry('780x430')
        root.minsize(660, 400)

        self.build()
        self.root.after(80, self.connect)
        self.root.after(1000, self.tick)

    # ---------------- metin ----------------
    @property
    def t(self):
        return i18n.strings(self.locale)

    def relabel(self):
        t = self.t
        self.subtitle.config(text=t['hint'])
        self.btn_reconnect.config(text=t['reconnect'])
        self.btn_detect.config(text=t['detect'])
        self.lang_label.config(text=t['language'])
        for name, label in i18n.ordered_axes(self.locale):
            self.rows[name][0].config(text=label)
        self.refresh_status()

    def refresh_status(self):
        t = self.t
        if self.pid:
            self.status.config(text=f"{t['connected']} · pid {self.pid} · 0x{self.addr:X}", fg=OK)
        elif self._status_key:
            self.status.config(text=t[self._status_key], fg=ERR)
        else:
            self.status.config(text=t['connecting'], fg=DIM)

    # ---------------- arayuz ----------------
    def build(self):
        head = tk.Frame(self.root, bg=BG)
        head.pack(fill='x', padx=22, pady=(16, 4))
        tk.Label(head, text='Multi Window Rotation Fix', bg=BG, fg=FG,
                 font=('Segoe UI Semibold', 16)).pack(side='left')
        self.status = tk.Label(head, text='', bg=BG, fg=DIM, font=('Segoe UI', 9))
        self.status.pack(side='right')

        self.subtitle = tk.Label(self.root, text='', bg=BG, fg=DIM, justify='left',
                                 wraplength=720, font=('Segoe UI', 9))
        self.subtitle.pack(anchor='w', padx=24, pady=(0, 10))

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill='both', expand=True, padx=16)

        for name in core.ROW_ORDER:
            row = tk.Frame(body, bg=PANEL)
            row.pack(fill='x', pady=3)
            top = tk.Frame(row, bg=PANEL)
            top.pack(fill='x', padx=14, pady=(8, 0))
            label = tk.Label(top, text='', bg=PANEL, fg=FG, font=('Segoe UI', 10))
            label.pack(side='left')
            value = tk.Label(top, text='—', bg=PANEL, fg=ACCENT, width=6, anchor='e',
                             font=('Consolas', 11, 'bold'))
            value.pack(side='right')

            line = tk.Frame(row, bg=PANEL)
            line.pack(fill='x', padx=14, pady=(4, 10))
            scale = Slider(line, -core.SPAN, core.SPAN,
                           on_change=lambda v, n=name: self.on_slide(n, v))
            scale.pack(side='left', fill='x', expand=True)
            entry = tk.Entry(line, bg=FIELD, fg=FG, insertbackground=FG, relief='flat',
                             justify='center', width=6, font=('Consolas', 10),
                             highlightthickness=1, highlightbackground='#2f353c',
                             highlightcolor=ACCENT)
            entry.pack(side='right', padx=(10, 0))
            entry.bind('<Return>', lambda e, n=name: self.on_entry(n))
            entry.bind('<FocusOut>', lambda e, n=name: self.on_entry(n))
            self.rows[name] = (label, value, scale, entry)

        foot = tk.Frame(self.root, bg=BG)
        foot.pack(fill='x', padx=22, pady=12)

        self.hint = tk.Label(foot, text='', bg=BG, fg=DIM, font=('Segoe UI', 9))
        self.hint.pack(side='left')

        self.btn_reconnect = self.mk_button(foot, '', self.connect)
        self.btn_reconnect.pack(side='right')
        self.btn_detect = self.mk_button(foot, '', self.on_detect)
        self.btn_detect.pack(side='right', padx=(0, 6))

        self.lang_var = tk.StringVar(value=i18n.NATIVE.get(self.locale, 'English'))
        langs = [i18n.NATIVE[k] for k in i18n.NATIVE]
        self.lang_menu = tk.OptionMenu(foot, self.lang_var, *langs, command=self.on_lang)
        self.lang_menu.config(bg=PANEL, fg=FG, activebackground='#2f353c', activeforeground=FG,
                              bd=0, highlightthickness=0, font=('Segoe UI', 9), width=14)
        self.lang_menu['menu'].config(bg=PANEL, fg=FG, activebackground=ACCENT,
                                      activeforeground='#fff', bd=0)
        self.lang_menu.pack(side='left', padx=(0, 10))
        self.lang_label = tk.Label(foot, text='', bg=BG, fg=DIM, font=('Segoe UI', 9))
        self.lang_label.pack(side='left')

        self._status_key = None
        self.relabel()

    def mk_button(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=PANEL, fg=FG, bd=0,
                         activebackground='#2f353c', activeforeground=FG,
                         padx=12, pady=4, font=('Segoe UI', 9), cursor='hand2')

    def on_lang(self, native):
        for code, name in i18n.NATIVE.items():
            if name == native:
                self.locale = code
                break
        self.relabel()

    # ---------------- baglanti ----------------
    def connect(self):
        pids = core.find_pids()
        if not pids:
            self.pid = self.addr = None
            self._status_key = 'not_running'
            self.refresh_status()
            self.schedule_retry()
            return
        pid = pids[0]
        try:
            addr, rva, cands = core.locate(pid)
        except OSError:
            self.pid = self.addr = None
            self._status_key = 'admin'
            self.refresh_status()
            self.schedule_retry()
            return
        if addr is None:
            self.pid = self.addr = None
            if len(cands) > 1:
                self._status_key = 'ambiguous'
                self.refresh_status()
                self.pick_candidate(pid, cands)
            else:
                self._status_key = 'bad_rva'
                self.refresh_status()
                self.schedule_retry()
            return
        self.pid, self.addr = pid, addr
        self._status_key = None
        self.refresh_status()
        vals = core.read_struct(pid, addr)
        if vals and core.sane(vals):
            self.render(vals)

    def schedule_retry(self):
        if self.retry_job:
            self.root.after_cancel(self.retry_job)
        self.retry_job = self.root.after(2500, self.connect)

    # ---------------- deger ----------------
    def render(self, vals):
        for i, name in enumerate(core.FIELDS):
            v = vals[i]
            label, value, scale, entry = self.rows[name]
            value.config(text=f'{v:g}')
            if self.root.focus_get() is not entry:
                entry.delete(0, 'end')
                entry.insert(0, f'{v:g}')
            scale.set_value(round(v))

    def on_slide(self, name, v):
        if self.writing:
            return
        val = float(round(float(v)))   # offset'ler tam derece
        _, value, scale, entry = self.rows[name]
        if value.cget('text') == f'{val:g}':
            return
        value.config(text=f'{val:g}')
        entry.delete(0, 'end')
        entry.insert(0, f'{val:g}')
        self.queue(name, val)

    def on_entry(self, name):
        txt = self.rows[name][3].get().strip().replace(',', '.')
        try:
            val = float(txt)
        except ValueError:
            self.hint.config(text=f'! {txt}', fg=ERR)
            return
        val = max(-core.SPAN, min(core.SPAN, val))
        self.rows[name][1].config(text=f'{val:g}')
        self.rows[name][2].set_value(val)
        self.queue(name, val)

    def queue(self, name, val):
        self.pending[name] = val
        if self.flush_job:
            self.root.after_cancel(self.flush_job)
        self.flush_job = self.root.after(120, self.flush)

    def flush(self):
        self.flush_job = None
        if not self.pending:
            return
        updates, self.pending = list(self.pending.items()), {}
        if not self.pid:
            return
        self.writing = True
        try:
            back = core.write_fields(self.pid, updates, self.addr)
        finally:
            self.writing = False
        if back is None:
            self.pid = None
            self._status_key = 'admin'
            self.refresh_status()
            return
        for name, want in updates:
            if abs(back[core.FIELDS.index(name)] - want) > 1e-3:
                self.hint.config(text=self.t['reverted'], fg=ERR)
                break
        else:
            self.hint.config(text='', fg=DIM)
        self.render(back)

    def tick(self):
        if self.pid and not self.pending and not self.writing:
            vals = core.read_struct(self.pid, self.addr)
            if vals is None or not core.sane(vals):
                self.pid = None
                self._status_key = 'not_running'
                self.refresh_status()
                self.schedule_retry()
            else:
                self.render(vals)
        self.root.after(1200, self.tick)

    # ---------------- yeniden bulma ----------------
    def on_detect(self):
        if self.pid:
            try:
                addr, rva, cands = core.locate(self.pid, rescan=True)
            except OSError:
                self.hint.config(text=self.t['admin'], fg=ERR)
                return
            if addr is not None:
                self.addr = addr
                self.refresh_status()
                self.hint.config(text=f"{self.t['detected']}: RVA 0x{rva:X}", fg=OK)
                return
            if cands:
                self.pick_candidate(self.pid, cands)
                return
        self.connect()
        if not self.pid:
            self.hint.config(text=self.t['not_running'], fg=ERR)

    def pick_candidate(self, pid, cands):
        t = self.t
        win = tk.Toplevel(self.root, bg=BG)
        win.title(t['pick_title'])
        win.configure(bg=BG)
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text=t['pick_hint'], bg=BG, fg=DIM, font=('Segoe UI', 9),
                 wraplength=460, justify='left').pack(anchor='w', padx=16, pady=(14, 8))
        box = tk.Listbox(win, bg=FIELD, fg=FG, bd=0, highlightthickness=0,
                         font=('Consolas', 10), height=min(len(cands), 10),
                         selectbackground=ACCENT, selectforeground='#fff')
        box.pack(fill='both', expand=True, padx=16)
        for a, ver, lat, roll in cands:
            box.insert('end', f'0x{a:X}   lat={lat:g}  ver={ver:g}  roll={roll:g}')
        box.selection_set(0)

        def choose():
            sel = box.curselection()
            if not sel:
                return
            rva = core.adopt(pid, cands[sel[0]][0])
            win.destroy()
            self.pid, self.addr = pid, cands[sel[0]][0]
            self.refresh_status()
            self.hint.config(text=f"{self.t['detected']}: RVA 0x{rva:X}", fg=OK)
            vals = core.read_struct(pid, self.addr)
            if vals and core.sane(vals):
                self.render(vals)

        btns = tk.Frame(win, bg=BG)
        btns.pack(fill='x', padx=16, pady=12)
        tk.Button(btns, text=t['ok'], command=choose, bg=ACCENT, fg='#fff', bd=0,
                  padx=16, pady=4, font=('Segoe UI', 9), cursor='hand2').pack(side='right')
        tk.Button(btns, text=t['cancel'], command=win.destroy, bg=PANEL, fg=FG, bd=0,
                  padx=16, pady=4, font=('Segoe UI', 9), cursor='hand2').pack(side='right', padx=(0, 6))
        box.bind('<Double-Button-1>', lambda e: choose())


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
