-- Minimal WezTerm configuration using Flatcap 2.0.
-- Save as ~/.wezterm.lua (or $XDG_CONFIG_HOME/wezterm/wezterm.lua) and adjust.

local wezterm = require 'wezterm'
local config = wezterm.config_builder()

-- Fetched (cloned) once by WezTerm the first time this line runs.
local flatcap = wezterm.plugin.require 'https://github.com/cheycron/flatcap-wezterm'

-- mode: 'system' (default, follows the OS light/dark setting), 'slate' or 'daylight'.
-- fonts: opt-in; Cascadia Code for the terminal, IBM Plex Sans for the tab bar.
flatcap.apply_to_config(config, { mode = 'system', fonts = true })

-- Your own settings go after the plugin call, so they can override what it sets.
config.use_fancy_tab_bar = true
config.font_size = 11.25 -- points: 15 px at 96 DPI (use 15 on macOS, which counts at 72 DPI)

return config
