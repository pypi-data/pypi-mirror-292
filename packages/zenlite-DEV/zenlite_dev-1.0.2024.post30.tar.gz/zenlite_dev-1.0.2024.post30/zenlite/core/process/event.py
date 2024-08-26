from .__init__ import zenprocess
from zenlite.core.globs import pg

# TODO: implement controller class
class zencontroller:
    def __init__(self) -> None:
        self.id:int=0

ZEN_CONTROLLER_MAX:int=6
class zenevents(zenprocess):
    def __init__(self, zenlite, *args, **kwargs)  -> None:
        super().__init__(*args, **kwargs)
        self.zen=zenlite
        self.quit:bool=False
        self.keyboard = {}
        self.mouse_pos = (0,0)
        self.mouse_delta = (0,0)
        self.kb_state = []
        self.mouse_state = []
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0
        self.mouse = {1:False, 2:False, 3:False, 4:False, 5:False, 6:False, 7:False}
        
        self.mouse_wheelu=False
        self.mouse_wheeld=False
        self.mouse_prev = {}
        self.keyboard_prev = {}
        
        self.controllers = {}
        self.controller = None
        self.controller_name = None
    
    def register_controller(self, name, controller):
        if len(list(self.controllers.keys())) + 1 < ZEN_CONTROLLER_MAX:
                if name not in self.controllers:
                    self.controllers[name] = controller
                    self.controller_name = name
                    self.controller = self.controllers[self.controller_name]
    
    def set_controller(self, name):
        if name in self.controllers:
            self.controller_name = name
            self.controller = self.controllers[self.controller_name]
    
    def rem_controller(self, name):
        if name in self.controllers:
            self.controllers.pop(name)
            index = len(list(self.controllers.keys())) - 1
            self.controller_name = list(self.controllers.keys())[index]
            self.controller = self.controllers[self.controller_name]

    def process(self, *args, **kwargs) -> int:
        self.mouse_wheelu = False
        self.mouse_wheeld = False
        self.mouse_prev = self.mouse.copy()
        self.keyboard_prev = self.keyboard.copy()
        self.kb_state = pg.key.get_pressed()
        self.mouse_state = pg.mouse.get_pressed()

        self.zen.state.mouseX, self.zen.state.mouseY = pg.mouse.get_pos()
        self.zen.state.mouseDX, self.zen.state.mouseDY = pg.mouse.get_rel()
        
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_F12): self.quit = True; self.polling = False
            match e.type:
                case pg.KEYUP:
                    self.keyboard[e.key] = False
                case pg.KEYDOWN:
                    self.keyboard[e.key] = True
                case pg.MOUSEBUTTONUP:
                    self.mouse[e.button] = False
                case pg.MOUSEBUTTONDOWN:
                    self.mouse[e.button] = True
                    if e.button == 4:
                        self.mouse_wheelu = True
                    if e.button == 5:
                        self.mouse_wheeld = True
        self.controller() if self.controller else 0

    def is_key_pressed(self, key):
        return self.keyboard.get(key, False)

    def is_key_triggered(self, key):
        return self.keyboard.get(key, False) and not self.keyboard_prev.get(key, False)
    
    def is_mouse_pressed(self, button:int):
        return self.mouse.get(button, False)

    def is_mouse_triggered(self, button):
        return self.mouse.get(button, False) and not self.mouse_prev.get(button, False)

class zenkb:
    # Letter keys
    A = pg.K_a
    B = pg.K_b
    C = pg.K_c
    D = pg.K_d
    E = pg.K_e
    F = pg.K_f
    G = pg.K_g
    H = pg.K_h
    I = pg.K_i
    J = pg.K_j
    K = pg.K_k
    L = pg.K_l
    M = pg.K_m
    N = pg.K_n
    O = pg.K_o
    P = pg.K_p
    Q = pg.K_q
    R = pg.K_r
    S = pg.K_s
    T = pg.K_t
    U = pg.K_u
    V = pg.K_v
    W = pg.K_w
    X = pg.K_x
    Y = pg.K_y
    Z = pg.K_z

    # Number keys
    Num0 = pg.K_0
    Num1 = pg.K_1
    Num2 = pg.K_2
    Num3 = pg.K_3
    Num4 = pg.K_4
    Num5 = pg.K_5
    Num6 = pg.K_6
    Num7 = pg.K_7
    Num8 = pg.K_8
    Num9 = pg.K_9

    # Function keys
    F1 = pg.K_F1
    F2 = pg.K_F2
    F3 = pg.K_F3
    F4 = pg.K_F4
    F5 = pg.K_F5
    F6 = pg.K_F6
    F7 = pg.K_F7
    F8 = pg.K_F8
    F9 = pg.K_F9
    F10 = pg.K_F10
    F11 = pg.K_F11
    F12 = pg.K_F12

    # Special keys
    Space = pg.K_SPACE
    Escape = pg.K_ESCAPE
    Enter = pg.K_RETURN
    Tab = pg.K_TAB
    Shift = pg.K_LSHIFT  # Left Shift
    Ctrl = pg.K_LCTRL    # Left Control
    Alt = pg.K_LALT      # Left Alt
    RShift = pg.K_RSHIFT  # Right Shift
    RCtrl = pg.K_RCTRL    # Right Control
    RAlt = pg.K_RALT      # Right Alt

    # Arrow keys
    Up = pg.K_UP
    Down = pg.K_DOWN
    Left = pg.K_LEFT
    Right = pg.K_RIGHT

    # Numpad keys
    NumPad0 = pg.K_KP0
    NumPad1 = pg.K_KP1
    NumPad2 = pg.K_KP2
    NumPad3 = pg.K_KP3
    NumPad4 = pg.K_KP4
    NumPad5 = pg.K_KP5
    NumPad6 = pg.K_KP6
    NumPad7 = pg.K_KP7
    NumPad8 = pg.K_KP8
    NumPad9 = pg.K_KP9
    NumPadDivide = pg.K_KP_DIVIDE
    NumPadMultiply = pg.K_KP_MULTIPLY
    NumPadSubtract = pg.K_KP_MINUS
    NumPadAdd = pg.K_KP_PLUS
    NumPadEnter = pg.K_KP_ENTER
    NumPadDecimal = pg.K_KP_PERIOD

    # Modifier keys
    LShift = pg.K_LSHIFT
    RShift = pg.K_RSHIFT
    LCtrl = pg.K_LCTRL
    RCtrl = pg.K_RCTRL
    LAlt = pg.K_LALT
    RAlt = pg.K_RALT
    LMeta = pg.K_LMETA
    RMeta = pg.K_RMETA
    LSuper = pg.K_LSUPER  # Windows key for left
    RSuper = pg.K_RSUPER  # Windows key for right

    # Miscellaneous keys
    CapsLock = pg.K_CAPSLOCK
    NumLock = pg.K_NUMLOCK
    ScrollLock = pg.K_SCROLLOCK
    PrintScreen = pg.K_PRINT
    Pause = pg.K_PAUSE
    Insert = pg.K_INSERT
    Delete = pg.K_DELETE
    Home = pg.K_HOME
    End = pg.K_END
    PageUp = pg.K_PAGEUP
    PageDown = pg.K_PAGEDOWN

    # Symbol keys
    Grave = pg.K_BACKQUOTE  # `~
    Minus = pg.K_MINUS      # -_
    Equals = pg.K_EQUALS    # =+
    LeftBracket = pg.K_LEFTBRACKET   # [{
    RightBracket = pg.K_RIGHTBRACKET # ]}
    Backslash = pg.K_BACKSLASH       # \|
    Semicolon = pg.K_SEMICOLON       # ;:
    Quote = pg.K_QUOTE               # '"
    Comma = pg.K_COMMA               # ,<
    Period = pg.K_PERIOD             # .>
    Slash = pg.K_SLASH               # /?
    BackSpace = pg.K_BACKSPACE
    Tab = pg.K_TAB
    Enter = pg.K_RETURN
    Menu = pg.K_MENU

class zenmouse:
    LeftClick = 1
    WheelClick = 2
    RightClick = 3
    WheelUp = 4
    WheelDown = 5