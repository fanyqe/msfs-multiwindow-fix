# MSFS Multi Window Rotation Fix

Fixes the **Multi Window rotation offsets** (lateral / vertical / roll) that get
locked or greyed out in Microsoft Flight Simulator 2024 after **Sim Update 6**
(build 1.8.14.0).

> **Status:** workaround, not a mod. Nothing is patched on disk — the values are
> written straight into the running sim, exactly where its own UI reads them
> from. The sim updates the view immediately, and the value survives until you
> close the sim.

---

## The problem

Since Sim Update 6, `Advanced Options → Multi Window` stops accepting input for
the rotation offsets of an existing render window. A window may allow one or two
of the five fields to be edited before locking again, and deleting/recreating the
window brings back the same values. This makes a fresh multi-monitor setup almost
impossible.

Tracked upstream:

- [Multi Window settings partially locked / unresponsive after Sim Update 6](https://forums.flightsimulator.com/t/multi-window-settings-partially-locked-unresponsive-after-sim-update-6-1-8-14-0/774020)

## How it works

The three offsets live next to each other as 32-bit floats inside the writable
data section of `FlightSimulator2024.exe`. The sim reads them every frame, so
writing there updates the render window immediately — the same thing the slider
would have done before it broke.

The address moves between builds, so nothing is hardcoded:

1. The tool reads `UserCfg.opt` (the sim's own config file) and takes the
   `WindowCustomN.PosX / PosY` pair of a configured render window.
2. That pair sits in memory right before the offset block. It is searched in the
   module's writable sections.
3. The three floats found there are cross-checked against
   `WindowCustomN.CameraDegRotationAdd` from the same config file, so a wrong
   match is rejected instead of writing into random memory.
4. The resulting module offset is cached per build (`SizeOfImage`), so later
   launches skip the scan.

If the config has no usable window (or `PosX/PosY` are `0 0`), the tool falls
back to searching for the exact `CameraDegRotationAdd` triple.

## Requirements

- Windows 10/11, 64-bit
- Microsoft Flight Simulator 2024 running (MS Store or Steam build)
- Administrator rights (reading another process's memory requires it)
- For the Python version: Python 3.10+ and `numpy`

## Usage — prebuilt

1. Start the sim and get to the main menu (a flight is not required).
2. Run `MSFS-MultiWindowFix.exe` and accept the UAC prompt.
3. Drag a slider, or type a value and press Enter.

The header shows `connected · pid … · 0x…` once the offsets were located. If it
says `sim not running`, start the sim and press **Reconnect**.

## Usage — from source

```bash
pip install numpy
python msfs_mw_gui.py
```

Command line, if you prefer:

```bash
python msfs_mw.py show
python msfs_mw.py set lateral 92 vertical -7 roll 9
```

## Languages

The UI ships in 15 languages and starts in English. The axis labels are taken
from the sim's own localization packages (`Packages/fs-base/<locale>.locPak`,
keys `MENU.OPTIONS.MULTIWINDOW.DELTA_*`), so they match what you see in the sim.

English · Türkçe · Deutsch · Español · Français · Italiano · Polski · Português (BR) ·
Русский · Svenska · Norsk · Suomi · 日本語 · 한국어 · 中文（简体）

Locales the sim ships without a translation for (e.g. `cs-CZ`, `nl-NL`, `zh-TW`)
fall back to the English labels, because the sim shows English there too.

## Notes and limits

- **Nothing is written to disk.** `UserCfg.opt` is only read. The values reset
  when the sim closes, so set them again after a restart.
- **Per-build offset.** After a sim update the tool rescans once and caches the
  new offset automatically. If it ever reports `several candidates`, pick the row
  whose numbers match the ones in the sim.
- **Only the current position is fixed.** The underlying lock in the settings UI
  is a sim bug; this tool bypasses the UI instead of repairing it.
- Tested with MSFS 2024 **1.9.24.0**. MSFS 2020 is detected by name but untested —
  the `UserCfg.opt` layout may differ.
- The value written is the raw float the sim uses. Fractions are supported
  through the text box; the sliders snap to whole degrees.

## Safety

The tool only touches 12 bytes at a location it has verified against your own
config file. It never patches files, never injects code, and needs no network
access. Source is short enough to read in one sitting — please do.

## License

MIT — see [LICENSE](LICENSE).

Not affiliated with Microsoft or Asobo Studio. Microsoft Flight Simulator is a
trademark of Microsoft Corporation.
