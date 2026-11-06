#!/usr/bin/env python3
"""Generate the Flatcap 2.0 files for WezTerm.

    python3 scripts/build.py              # write the generated files and the README/docs blocks
    python3 scripts/build.py --check      # fail if a generated file is stale or a contrast target is missed
    python3 scripts/build.py --sync       # refresh src/theme.json from ../00-Flatcap, then rebuild
    python3 scripts/build.py --contrast   # print the contrast report (checks, ANSI x background, ANSI x ANSI)
    python3 scripts/build.py --lua        # also syntax-check the Lua files (needs luac or lua on PATH)

Input  : src/theme.json, a versioned copy of the Flatcap 2.0 core (the only source of values).
Outputs: colors/Flatcap Slate.toml      WezTerm color scheme files ([colors] + [metadata])
         colors/Flatcap Daylight.toml
         plugin/init.lua                WezTerm plugin: schemes, window_frame, command palette, char select
         README.md                      only the blocks between <!-- build:NAME --> markers
         docs/mapping.md                same markers: role tables, ANSI table, contrast tables

No hex value is written by hand in this file: every color is resolved from a Flatcap role.
Python 3.10+, standard library only. Output is deterministic.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import re
import shutil
import subprocess
import sys

try:  # Python 3.11+; on 3.10 the TOML re-parse check is skipped
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "src" / "theme.json"
README = ROOT / "README.md"
MAPPING_DOC = ROOT / "docs" / "mapping.md"
PLUGIN = ROOT / "plugin" / "init.lua"
EXAMPLE = ROOT / "examples" / "wezterm.lua"
UPSTREAM = (ROOT / ".." / "00-Flatcap" / "src" / "theme.json").resolve()

MODES = ("slate", "daylight")
SCHEME_NAME = {"slate": "Flatcap Slate", "daylight": "Flatcap Daylight"}
AUTHOR = "Cheycron Blaine"
ORIGIN_URL = "https://github.com/cheycron/flatcap-wezterm"
FONT_CODE = "Cascadia Code"
FONT_UI = "IBM Plex Sans"

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

# ---------------------------------------------------------------------------
# Mapping tables. Roles only; hex values come from src/theme.json.
# ---------------------------------------------------------------------------

# (WezTerm key under [colors], role, intent)
COLORS = [
    ("foreground", "text.primary", "Content text."),
    ("background", "bg.canvas", "Main area."),
    ("cursor_bg", "accent.fill",
     "Text cursor fill (block). Not focus.ring: focus is independent of the text cursor."),
    ("cursor_fg", "accent.on", "Character under a block cursor. The accent.fill / accent.on pair keeps it readable."),
    ("cursor_border", "accent.fill", "Bar and underline cursors, and the outline of an unfocused block."),
    ("selection_fg", "selection.fg", "Selected text. WezTerm supports the full pair, unlike Windows Terminal."),
    ("selection_bg", "selection.bg", "Text selection."),
    ("scrollbar_thumb", "border.control", "Scrollbar thumb: a functional mark, so the control outline role."),
    ("split", "border.control", "Pane divider: functional (it is also the resize handle), so the control outline role."),
    ("compose_cursor", "warning.fg", "Cursor while an IME, dead key or leader key holds input pending."),
    ("visual_bell", "info.bg", "Background flash for the visual bell: feedback, quiet."),
]

# Keys of [colors] whose value is a color spec table: { Color = "#rrggbb" }.
SPEC_COLORS = [
    ("copy_mode_active_highlight_bg", "accent.fill", "Current search match / mouse-extended selection in copy mode."),
    ("copy_mode_active_highlight_fg", "accent.on", ""),
    ("copy_mode_inactive_highlight_bg", "bg.selected", "Other search matches in copy mode."),
    ("copy_mode_inactive_highlight_fg", "text.primary", ""),
    ("quick_select_label_bg", "accent.fill", "Hint label of Quick Select."),
    ("quick_select_label_fg", "accent.on", ""),
    ("quick_select_match_bg", "selection.bg", "Matched text of Quick Select."),
    ("quick_select_match_fg", "selection.fg", ""),
]

# (key, ANSI index, Slate role, Daylight role, intent). Same decisions as Flatcap for Windows Terminal.
# Rule 1: the six hues keep their meaning (red=danger, green=success, yellow=warning,
#         blue=interaction/info, purple=number/literal, cyan=function) and never cycle data.*.
# Rule 2: the core has no "bright" tier. Where a role with the same hue and a stronger step exists
#         it is used (blue); otherwise bright repeats the normal role instead of inventing a value.
# Rule 3: black (0) and brightWhite (15) follow luminance, not role identity: they stay dark and
#         light in both modes because programs use them as block backgrounds.
# Rule 4: white (7) is readable ink in both modes (text.secondary): TUIs use it as ordinary text.
ANSI = [
    ("black", 0, "border.subtle", "text.primary",
     "Dark neutral. Slate: lifted just enough to stay visible as a block on the canvas; Daylight: ink."),
    ("red", 1, "danger.fg", "danger.fg", "Errors, deletions."),
    ("green", 2, "success.fg", "success.fg", "Success, additions."),
    ("yellow", 3, "warning.fg", "warning.fg", "Warnings."),
    ("blue", 4, "accent.fg", "accent.fg", "Directories, links, information."),
    ("purple", 5, "syntax.number", "syntax.number", "ANSI magenta: numbers, literals."),
    ("cyan", 6, "syntax.function", "syntax.function", "Functions, secondary identifiers."),
    ("white", 7, "text.secondary", "text.secondary", "Common TUI text. Readable ink in both modes."),
    ("brightBlack", 8, "text.muted", "text.muted", "Dimmed text: autosuggestions, comments, metadata."),
    ("brightRed", 9, "danger.fg", "danger.fg", "No stronger red in the core: repeats red."),
    ("brightGreen", 10, "success.fg", "success.fg", "No stronger green in the core: repeats green."),
    ("brightYellow", 11, "warning.fg", "warning.fg", "No stronger yellow in the core: repeats yellow."),
    ("brightBlue", 12, "accent.hover", "accent.hover", "Stronger step of the accent ramp."),
    ("brightPurple", 13, "syntax.number", "syntax.number", "No stronger purple in the core: repeats purple."),
    ("brightCyan", 14, "syntax.function", "syntax.function", "No stronger cyan in the core: repeats cyan."),
    ("brightWhite", 15, "text.primary", "bg.raised", "Emphasized light neutral."),
]
ANSI_KEYS = [a[0] for a in ANSI]
HUES = ("red", "green", "yellow", "blue", "purple", "cyan")
HUE_KEYS = [k for h in HUES for k in (h, "bright" + h[0].upper() + h[1:])]
NEUTRAL_BLOCKS = ("black", "brightWhite")  # used as backgrounds, not for reading on the canvas

# Fancy tab bar. (group, key, role, intent). Tab text pairs are checked below.
TAB_BAR = [
    ("", "background", "bg.surface", "Retro tab bar strip. The fancy tab bar takes window_frame.*_titlebar_bg instead."),
    ("", "inactive_tab_edge", "border.subtle", "Divider between inactive tabs (decorative)."),
    ("active_tab", "bg_color", "bg.selected", "Current tab: the selected-state fill (the fancy tab bar cannot add a second indicator)."),
    ("active_tab", "fg_color", "text.primary", ""),
    ("inactive_tab", "bg_color", "bg.surface", "Inactive tabs sit on the tab bar."),
    ("inactive_tab", "fg_color", "text.secondary", ""),
    ("inactive_tab_hover", "bg_color", "bg.hover", "Neutral hover."),
    ("inactive_tab_hover", "fg_color", "text.primary", ""),
    ("new_tab", "bg_color", "bg.surface", ""),
    ("new_tab", "fg_color", "text.secondary", ""),
    ("new_tab_hover", "bg_color", "bg.hover", ""),
    ("new_tab_hover", "fg_color", "text.primary", ""),
]
# Non-color indicator for the current tab (Flatcap: selected/current needs more than fill).
ACTIVE_TAB_EXTRA = {"intensity": "Bold"}

# window_frame: what a color scheme cannot carry; set by the plugin. Used by the fancy tab bar.
WINDOW_FRAME = [
    ("active_titlebar_bg", "bg.surface", "Tab bar / title bar, focused. Navigation chrome."),
    ("inactive_titlebar_bg", "bg.surface", "Unchanged when the window loses focus."),
    ("active_titlebar_fg", "text.primary", ""),
    ("inactive_titlebar_fg", "text.secondary", ""),
    ("active_titlebar_border_bottom", "border.subtle", "Separator between the tab bar and the terminal."),
    ("inactive_titlebar_border_bottom", "border.subtle", ""),
    ("button_fg", "text.secondary", "Window buttons and the new-tab button glyph."),
    ("button_bg", "bg.surface", ""),
    ("button_hover_fg", "text.primary", ""),
    ("button_hover_bg", "bg.hover", ""),
]

# Top-level config keys set by the plugin besides window_frame.
UI_KEYS = [
    ("command_palette_bg_color", "bg.raised", "Command palette floats over the terminal."),
    ("command_palette_fg_color", "text.primary", ""),
    ("char_select_bg_color", "bg.raised", "Character selector floats over the terminal."),
    ("char_select_fg_color", "text.primary", ""),
]

# Default inactive_pane_hsb of WezTerm (documented defaults). Not set by Flatcap; used for an estimate only.
INACTIVE_HSB = (1.0, 0.9, 0.8)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
def load() -> dict:
    return json.loads(THEME.read_text(encoding="utf-8"))


def role(theme: dict, mode: str, name: str) -> str:
    return theme["themes"][mode][name]


def ansi_role(mode: str, key: str) -> str:
    for k, _i, s, d, _n in ANSI:
        if k == key:
            return s if mode == "slate" else d
    raise KeyError(key)


def ansi_lists(theme: dict, mode: str) -> tuple[list[str], list[str]]:
    vals = [role(theme, mode, ansi_role(mode, k)) for k in ANSI_KEYS]
    return vals[:8], vals[8:]


def scheme_colors(theme: dict, mode: str) -> dict:
    """The [colors] table, in output order. Nested dicts become sub-tables / Lua tables."""
    r = lambda name: role(theme, mode, name)  # noqa: E731
    out: dict = {}
    for key, name, _ in COLORS:
        out[key] = r(name)
    ansi, brights = ansi_lists(theme, mode)
    out["ansi"] = ansi
    out["brights"] = brights
    for key, name, _ in SPEC_COLORS:
        out[key] = {"Color": r(name)}
    tab: dict = {}
    for group, key, name, _ in TAB_BAR:
        if group:
            tab.setdefault(group, {})[key] = r(name)
            if group == "active_tab" and key == "fg_color":
                tab[group].update(ACTIVE_TAB_EXTRA)
        else:
            tab[key] = r(name)
    out["tab_bar"] = tab
    return out


def window_frame(theme: dict, mode: str) -> dict:
    return {key: role(theme, mode, name) for key, name, _ in WINDOW_FRAME}


def ui_keys(theme: dict, mode: str) -> dict:
    return {key: role(theme, mode, name) for key, name, _ in UI_KEYS}


def families(stack: str) -> list[str]:
    return re.findall(r'"([^"]+)"', stack)


def rem_to_px(value: str) -> float:
    assert value.endswith("rem"), value
    return float(value[:-3]) * 16


def fmt_num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def fonts(theme: dict) -> dict:
    code = families(theme["typography"]["font.code"])
    literal = families(theme["typography"]["font.literal"])
    ui = families(theme["typography"]["font.ui"])
    px = rem_to_px(theme["typography"]["font.size.code"])
    return {"code": code[0], "code_nf": code[1], "mono": literal[0], "mono_nf": literal[1], "ui": ui[0],
            "size_px": px, "size_pt_96": px * 0.75}


# ---------------------------------------------------------------------------
# Flat lookup for contrast checks
# ---------------------------------------------------------------------------
def flat(theme: dict, mode: str) -> dict[str, str]:
    c = scheme_colors(theme, mode)
    v: dict[str, str] = {}
    for key, name, _ in COLORS:
        v[key] = c[key]
    for key, name, _ in SPEC_COLORS:
        v[key] = c[key]["Color"]
    for k, val in zip(ANSI_KEYS, c["ansi"] + c["brights"]):
        v["ansi." + k] = val
    for group, key, name, _ in TAB_BAR:
        v["tab_bar." + (group + "." if group else "") + key] = role(theme, mode, name)
    for key, val in window_frame(theme, mode).items():
        v["window_frame." + key] = val
    v.update(ui_keys(theme, mode))
    return v


# ---------------------------------------------------------------------------
# Contrast
# ---------------------------------------------------------------------------
def _lum(h: str) -> float:
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def hsb(h: str, hue: float, sat: float, val: float) -> str:
    """Approximation of inactive_pane_hsb: multiply the HSV components as the WezTerm docs describe."""
    r, g, b = (int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    hh = (hh * hue) % 1.0
    ss, vv = min(ss * sat, 1.0), min(vv * val, 1.0)
    r, g, b = colorsys.hsv_to_rgb(hh, ss, vv)
    return "#%02X%02X%02X" % tuple(round(x * 255) for x in (r, g, b))


# (label, foreground key, background key, target). Keys come from flat().
CHECKS: list[tuple[str, str, str, float]] = [
    ("`foreground` on `background`", "foreground", "background", 7),
    ("`cursor_fg` on `cursor_bg`", "cursor_fg", "cursor_bg", 4.5),
    ("`cursor_bg` on `background`", "cursor_bg", "background", 3),
    ("`cursor_border` on `background`", "cursor_border", "background", 3),
    ("`selection_fg` on `selection_bg`", "selection_fg", "selection_bg", 4.5),
    ("`scrollbar_thumb` on `background`", "scrollbar_thumb", "background", 3),
    ("`split` on `background`", "split", "background", 3),
    ("`compose_cursor` on `background`", "compose_cursor", "background", 3),
    ("`copy_mode_active_highlight_fg` on `_bg`", "copy_mode_active_highlight_fg", "copy_mode_active_highlight_bg", 4.5),
    ("`copy_mode_inactive_highlight_fg` on `_bg`", "copy_mode_inactive_highlight_fg", "copy_mode_inactive_highlight_bg", 4.5),
    ("`quick_select_label_fg` on `_bg`", "quick_select_label_fg", "quick_select_label_bg", 4.5),
    ("`quick_select_match_fg` on `_bg`", "quick_select_match_fg", "quick_select_match_bg", 4.5),
    ("Active tab text", "tab_bar.active_tab.fg_color", "tab_bar.active_tab.bg_color", 7),
    ("Inactive tab text", "tab_bar.inactive_tab.fg_color", "tab_bar.inactive_tab.bg_color", 5),
    ("Inactive tab text, hover", "tab_bar.inactive_tab_hover.fg_color", "tab_bar.inactive_tab_hover.bg_color", 7),
    ("New-tab button", "tab_bar.new_tab.fg_color", "tab_bar.new_tab.bg_color", 5),
    ("New-tab button, hover", "tab_bar.new_tab_hover.fg_color", "tab_bar.new_tab_hover.bg_color", 7),
    ("Title bar text, active", "window_frame.active_titlebar_fg", "window_frame.active_titlebar_bg", 7),
    ("Title bar text, inactive", "window_frame.inactive_titlebar_fg", "window_frame.inactive_titlebar_bg", 5),
    ("Window buttons", "window_frame.button_fg", "window_frame.button_bg", 5),
    ("Window buttons, hover", "window_frame.button_hover_fg", "window_frame.button_hover_bg", 7),
    ("Command palette text", "command_palette_fg_color", "command_palette_bg_color", 7),
    ("Character selector text", "char_select_fg_color", "char_select_bg_color", 7),
]
# Every ANSI color as text on `background`.
ANSI_TARGETS = {**{k: 5.0 for k in ANSI_KEYS if k not in NEUTRAL_BLOCKS}}
# Slate's black is a block color by design; Slate's brightWhite and Daylight's black are ink and are checked too.
EXTRA_NEUTRAL_CHECKS = {"slate": ("brightWhite",), "daylight": ("black",)}


def evaluate(theme: dict) -> dict:
    """Return per-mode results: rows of (label, ratio, target) and a list of failures."""
    out = {}
    for mode in MODES:
        v = flat(theme, mode)
        rows = [(label, ratio(v[f], v[b]), tgt) for label, f, b, tgt in CHECKS]
        for k in ANSI_KEYS:
            tgt = ANSI_TARGETS.get(k, 5.0 if k in EXTRA_NEUTRAL_CHECKS[mode] else None)
            if tgt:
                rows.append((f"ANSI `{k}` on `background`", ratio(v["ansi." + k], v["background"]), tgt))
        out[mode] = {"values": v, "rows": rows, "fails": [r for r in rows if r[1] < r[2]]}
    return out


def info(theme: dict) -> dict:
    """Informational numbers (no target)."""
    d = {}
    for mode in MODES:
        v = flat(theme, mode)
        ia = hsb(v["foreground"], *INACTIVE_HSB)
        ib = hsb(v["background"], *INACTIVE_HSB)
        d[mode] = {
            "selection_bg_vs_bg": ratio(v["selection_bg"], v["background"]),
            "active_tab_vs_bar": ratio(v["tab_bar.active_tab.bg_color"], v["window_frame.active_titlebar_bg"]),
            "palette_vs_bg": ratio(v["command_palette_bg_color"], v["background"]),
            "bell_vs_bg": ratio(v["visual_bell"], v["background"]),
            "inactive_pane": ratio(ia, ib),
            "inactive_fg": ia, "inactive_bg": ib,
            "cross": {f: {b: ratio(v["ansi." + f], v["ansi." + b]) for b in ANSI_KEYS} for f in ANSI_KEYS},
            "fg_on_ansi": {h: ratio(v["foreground"], v["ansi." + h]) for h in HUES},
        }
    return d


def contrast_report(theme: dict) -> str:
    ev, inf = evaluate(theme), info(theme)
    L: list[str] = []
    for mode in MODES:
        v = ev[mode]["values"]
        L.append(f"[{SCHEME_NAME[mode]}]  background {v['background']}  selection {v['selection_bg']}")
        L.append(f"  {'check':<48}{'ratio':>8}{'target':>8}")
        for label, r, t in ev[mode]["rows"]:
            L.append(f"  {label.replace('`', ''):<48}{r:8.2f}{t:8g}  {'FAIL' if r < t else ''}")
        d = inf[mode]
        L.append(f"  info: selection_bg vs background {d['selection_bg_vs_bg']:.2f}; active tab vs tab bar "
                 f"{d['active_tab_vs_bar']:.2f}; palette vs background {d['palette_vs_bg']:.2f}; "
                 f"visual_bell vs background {d['bell_vs_bg']:.2f}; default inactive pane text {d['inactive_pane']:.2f}")
        L.append("  Cross matrix (fg rows on bg columns, ratio):")
        L.append("    " + " " * 13 + "".join(f"{i:>6}" for i in range(16)))
        for f in ANSI_KEYS:
            L.append(f"    {f:<13}" + "".join(f"{d['cross'][f][b]:6.1f}" for b in ANSI_KEYS))
        L.append("")
    return "\n".join(L)


def validate(theme: dict) -> list[str]:
    errs: list[str] = []
    for mode in MODES:
        for k, val in flat(theme, mode).items():
            if not HEX.match(val):
                errs.append(f"{SCHEME_NAME[mode]}: {k} is not #rrggbb ({val!r})")
    if [a[1] for a in ANSI] != list(range(16)):
        errs.append("ANSI table must cover indexes 0..15 in order")
    return errs


# ---------------------------------------------------------------------------
# Emitters: TOML and Lua
# ---------------------------------------------------------------------------
def toml_val(v) -> str:
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, list):
        return "[" + ", ".join(toml_val(x) for x in v) + "]"
    if isinstance(v, dict):  # inline table
        return "{ " + ", ".join(f"{k} = {toml_val(x)}" for k, x in v.items()) + " }"
    raise TypeError(v)


def is_inline(v) -> bool:
    return isinstance(v, dict) and set(v) == {"Color"}


def toml_tables(d: dict, path: str, out: list[str]) -> None:
    subs = {k: v for k, v in d.items() if isinstance(v, dict) and not is_inline(v)}
    out.append(f"[{path}]")
    for k, v in d.items():
        if k not in subs:
            out.append(f"{k} = {toml_val(v)}")
    for k, v in subs.items():
        out.append("")
        toml_tables(v, f"{path}.{k}", out)


def scheme_toml(theme: dict, mode: str) -> str:
    out = [f"# {SCHEME_NAME[mode]} {theme['version']}: generated by scripts/build.py from src/theme.json. Do not edit by hand."]
    toml_tables(scheme_colors(theme, mode), "colors", out)
    out += ["", "[metadata]", f"name = {toml_val(SCHEME_NAME[mode])}", f"author = {toml_val(AUTHOR)}",
            f"origin_url = {toml_val(ORIGIN_URL)}", ""]
    return "\n".join(out)


LUA_IDENT = re.compile(r"^[A-Za-z_]\w*$")


def lua_val(v, level: int = 0) -> str:
    pad, pad_in = "  " * level, "  " * (level + 1)
    if isinstance(v, str):
        return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
    if isinstance(v, list):
        return "{ " + ", ".join(lua_val(x) for x in v) + " }"
    if isinstance(v, dict):
        if all(not isinstance(x, dict) for x in v.values()) and len(v) <= 1:
            return "{ " + ", ".join(f"{k} = {lua_val(x)}" for k, x in v.items()) + " }"
        lines = [f"{pad_in}{k if LUA_IDENT.match(k) else '[' + lua_val(k) + ']'} = {lua_val(x, level + 1)},"
                 for k, x in v.items()]
        return "{\n" + "\n".join(lines) + f"\n{pad}}}"
    raise TypeError(v)


PLUGIN_TEMPLATE = r"""-- Flatcap @VERSION@ for WezTerm.
-- Generated by scripts/build.py from src/theme.json. Do not edit by hand.
--
--   local wezterm = require 'wezterm'
--   local flatcap = wezterm.plugin.require 'https://github.com/cheycron/flatcap-wezterm'
--   local config = wezterm.config_builder()
--   flatcap.apply_to_config(config, { mode = 'system' })
--
-- Options (all optional):
--   mode   'system' (default, follows the OS appearance), 'slate' (dark) or 'daylight' (light)
--   fonts  false (default) | true | { code = 'Cascadia Code', ui = 'IBM Plex Sans' }
--
-- Never touched: opacity, backdrop, blur, key bindings, font sizes, front end.

local wezterm = require 'wezterm'

local M = {}

M.version = '@VERSION@'

M.names = @NAMES@

-- The two color schemes, in the format of `config.color_schemes`.
M.schemes = @SCHEMES@

-- What a color scheme cannot carry: the window frame (fancy tab bar) ...
M.window_frame = @FRAME@

-- ... and the overlays (command palette, character selector).
M.ui = @UI@

M.fonts = { code = '@FONT_CODE@', ui = '@FONT_UI@' }

local function copy(v)
  if type(v) ~= 'table' then
    return v
  end
  local out = {}
  for k, x in pairs(v) do
    out[k] = copy(x)
  end
  return out
end

-- 'Dark' and 'DarkHighContrast' are Slate; 'Light' and 'LightHighContrast' are Daylight.
function M.mode_for_appearance(appearance)
  if type(appearance) == 'string' and appearance:find 'Dark' then
    return 'slate'
  end
  return 'daylight'
end

-- wezterm.gui does not exist in the mux server process, so it is guarded; Slate is the fallback.
local function system_mode()
  if wezterm.gui and wezterm.gui.get_appearance then
    local ok, appearance = pcall(wezterm.gui.get_appearance)
    if ok then
      return M.mode_for_appearance(appearance)
    end
  end
  return 'slate'
end

function M.resolve_mode(mode)
  if mode == nil or mode == 'system' then
    return system_mode()
  end
  if mode == 'slate' or mode == 'daylight' then
    return mode
  end
  wezterm.log_warn("flatcap: unknown mode '" .. tostring(mode) .. "', using 'system'")
  return system_mode()
end

function M.apply_to_config(config, opts)
  opts = opts or {}
  local mode = M.resolve_mode(opts.mode)

  -- Register both schemes next to any the user already defined, then select one.
  local schemes = config.color_schemes or {}
  for key, name in pairs(M.names) do
    schemes[name] = copy(M.schemes[key])
  end
  config.color_schemes = schemes
  config.color_scheme = M.names[mode]

  -- The fancy tab bar reads config.colors.tab_bar directly and ignores the tab_bar of the
  -- selected scheme (WezTerm 20240203), so the tab colors are copied there. Only tab_bar is
  -- written: every other color still comes from the scheme.
  local colors = config.colors or {}
  local tab_bar = colors.tab_bar or {}
  for k, v in pairs(M.schemes[mode].tab_bar) do
    tab_bar[k] = copy(v)
  end
  colors.tab_bar = tab_bar
  config.colors = colors

  -- Merge into window_frame instead of replacing it, so the user's own keys survive.
  local frame = config.window_frame or {}
  for k, v in pairs(M.window_frame[mode]) do
    frame[k] = v
  end

  for k, v in pairs(M.ui[mode]) do
    config[k] = v
  end

  if opts.fonts then
    local f = type(opts.fonts) == 'table' and opts.fonts or {}
    config.font = wezterm.font(f.code or M.fonts.code)
    frame.font = wezterm.font { family = f.ui or M.fonts.ui, weight = 'Medium' }
  end

  config.window_frame = frame
  return config
end

return M
"""


def plugin_lua(theme: dict) -> str:
    f = fonts(theme)
    assert f["code"] == FONT_CODE and f["ui"] == FONT_UI, "typography changed in the core: review the plugin fonts"
    names = {m: SCHEME_NAME[m] for m in MODES}
    text = PLUGIN_TEMPLATE
    for token, val in {
        "@VERSION@": theme["version"],
        "@NAMES@": lua_val(names),
        "@SCHEMES@": lua_val({m: scheme_colors(theme, m) for m in MODES}),
        "@FRAME@": lua_val({m: window_frame(theme, m) for m in MODES}),
        "@UI@": lua_val({m: ui_keys(theme, m) for m in MODES}),
        "@FONT_CODE@": FONT_CODE, "@FONT_UI@": FONT_UI,
    }.items():
        text = text.replace(token, val)
    return text


# ---------------------------------------------------------------------------
# README / docs blocks
# ---------------------------------------------------------------------------
def md_colors(theme: dict) -> str:
    rows = ["| `[colors]` key | Flatcap role | Slate | Daylight |", "| :--- | :--- | :--- | :--- |"]
    for key, name, _ in [*COLORS, *SPEC_COLORS]:
        s, d = role(theme, "slate", name), role(theme, "daylight", name)
        shown = f"{key} = {{ Color }}" if (key, name, _) in SPEC_COLORS else key
        rows.append(f"| `{shown}` | `{name}` | `{s}` | `{d}` |")
    return "\n".join(rows)


def md_tabbar(theme: dict) -> str:
    rows = ["| `[colors.tab_bar]` key | Flatcap role | Slate | Daylight |", "| :--- | :--- | :--- | :--- |"]
    for group, key, name, _ in TAB_BAR:
        label = (group + "." if group else "") + key
        rows.append(f"| `{label}` | `{name}` | `{role(theme, 'slate', name)}` | `{role(theme, 'daylight', name)}` |")
    extra = ", ".join(f"`{k} = {v}`" for k, v in ACTIVE_TAB_EXTRA.items())
    rows.append(f"| `active_tab` (text attributes) | (non-color indicator) | {extra} | {extra} |")
    return "\n".join(rows)


def md_plugin_keys(theme: dict) -> str:
    rows = ["| Config key | Flatcap role | Slate | Daylight |", "| :--- | :--- | :--- | :--- |"]
    for key, name, _ in WINDOW_FRAME:
        rows.append(f"| `window_frame.{key}` | `{name}` | `{role(theme, 'slate', name)}` | `{role(theme, 'daylight', name)}` |")
    for key, name, _ in UI_KEYS:
        rows.append(f"| `{key}` | `{name}` | `{role(theme, 'slate', name)}` | `{role(theme, 'daylight', name)}` |")
    return "\n".join(rows)


def md_ansi(theme: dict) -> str:
    ev = evaluate(theme)
    rows = ["| # | Key | Flatcap role | Slate | Daylight |", "| ---: | :--- | :--- | :--- | :--- |"]
    for key, idx, rs, rd, _ in ANSI:
        r = f"`{rs}`" if rs == rd else f"`{rs}` (Slate) · `{rd}` (Daylight)"
        cells = []
        for mode in MODES:
            v = ev[mode]["values"]
            cells.append(f"`{v['ansi.' + key]}` · {ratio(v['ansi.' + key], v['background']):.1f}:1")
        rows.append(f"| {idx} | `{key}` | {r} | {cells[0]} | {cells[1]} |")
    return "\n".join(rows)


def md_contrast(theme: dict) -> str:
    ev = evaluate(theme)
    rows = ["| Pair | Slate | Daylight | Target | Result |", "| :--- | ---: | ---: | ---: | :--- |"]
    for (label, rs, t), (_l, rd, _t) in zip(ev["slate"]["rows"], ev["daylight"]["rows"]):
        rows.append(f"| {label} | {rs:.2f}:1 | {rd:.2f}:1 | {t:g}:1 | {'met' if rs >= t and rd >= t else 'not met'} |")
    return "\n".join(rows)


def md_info(theme: dict) -> str:
    d = info(theme)
    rows = ["| Pair (no core target) | Slate | Daylight |", "| :--- | ---: | ---: |"]
    for label, key in (("`selection_bg` vs `background`", "selection_bg_vs_bg"),
                       ("Active tab fill vs tab bar fill", "active_tab_vs_bar"),
                       ("Command palette fill vs `background`", "palette_vs_bg"),
                       ("`visual_bell` flash vs `background`", "bell_vs_bg"),
                       ("Default text on `background` in an inactive pane (estimate, default `inactive_pane_hsb`)", "inactive_pane")):
        rows.append(f"| {label} | {d['slate'][key]:.2f}:1 | {d['daylight'][key]:.2f}:1 |")
    return "\n".join(rows)


def md_ansibg(theme: dict) -> str:
    d = info(theme)
    out = []
    for mode, label in (("slate", "Slate"), ("daylight", "Daylight")):
        out += [f"{label}: text on an ANSI background color (`ESC[4Xm`), ratio of the text color on that background.", "",
                "| Background | default `foreground` | `black` | `brightWhite` |", "| :--- | ---: | ---: | ---: |"]
        for h in HUES:
            out.append(f"| `{h}` | {d[mode]['fg_on_ansi'][h]:.2f}:1 | {d[mode]['cross']['black'][h]:.2f}:1 | "
                       f"{d[mode]['cross']['brightWhite'][h]:.2f}:1 |")
        out.append("")
    return "\n".join(out).rstrip("\n")


def md_fonts(theme: dict) -> str:
    f = fonts(theme)
    return (f"| Use | Family (exact) |\n| :--- | :--- |\n"
            f"| Terminal (default) | `{f['code']}` |\n"
            f"| Prompts with icons (oh-my-posh, starship) | `{f['code_nf']}` |\n"
            f"| No ligatures (logs, literal output) | `{f['mono']}` |\n"
            f"| Tab bar, command palette (UI) | `{f['ui']}` |\n\n"
            f"Starting size: {fmt_num(f['size_px'])} px from `font.size.code`. `font_size` is in points: "
            f"{fmt_num(f['size_pt_96'])} on Windows and X11 at 96 DPI, {fmt_num(f['size_px'])} on macOS (72 DPI).")


def md_a11y(theme: dict) -> str:
    ev, d = evaluate(theme), info(theme)
    low = {m: min(r for lab, r, t in ev[m]["rows"] if lab.startswith("ANSI") and "`black`" not in lab and "`brightWhite`" not in lab)
           for m in MODES}
    fg = {m: ratio(ev[m]["values"]["foreground"], ev[m]["values"]["background"]) for m in MODES}
    return (f"Measured on the generated values: default text on the background is {fg['slate']:.1f}:1 in Slate and "
            f"{fg['daylight']:.1f}:1 in Daylight (target 7:1). Every ANSI color used as text is at least "
            f"{min(low.values()):.1f}:1 on the background (lowest: {low['slate']:.2f}:1 Slate, {low['daylight']:.2f}:1 Daylight; "
            f"target 5:1). Selected text uses the `selection.fg` / `selection.bg` pair "
            f"({ratio(ev['slate']['values']['selection_fg'], ev['slate']['values']['selection_bg']):.1f}:1 Slate, "
            f"{ratio(ev['daylight']['values']['selection_fg'], ev['daylight']['values']['selection_bg']):.1f}:1 Daylight).")


README_BLOCKS = {"fonts": md_fonts, "a11y": md_a11y}
DOC_BLOCKS = {"colors": md_colors, "tabbar": md_tabbar, "pluginkeys": md_plugin_keys, "ansi": md_ansi,
              "contrast": md_contrast, "info": md_info, "ansibg": md_ansibg}


def render_blocks(path: Path, blocks: dict, theme: dict) -> str:
    if not path.is_file():
        raise SystemExit(f"error: {path.relative_to(ROOT)} does not exist")
    text = path.read_text(encoding="utf-8")
    for name, fn in blocks.items():
        pat = re.compile(rf"(<!-- build:{name} -->)\n.*?(<!-- /build:{name} -->)", re.S)
        if not pat.search(text):
            raise SystemExit(f"error: {path.relative_to(ROOT)} is missing the build:{name} markers")
        text = pat.sub(lambda m: m.group(1) + "\n" + fn(theme) + "\n" + m.group(2), text)
    return text


# ---------------------------------------------------------------------------
# Extra checks
# ---------------------------------------------------------------------------
def check_toml(outputs: dict[Path, str], theme: dict) -> list[str]:
    """Parse each generated TOML and compare it with the model it came from."""
    errs = []
    if tomllib is None:
        return errs
    for mode in MODES:
        path = ROOT / "colors" / f"{SCHEME_NAME[mode]}.toml"
        try:
            doc = tomllib.loads(outputs[path])
        except tomllib.TOMLDecodeError as e:
            errs.append(f"{path.name}: invalid TOML: {e}")
            continue
        if doc.get("colors") != scheme_colors(theme, mode):
            errs.append(f"{path.name}: parsed [colors] differs from the model")
        if doc.get("metadata", {}).get("name") != SCHEME_NAME[mode]:
            errs.append(f"{path.name}: metadata.name mismatch")
    return errs


def check_no_hand_hex() -> list[str]:
    errs = []
    for p in (EXAMPLE, ROOT / "scripts" / "build.py"):
        if p.is_file() and re.search(r"#[0-9A-Fa-f]{6}\b", p.read_text(encoding="utf-8")):
            errs.append(f"{p.relative_to(ROOT)} contains a hand-written hex color")
    return errs


def lua_syntax(files: list[Path]) -> list[str]:
    for cmd in ("luac5.4", "luac", "luac5.3", "luajit"):
        exe = shutil.which(cmd)
        if exe:
            break
    else:
        return ["no Lua compiler on PATH (install lua5.4)"]
    errs = []
    for f in files:
        args = [exe, "-bl", str(f)] if "luajit" in exe else [exe, "-p", str(f)]
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode:
            errs.append(f"{f.relative_to(ROOT)}: {r.stderr.strip()}")
    return errs


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if generated outputs are stale or a contrast target is missed")
    ap.add_argument("--contrast", action="store_true", help="print the contrast report and exit")
    ap.add_argument("--lua", action="store_true", help="also syntax-check the Lua files with luac")
    ap.add_argument("--sync", nargs="?", const=str(UPSTREAM), metavar="PATH",
                    help="copy theme.json from the core checkout (default ../00-Flatcap/src/theme.json)")
    args = ap.parse_args()

    if args.sync:
        src = Path(args.sync)
        if src.is_dir():
            src = src / "src" / "theme.json"
        if not src.is_file():
            print(f"error: {src} not found", file=sys.stderr)
            return 2
        shutil.copyfile(src, THEME)
        print(f"synced {src} -> {THEME.relative_to(ROOT)}")

    theme = load()
    if not str(theme.get("version", "")).startswith("2."):
        print(f"error: expected Flatcap 2.x theme.json, got {theme.get('version')}", file=sys.stderr)
        return 2
    errs = validate(theme)
    if errs:
        print("\n".join("error: " + e for e in errs), file=sys.stderr)
        return 2
    if args.contrast:
        print(contrast_report(theme))
        return 0
    ev = evaluate(theme)
    fails = [f"{SCHEME_NAME[m]}: {lab.replace('`', '')} {r:.2f}:1 < {t:g}:1" for m in MODES for lab, r, t in ev[m]["fails"]]
    if fails:
        print("contrast targets missed:\n  " + "\n  ".join(fails), file=sys.stderr)
        return 1
    if UPSTREAM.is_file() and UPSTREAM.read_bytes() != THEME.read_bytes():
        print("note: src/theme.json differs from ../00-Flatcap (run --sync to refresh)", file=sys.stderr)

    outputs: dict[Path, str] = {ROOT / "colors" / f"{SCHEME_NAME[m]}.toml": scheme_toml(theme, m) for m in MODES}
    outputs[PLUGIN] = plugin_lua(theme)
    outputs[README] = render_blocks(README, README_BLOCKS, theme)
    outputs[MAPPING_DOC] = render_blocks(MAPPING_DOC, DOC_BLOCKS, theme)

    problems = check_toml(outputs, theme) + check_no_hand_hex()
    if problems:
        print("\n".join("error: " + p for p in problems), file=sys.stderr)
        return 1

    stale = []
    for path, text in outputs.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    if args.check and stale:
        print("stale: " + ", ".join(stale) + " (run python3 scripts/build.py)", file=sys.stderr)
        return 1
    if args.lua:
        lerrs = lua_syntax([PLUGIN, EXAMPLE])
        if lerrs:
            print("\n".join("error: " + e for e in lerrs), file=sys.stderr)
            return 1
        print("ok: Lua syntax")
    if args.check:
        print("ok: generated files are up to date; all contrast targets met")
    return 0


if __name__ == "__main__":
    sys.exit(main())
