from .core.globs import pg, glm, glfw, time, ZEN_ASSET_DIR
from .zplatform import *
from .zapplication import *
from .core.zengl import zencontext
from .core.zenprofiler import zenprofiler
from .core.process.render import zenrenderer
from .core.resource.zencam3D import zencam3D
from .core.resource.zenmesh import zenmesh, zenmeshbank
from .core.process.event import zenevents, zenkb, zenmouse
from .core.resource.zvxbank import zvxchunk, zvxchunkbank
from .core.resource.zenshader import zenshader, zenshaderbank
from .core.resource.zentexture import zentexture, zentexturebank

from .core.zenvx.zvxterrain import zvxterraingen, simplexGL, simple_fill, ridged_noise, plateau_noise, hybrid_terrain, octave_noise, biome_noise, heightmap_noise

zendebug:zenprofiler=zenprofiler()
class zenlite:
    class config:
        target_fps:int=144

    class process:
        event:zenevents
        render:zenrenderer

    class state:
        running:bool
        fps:float=0.0
        time:float=0.0
        mouseX:float=0.0
        mouseY:float=0.0
        mouseDX:float=0.0
        mouseDY:float=0.0
        end_time:float=0.0
        start_time:float=0.0
        delta_time:float=0.0
        cursorhide:bool=False
        cursorgrab:bool=False
        clock:pg.time.Clock=pg.time.Clock()

    class resource:
        camera:zencam3D
        window:pg.Surface
        meshbank:zenmeshbank
        chunkbank:zvxchunkbank
        shaderbank:zenshaderbank
        texturebank:zentexturebank
        zvxterrain:zvxterraingen
        
        shaders:dict={
            "default001":None,
            "default002":None
        }
        
        textures:dict={
            "zenwhite":None,
            "zenblack":None
        }

        def make_quad_mesh() -> int:
            return zenlite.resource.meshbank.make_mesh(
                vertices=[
                    (0.5, 0.5, 0.0),
                    (-0.5, 0.5, 0.0),
                    (-0.5, -0.5, 0.0),
                
                    (0.5, 0.5, 0.0),
                    (-0.5, -0.5, 0.0),
                    (0.5, -0.5, 0.0)
                ],
                colors=[
                    (0, 1, 0), (1, 0, 0), (1, 1, 0),
                    (0, 1, 0), (1, 1, 0), (0, 0, 1)
                ],
                vattribs=('position', 'color'),
                vformat="3f 3f"
            )

        def make_cube_mesh() -> int:
            return zenlite.resource.meshbank.make_mesh(
                vertices=[
                    (-1.0, -1.0, 1.0),  (1.0, -1.0, 1.0),  (1.0, 1.0, 1.0),  (-1.0, 1.0, 1.0),
                    (-1.0, 1.0, -1.0), (-1.0, -1.0, -1.0), (1.0, -1.0, -1.0), (1.0, 1.0, -1.0)
                ],
                indices=[
                    (0, 2, 3), (0, 1, 2),
                    (1, 7, 2), (1, 6, 7),
                    (6, 5, 4), (4, 7, 6),
                    (3, 4, 5), (3, 5, 0),
                    (3, 7, 4), (3, 2, 7),
                    (0, 6, 1), (0, 5, 6)
                ],
                colors=[
                    (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 1.0),
                    (0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 1.0, 0.0)
                ],
                vattribs=('position', 'color'),
                vformat="3f 3f"
            )

    def __init__(self) -> None:
        self.context:zencontext=zencontext()
        self.resource.window = self.context.make_window()
        self.__init_resources__()
        self.__precompile__()
        self.__pregenerate__()
        self.__init_processes__()
        self.state.running = True

    def __precompile__(self) -> None:
        self.resource.shaders["default001"] = self.resource.shaderbank.make_shader(
            f"{ZEN_ASSET_DIR}shaders/zen01.vert",
            f"{ZEN_ASSET_DIR}shaders/zen01.frag",
            "default001"
        )

        self.resource.shaders["default002"] = self.resource.shaderbank.make_shader(
            f"{ZEN_ASSET_DIR}shaders/zen02.vert",
            f"{ZEN_ASSET_DIR}shaders/zen02.frag",
            "default002"
        )

        [ self.resource.shaderbank.set_uniforms(shader, "m_proj", self.resource.camera.m_proj) for shader in self.resource.shaders.values() ]

    def __pregenerate__(self) -> None:
        self.resource.textures["zenblack"] = self.resource.texturebank.make_texture(
            f"{ZEN_ASSET_DIR}textures/zenblack.png", tag="zenblack", unitloc=0
        )
        self.resource.textures["zenwhite"] = self.resource.texturebank.make_texture(
            f"{ZEN_ASSET_DIR}textures/zenwhite.png", tag="zenwhite", unitloc=0
        )

    def __init_resources__(self) -> None:
        self.resource.camera = zencam3D()
        self.resource.meshbank=zenmeshbank(self.context, self.resource)
        self.resource.shaderbank=zenshaderbank(self.context)
        self.resource.texturebank=zentexturebank(self.context)
        self.resource.chunkbank=zvxchunkbank(self.resource)
        self.resource.zvxterrain=zvxterraingen(noise_function=biome_noise)

    def __init_processes__(self) -> None:
        self.process.event=zenevents(self)
        self.process.render=zenrenderer()
    
    def run(self, *args, **kwargs) -> None:
        while self.state.running:
            self.state.running = not self.process.event.quit

            self.state.delta_time = self.state.clock.tick(self.config.target_fps)
            self.state.time = pg.time.get_ticks() * 0.001
            self.state.fps = self.state.clock.get_fps()

            self.process.event.process(args, kwargs)
            self.resource.camera.update()

            self.process.render.pre_process(self.context, args, kwargs)
            for mesh_id in self.resource.meshbank.active_id:
                if mesh_id != -1:
                    mesh=self.resource.meshbank.get_mesh(mesh_id=mesh_id)
                    shader=self.resource.shaderbank.get_shader(mesh.shader)
                    texture=self.resource.texturebank.get_texture(mesh.texture)
                    shader.set_uniform(
                        "m_view",
                        self.resource.camera.m_view
                    ); shader.set_uniform(
                        "m_model",
                        mesh.m_model
                    ); texture.set_unit() if texture else 0
                    self.process.render.process(mesh, args, kwargs)
            self.process.render.post_process(args, kwargs)


# zenlite 'engine' methods
def hide_cursor() -> None:
    zenlite.state.cursorhide=True; pg.mouse.set_visible(not zenlite.state.cursorhide)

def show_cursor() -> None:
    zenlite.state.cursorhide=False; pg.mouse.set_visible(not zenlite.state.cursorhide)

def grab_cursor() -> None:
    zenlite.state.cursorgrab=True;  pg.event.set_grab(zenlite.state.cursorgrab)

def release_cursor() -> None:
    zenlite.state.cursorgrab=False; pg.event.set_grab(zenlite.state.cursorgrab)

def start_timer() -> None:
    zenlite.state.start_time = time.perf_counter()

def stop_timer() -> float:
    end_time = time.perf_counter()
    return end_time - zenlite.state.start_time

# TODO: no specific order :)
# anti-aliasing
# [byte-code optimization]
# model bank/interface implementation
# [byte-code optimization]
# material bank/interface implementation
# [byte-code optimization]
# frame buffer objects
# [byte-code optimization]
# frustum culling
# [byte-code optimization]
# ambiant occlusion
# anisotropic filtering
# phong lighting
# [byte-code optimization]

