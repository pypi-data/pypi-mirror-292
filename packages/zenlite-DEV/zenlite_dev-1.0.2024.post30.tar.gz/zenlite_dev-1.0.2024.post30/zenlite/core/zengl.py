from .globs import pg, ZEN_ASSET_DIR
import moderngl as gl

class zencontext:
    GL:gl.Context
    def __init__(self) -> None:
        pg.display.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)

    def make_window(self, size:tuple[int]=(800,600)):
        win = pg.display.set_mode(size, flags=pg.OPENGL|pg.DOUBLEBUF); pg.display.set_caption("zenlite"); pg.display.set_icon(pg.image.load(f"{ZEN_ASSET_DIR}logo_32x.ico"))
        self.GL:gl.Context = gl.create_context()
        self.GL.enable(flags=gl.DEPTH_TEST|gl.CULL_FACE|gl.BLEND); self.GL.gc_mode = 'auto'
        return win
