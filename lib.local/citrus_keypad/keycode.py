# pylint: disable-msg=invalid-name
from micropython import const
class ConsumerControlCode(int): pass
class MouseCode(int): pass

CC = ConsumerControlCode
MS = MouseCode

# Here we define all common keys for ease of use
# 这里定义了所有常用的键盘按键码，方便使用
# including keyboard keys, mouse buttons, and consumer control keys
# 包括键盘按键，鼠标按键，以及多媒体按键
# Please use search function to find the keycode corresponding to the target symbol
# 请使用搜索功能来找到目标符号对应的键盘按键码

### keyboard keys
### 键盘按键键码

A = const(0x04)
# ``a`` and ``A``
B = const(0x05)
# ``b`` and ``B``
C = const(0x06)
# ``c`` and ``C``
D = const(0x07)
# ``d`` and ``D``
E = const(0x08)
# ``e`` and ``E``
F = const(0x09)
# ``f`` and ``F``
G = const(0x0A)
# ``g`` and ``G``
H = const(0x0B)
# ``h`` and ``H``
I = const(0x0C)
# ``i`` and ``I``
J = const(0x0D)
# ``j`` and ``J``
K = const(0x0E)
# ``k`` and ``K``
L = const(0x0F)
# ``l`` and ``L``
M = const(0x10)
# ``m`` and ``M``
N = const(0x11)
# ``n`` and ``N``
O = const(0x12)
# ``o`` and ``O``
P = const(0x13)
# ``p`` and ``P``
Q = const(0x14)
# ``q`` and ``Q``
R = const(0x15)
# ``r`` and ``R``
S = const(0x16)
# ``s`` and ``S``
T = const(0x17)
# ``t`` and ``T``
U = const(0x18)
# ``u`` and ``U``
V = const(0x19)
# ``v`` and ``V``
W = const(0x1A)
# ``w`` and ``W``
X = const(0x1B)
# ``x`` and ``X``
Y = const(0x1C)
# ``y`` and ``Y``
Z = const(0x1D)
# ``z`` and ``Z``

N1 = ONE = const(0x1E)
# ``1`` and ``!``
N2 = TWO = const(0x1F)
# ``2`` and ``@``
N3 = THREE = const(0x20)
# ``3`` and ``#``
N4 = FOUR = const(0x21)
# ``4`` and ``$``
N5 = FIVE = const(0x22)
# ``5`` and ``%``
N6 = SIX = const(0x23)
# ``6`` and ``^``
N7 = SEVEN = const(0x24)
# ``7`` and ``&``
N8 = EIGHT = const(0x25)
# ``8`` and ``*``
N9 = NINE = const(0x26)
# ``9`` and ``(``
N0 = ZERO = const(0x27)
# ``0`` and ``)``
RETURN = ENTER = 0x28
# Enter (Return)
ESCAPE = ESC = const(0x29)
# Escape
BACKSPACE = const(0x2A)
# Delete backward (Backspace)
TAB = const(0x2B)
# Tab and Backtab
SPACE = SPACEBAR = const(0x2C)
# Spacebar
MINUS = const(0x2D)
# ``-` and ``_``
EQUALS = const(0x2E)
# ``=` and ``+``
LEFT_BRACKET = const(0x2F)
# ``[`` and ``{``
RIGHT_BRACKET = const(0x30)
# ``]`` and ``}``
BACKSLASH = const(0x31)
# ``\`` and ``|``
POUND = const(0x32)
# ``#`` and ``~`` (Non-US keyboard)
SEMICOLON = const(0x33)
# ``;`` and ``:``
QUOTE = const(0x34)
# ``'`` and ``"``
GRAVE_ACCENT = const(0x35)
# :literal:`\`` and ``~``
COMMA = const(0x36)
# ``,`` and ``<``
PERIOD = const(0x37)
# ``.`` and ``>``
FORWARD_SLASH = const(0x38)
# ``/`` and ``?``

CAPS_LOCK = const(0x39)
# Caps Lock

F1 = const(0x3A)
# Function key F1
F2 = const(0x3B)
# Function key F2
F3 = const(0x3C)
# Function key F3
F4 = const(0x3D)
# Function key F4
F5 = const(0x3E)
# Function key F5
F6 = const(0x3F)
# Function key F6
F7 = const(0x40)
# Function key F7
F8 = const(0x41)
# Function key F8
F9 = const(0x42)
# Function key F9
F10 = const(0x43)
# Function key F10
F11 = const(0x44)
# Function key F11
F12 = const(0x45)
# Function key F12

PRINT_SCREEN = const(0x46)
# Print Screen (SysRq)
SCROLL_LOCK = const(0x47)
# Scroll Lock
PAUSE = const(0x48)
# Pause (Break)

INSERT = const(0x49)
# Insert
HOME = const(0x4A)
# Home (often moves to beginning of line)
PAGE_UP = const(0x4B)
# Go back one page
DELETE = const(0x4C)
# Delete forward
END = const(0x4D)
# End (often moves to end of line)
PAGE_DOWN = const(0x4E)
# Go forward one page

RIGHT_ARROW = const(0x4F)
# Move the cursor right
LEFT_ARROW = const(0x50)
# Move the cursor left
DOWN_ARROW = const(0x51)
# Move the cursor down
UP_ARROW = const(0x52)
# Move the cursor up

KEYPAD_NUMLOCK = const(0x53)
# Num Lock (Clear on Mac)
KEYPAD_FORWARD_SLASH = const(0x54)
# Keypad ``/``
KEYPAD_ASTERISK = const(0x55)
# Keypad ``*``
KEYPAD_MINUS = const(0x56)
# Keyapd ``-``
KEYPAD_PLUS = const(0x57)
# Keypad ``+``
KEYPAD_ENTER = const(0x58)
# Keypad Enter
KEYPAD_ONE = const(0x59)
# Keypad ``1`` and End
KEYPAD_TWO = const(0x5A)
# Keypad ``2`` and Down Arrow
KEYPAD_THREE = const(0x5B)
# Keypad ``3`` and PgDn
KEYPAD_FOUR = const(0x5C)
# Keypad ``4`` and Left Arrow
KEYPAD_FIVE = const(0x5D)
# Keypad ``5``
KEYPAD_SIX = const(0x5E)
# Keypad ``6`` and Right Arrow
KEYPAD_SEVEN = const(0x5F)
# Keypad ``7`` and Home
KEYPAD_EIGHT = const(0x60)
# Keypad ``8`` and Up Arrow
KEYPAD_NINE = const(0x61)
# Keypad ``9`` and PgUp
KEYPAD_ZERO = const(0x62)
# Keypad ``0`` and Ins
KEYPAD_PERIOD = const(0x63)
# Keypad ``.`` and Del
KEYPAD_BACKSLASH = const(0x64)
# Keypad ``\\`` and ``|`` (Non-US)

MENU = APPLICATION = const(0x65)
# Application: also known as the Menu key (Windows)
POWER = const(0x66)
# Power (Mac)
KEYPAD_EQUALS = const(0x67)
# Keypad ``=`` (Mac)
F13 = const(0x68)
# Function key F13 (Mac)
F14 = const(0x69)
# Function key F14 (Mac)
F15 = const(0x6A)
# Function key F15 (Mac)
F16 = const(0x6B)
# Function key F16 (Mac)
F17 = const(0x6C)
# Function key F17 (Mac)
F18 = const(0x6D)
# Function key F18 (Mac)
F19 = const(0x6E)
# Function key F19 (Mac)

F20 = const(0x6F)
# Function key F20
F21 = const(0x70)
# Function key F21
F22 = const(0x71)
# Function key F22
F23 = const(0x72)
# Function key F23
F24 = const(0x73)
# Function key F24

LEFT_CONTROL = const(0xE0)
# Control modifier left of the spacebar
CONTROL = const(LEFT_CONTROL)
# Alias for LEFT_CONTROL
LEFT_SHIFT = const(0xE1)
# Shift modifier left of the spacebar
SHIFT = const(LEFT_SHIFT)
# Alias for LEFT_SHIFT
LEFT_ALT = const(0xE2)
# Alt modifier left of the spacebar
ALT = const(LEFT_ALT)
# Alias for LEFT_ALT; Alt is also known as Option (Mac)
OPTION = const(ALT)
# Labeled as Option on some Mac keyboards
LEFT_GUI = const(0xE3)
# GUI modifier left of the spacebar
GUI = const(LEFT_GUI)
# Alias for LEFT_GUI; GUI is also known as the Windows key, Command (Mac), or Meta
WINDOWS = const(GUI)
# Labeled with a Windows logo on Windows keyboards
COMMAND = const(GUI)
# Labeled as Command on Mac keyboards, with a clover glyph
RIGHT_CONTROL = const(0xE4)
# Control modifier right of the spacebar
RIGHT_SHIFT = const(0xE5)
# Shift modifier right of the spacebar
RIGHT_ALT = const(0xE6)
# Alt modifier right of the spacebar
RIGHT_GUI = const(0xE7)
# GUI modifier right of the spacebar

### Mouse keys
### 鼠标按键

# the actual usage id is the bit number
# precalculate them makes it compatible with adafruit_hid

M_LEFT = M_L = MS(1)
# Left mouse button 鼠标左键
M_RIGHT = M_R = MS(2)
# Right mouse button 鼠标右键
M_MIDDLE = M_MID = MS(4)
# Middle mouse button 鼠标中键
M_BACK = MS(8)
# Back button 鼠标返回键
M_FORWARD = M_FWD = MS(16)
# Forward button 鼠标前进键

### Consumer control keys
### 多媒体控制键

C_RECORD = CC(0xB2)
# Record 录制
C_FAST_FORWARD = CC(0xB3)
# Fast Forward 快进
C_REWIND = CC(0xB4)
# Rewind 倒带
C_SCAN_NEXT_TRACK = CC(0xB5)
# Scan next track 跳至下一节
C_SCAN_PREVIOUS_TRACK = CC(0xB6)
# Scan previous track 跳至上一节
C_STOP = CC(0xB7)
# Stop 停止
C_EJECT = CC(0xB8)
# Eject 弹出
C_PLAY_PAUSE = CC(0xCD)
# Play/Pause 播放/暂停
C_MUTE = CC(0xE2)
# Mute 静音
C_VOLUME_DECREMENT = CC(0xEA)
# Volumne decrement 音量减
C_VOLUME_INCREMENT = CC(0xE9)
# Volumne increment 音量增
C_BRIGHTNESS_DECREMENT = CC(0x70)
# Brightness decrement 降低显示亮度
C_BRIGHTNESS_INCREMENT = CC(0x6F)
# Brightness increment 增加显示亮度
