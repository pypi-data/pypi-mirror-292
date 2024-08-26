from zenlite.core.globs import pg, glm
from .__init__ import zenprocess

class zenrenderer(zenprocess):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.mode = 0
        self.calls = 0
        self.window = 0
        self._wireframe:bool=False
        self.clear_color:list[float]=glm.vec3(0.1, 0.16, 0.25)

    def wireframe(self, mode:bool=True) -> None:
        self._wireframe = mode

    def pre_process(self, zencontext, *args, **kwargs) -> None:
        if zencontext.GL.wireframe != self._wireframe: zencontext.GL.wireframe = self._wireframe
        zencontext.GL.clear(color=self.clear_color)

    def process(self, mesh, *args, **kwargs) -> None:
        self.calls+=1;mesh.vao.render()
    
    def post_process(self, *args, **kwargs) -> None:
        pg.display.flip()
