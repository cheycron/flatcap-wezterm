<!-- build:colors -->
| `[colors]` key | Flatcap role | Slate | Daylight |
| :--- | :--- | :--- | :--- |
| `foreground` | `text.primary` | `#D5DBE3` | `#28313B` |
| `background` | `bg.canvas` | `#191D22` | `#F3F5F7` |
| `cursor_bg` | `accent.fill` | `#9BBFDF` | `#285D85` |
| `cursor_fg` | `accent.on` | `#101820` | `#FAFBFC` |
| `cursor_border` | `accent.fill` | `#9BBFDF` | `#285D85` |
| `selection_fg` | `selection.fg` | `#D5DBE3` | `#28313B` |
| `selection_bg` | `selection.bg` | `#3C546B` | `#C8DDF0` |
| `scrollbar_thumb` | `border.control` | `#8593A5` | `#6C7A89` |
| `split` | `border.control` | `#8593A5` | `#6C7A89` |
| `compose_cursor` | `warning.fg` | `#D8BC87` | `#765319` |
| `visual_bell` | `info.bg` | `#263E53` | `#DCE9F4` |
| `copy_mode_active_highlight_bg = { Color }` | `accent.fill` | `#9BBFDF` | `#285D85` |
| `copy_mode_active_highlight_fg = { Color }` | `accent.on` | `#101820` | `#FAFBFC` |
| `copy_mode_inactive_highlight_bg = { Color }` | `bg.selected` | `#263E53` | `#DCE9F4` |
| `copy_mode_inactive_highlight_fg = { Color }` | `text.primary` | `#D5DBE3` | `#28313B` |
| `quick_select_label_bg = { Color }` | `accent.fill` | `#9BBFDF` | `#285D85` |
| `quick_select_label_fg = { Color }` | `accent.on` | `#101820` | `#FAFBFC` |
| `quick_select_match_bg = { Color }` | `selection.bg` | `#3C546B` | `#C8DDF0` |
| `quick_select_match_fg = { Color }` | `selection.fg` | `#D5DBE3` | `#28313B` |
<!-- /build:colors -->
<!-- build:tabbar -->
| `[colors.tab_bar]` key | Flatcap role | Slate | Daylight |
| :--- | :--- | :--- | :--- |
| `background` | `bg.surface` | `#20252B` | `#FAFBFC` |
| `inactive_tab_edge` | `border.subtle` | `#3D4652` | `#D2D9E0` |
| `active_tab.bg_color` | `bg.canvas` | `#191D22` | `#F3F5F7` |
| `active_tab.fg_color` | `text.primary` | `#D5DBE3` | `#28313B` |
| `inactive_tab.bg_color` | `bg.surface` | `#20252B` | `#FAFBFC` |
| `inactive_tab.fg_color` | `text.secondary` | `#AEB8C4` | `#465463` |
| `inactive_tab_hover.bg_color` | `bg.hover` | `#323A43` | `#E6EBF0` |
| `inactive_tab_hover.fg_color` | `text.primary` | `#D5DBE3` | `#28313B` |
| `new_tab.bg_color` | `bg.surface` | `#20252B` | `#FAFBFC` |
| `new_tab.fg_color` | `text.secondary` | `#AEB8C4` | `#465463` |
| `new_tab_hover.bg_color` | `bg.hover` | `#323A43` | `#E6EBF0` |
| `new_tab_hover.fg_color` | `text.primary` | `#D5DBE3` | `#28313B` |
| `active_tab` (text attributes) | (non-color indicator) | `intensity = Bold` | `intensity = Bold` |
<!-- /build:tabbar -->
<!-- build:pluginkeys -->
| Config key | Flatcap role | Slate | Daylight |
| :--- | :--- | :--- | :--- |
| `window_frame.active_titlebar_bg` | `bg.surface` | `#20252B` | `#FAFBFC` |
| `window_frame.inactive_titlebar_bg` | `bg.surface` | `#20252B` | `#FAFBFC` |
| `window_frame.active_titlebar_fg` | `text.primary` | `#D5DBE3` | `#28313B` |
| `window_frame.inactive_titlebar_fg` | `text.secondary` | `#AEB8C4` | `#465463` |
| `window_frame.active_titlebar_border_bottom` | `border.subtle` | `#3D4652` | `#D2D9E0` |
| `window_frame.inactive_titlebar_border_bottom` | `border.subtle` | `#3D4652` | `#D2D9E0` |
| `window_frame.button_fg` | `text.secondary` | `#AEB8C4` | `#465463` |
| `window_frame.button_bg` | `bg.surface` | `#20252B` | `#FAFBFC` |
| `window_frame.button_hover_fg` | `text.primary` | `#D5DBE3` | `#28313B` |
| `window_frame.button_hover_bg` | `bg.hover` | `#323A43` | `#E6EBF0` |
| `command_palette_bg_color` | `bg.raised` | `#292F36` | `#FFFFFF` |
| `command_palette_fg_color` | `text.primary` | `#D5DBE3` | `#28313B` |
| `char_select_bg_color` | `bg.raised` | `#292F36` | `#FFFFFF` |
| `char_select_fg_color` | `text.primary` | `#D5DBE3` | `#28313B` |
<!-- /build:pluginkeys -->
<!-- build:ansi -->
| # | Key | Flatcap role | Slate | Daylight |
| ---: | :--- | :--- | :--- | :--- |
| 0 | `black` | `border.subtle` (Slate) · `text.primary` (Daylight) | `#3D4652` · 1.8:1 | `#28313B` · 12.1:1 |
| 1 | `red` | `danger.fg` | `#E2A0A5` · 7.9:1 | `#A43F4A` · 5.7:1 |
| 2 | `green` | `success.fg` | `#9FC3AD` · 8.8:1 | `#32664D` · 6.1:1 |
| 3 | `yellow` | `warning.fg` | `#D8BC87` · 9.2:1 | `#765319` · 6.4:1 |
| 4 | `blue` | `accent.fg` | `#9BBFDF` · 8.8:1 | `#285D85` · 6.4:1 |
| 5 | `purple` | `syntax.number` | `#B6AED5` · 8.1:1 | `#68598C` · 5.7:1 |
| 6 | `cyan` | `syntax.function` | `#ABC9CB` · 9.6:1 | `#306770` · 5.8:1 |
| 7 | `white` | `text.secondary` | `#AEB8C4` · 8.4:1 | `#465463` · 7.1:1 |
| 8 | `brightBlack` | `text.muted` | `#A7B3C2` · 8.0:1 | `#536273` · 5.7:1 |
| 9 | `brightRed` | `danger.fg` | `#E2A0A5` · 7.9:1 | `#A43F4A` · 5.7:1 |
| 10 | `brightGreen` | `success.fg` | `#9FC3AD` · 8.8:1 | `#32664D` · 6.1:1 |
| 11 | `brightYellow` | `warning.fg` | `#D8BC87` · 9.2:1 | `#765319` · 6.4:1 |
| 12 | `brightBlue` | `accent.hover` | `#ACCCE7` · 10.1:1 | `#214F73` · 7.9:1 |
| 13 | `brightPurple` | `syntax.number` | `#B6AED5` · 8.1:1 | `#68598C` · 5.7:1 |
| 14 | `brightCyan` | `syntax.function` | `#ABC9CB` · 9.6:1 | `#306770` · 5.8:1 |
| 15 | `brightWhite` | `text.primary` (Slate) · `bg.raised` (Daylight) | `#D5DBE3` · 12.2:1 | `#FFFFFF` · 1.1:1 |
<!-- /build:ansi -->
<!-- build:contrast -->
| Pair | Slate | Daylight | Target | Result |
| :--- | ---: | ---: | ---: | :--- |
| `foreground` on `background` | 12.15:1 | 12.06:1 | 7:1 | met |
| `cursor_fg` on `cursor_bg` | 9.30:1 | 6.77:1 | 4.5:1 | met |
| `cursor_bg` on `background` | 8.80:1 | 6.42:1 | 3:1 | met |
| `cursor_border` on `background` | 8.80:1 | 6.42:1 | 3:1 | met |
| `selection_fg` on `selection_bg` | 5.64:1 | 9.45:1 | 4.5:1 | met |
| `scrollbar_thumb` on `background` | 5.41:1 | 4.02:1 | 3:1 | met |
| `split` on `background` | 5.41:1 | 4.02:1 | 3:1 | met |
| `compose_cursor` on `background` | 9.24:1 | 6.36:1 | 3:1 | met |
| `copy_mode_active_highlight_fg` on `_bg` | 9.30:1 | 6.77:1 | 4.5:1 | met |
| `copy_mode_inactive_highlight_fg` on `_bg` | 7.95:1 | 10.68:1 | 4.5:1 | met |
| `quick_select_label_fg` on `_bg` | 9.30:1 | 6.77:1 | 4.5:1 | met |
| `quick_select_match_fg` on `_bg` | 5.64:1 | 9.45:1 | 4.5:1 | met |
| Active tab text | 12.15:1 | 12.06:1 | 7:1 | met |
| Inactive tab text | 7.68:1 | 7.48:1 | 5:1 | met |
| Inactive tab text, hover | 8.27:1 | 10.99:1 | 7:1 | met |
| New-tab button | 7.68:1 | 7.48:1 | 5:1 | met |
| New-tab button, hover | 8.27:1 | 10.99:1 | 7:1 | met |
| Title bar text, active | 11.07:1 | 12.73:1 | 7:1 | met |
| Title bar text, inactive | 7.68:1 | 7.48:1 | 5:1 | met |
| Window buttons | 7.68:1 | 7.48:1 | 5:1 | met |
| Window buttons, hover | 8.27:1 | 10.99:1 | 7:1 | met |
| Command palette text | 9.70:1 | 13.19:1 | 7:1 | met |
| Character selector text | 9.70:1 | 13.19:1 | 7:1 | met |
| ANSI `red` on `background` | 7.91:1 | 12.06:1 | 5:1 | met |
| ANSI `green` on `background` | 8.78:1 | 5.67:1 | 5:1 | met |
| ANSI `yellow` on `background` | 9.24:1 | 6.11:1 | 5:1 | met |
| ANSI `blue` on `background` | 8.80:1 | 6.36:1 | 5:1 | met |
| ANSI `purple` on `background` | 8.07:1 | 6.42:1 | 5:1 | met |
| ANSI `cyan` on `background` | 9.63:1 | 5.66:1 | 5:1 | met |
| ANSI `white` on `background` | 8.43:1 | 5.82:1 | 5:1 | met |
| ANSI `brightBlack` on `background` | 7.96:1 | 7.09:1 | 5:1 | met |
| ANSI `brightRed` on `background` | 7.91:1 | 5.71:1 | 5:1 | met |
| ANSI `brightGreen` on `background` | 8.78:1 | 5.67:1 | 5:1 | met |
| ANSI `brightYellow` on `background` | 9.24:1 | 6.11:1 | 5:1 | met |
| ANSI `brightBlue` on `background` | 10.12:1 | 6.36:1 | 5:1 | met |
| ANSI `brightPurple` on `background` | 8.07:1 | 7.91:1 | 5:1 | met |
| ANSI `brightCyan` on `background` | 9.63:1 | 5.66:1 | 5:1 | met |
| ANSI `brightWhite` on `background` | 12.15:1 | 5.82:1 | 5:1 | met |
<!-- /build:contrast -->
<!-- build:info -->
| Pair (no core target) | Slate | Daylight |
| :--- | ---: | ---: |
| `selection_bg` vs `background` | 2.15:1 | 1.28:1 |
| Active tab fill vs tab bar fill | 1.10:1 | 1.05:1 |
| Command palette fill vs `background` | 1.25:1 | 1.09:1 |
| `visual_bell` flash vs `background` | 1.53:1 | 1.13:1 |
| Default text on `background` in an inactive pane (estimate, default `inactive_pane_hsb`) | 8.18:1 | 8.52:1 |
<!-- /build:info -->
<!-- build:ansibg -->
Slate: text on an ANSI background color (`ESC[4Xm`), ratio of the text color on that background.

| Background | default `foreground` | `black` | `brightWhite` |
| :--- | ---: | ---: | ---: |
| `red` | 1.54:1 | 4.46:1 | 1.54:1 |
| `green` | 1.38:1 | 4.96:1 | 1.38:1 |
| `yellow` | 1.31:1 | 5.22:1 | 1.31:1 |
| `blue` | 1.38:1 | 4.97:1 | 1.38:1 |
| `purple` | 1.51:1 | 4.56:1 | 1.51:1 |
| `cyan` | 1.26:1 | 5.44:1 | 1.26:1 |

Daylight: text on an ANSI background color (`ESC[4Xm`), ratio of the text color on that background.

| Background | default `foreground` | `black` | `brightWhite` |
| :--- | ---: | ---: | ---: |
| `red` | 2.13:1 | 2.13:1 | 6.20:1 |
| `green` | 1.97:1 | 1.97:1 | 6.68:1 |
| `yellow` | 1.90:1 | 1.90:1 | 6.95:1 |
| `blue` | 1.88:1 | 1.88:1 | 7.01:1 |
| `purple` | 2.13:1 | 2.13:1 | 6.18:1 |
| `cyan` | 2.07:1 | 2.07:1 | 6.36:1 |
<!-- /build:ansibg -->
