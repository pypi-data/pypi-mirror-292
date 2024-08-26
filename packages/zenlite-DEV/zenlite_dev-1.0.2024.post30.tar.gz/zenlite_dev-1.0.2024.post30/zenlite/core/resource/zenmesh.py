from .__init__ import zenresource, zenbank, glm, np

class zenmesh(zenresource):
    def __init__(self, id:int):
        super().__init__(id=id)
        self.vbo:int=None
        self.vao:int=None
        self.shader:int=None
        """ zenresource id """
        self.texture:int=-1
        """ zenresource id """
        self.vformat:str=None
        self.vertices:list[float]=None
        self.vattribs:tuple[str, ...]=None
        self.m_model:glm.mat4=glm.identity(glm.mat4)

    def set_shader(self, resources, shader_id:int) -> None:
        self.shader=shader_id if isinstance(shader_id, int) else -1
        resources.meshbank.shader[self.id]=self.shader

    def set_texture(self, zenresources, texture_id:int, unitname:str=None, unitloc:int=0) -> None:
        if isinstance(texture_id, int) and self.shader:
            uname = f"u_texture_{unitloc}" if unitname is None else unitname
            self.texture=texture_id
            zenresources.shaderbank.get_shader(self.shader).new_uniform(uname, unitloc)
            zenresources.meshbank.texture[self.id]=self.texture

ZEN_MESH_MAX:int=100_00
class zenmeshbank(zenbank):
    def __init__(self, zencontext, *args, **kwargs):
        super().__init__(max=ZEN_MESH_MAX)
        self.context=zencontext
        self.zenresources = args[0]
        self.active_id:list[int]=[]
        self.inactive_id:list[int]=[]
        self.vbo:list[int]=[-1 for _ in range(self.max)]
        self.vao:list[int]=[-1 for _ in range(self.max)]
        
        self.shader:list[int]=[-1 for _ in range(self.max)]
        """ zenresource id -> get a mesh shader interface = zen.resource.sbank.get_shader(mesh.shader) """
        
        self.texture:list[int]=[-1 for _ in range(self.max)]
        """ zenresource id -> get a mesh texture interface = zen.resource.tbank.get_texture(mesh.texture) """
        
        self.vformat:list[str]=["None" for _ in range(self.max)]
        self.vertices:list[list[float]]=[[] for _ in range(self.max)]
        self.vattribs:list[tuple[str]]=[tuple() for _ in range(self.max)]
        self.m_model:list[glm.mat4]=[glm.identity(glm.mat4) for _ in range(self.max)]

    def rem_mesh(self, mesh_id:int) -> None:
        if self.count-1 >= 0 and mesh_id <= self.max and mesh_id != -1:
            self.vbo[mesh_id] = -1
            self.vao[mesh_id] = -1
            self.shader[mesh_id] = -1
            self.texture[mesh_id] = -1
            self.m_model[mesh_id] = -1
            self.vformat[mesh_id] = -1
            self.vertices[mesh_id] = -1
            self.vattribs[mesh_id] = -1
            self.active_id.remove(mesh_id)
            self.inactive_id.append(mesh_id)
            self.active_id.sort()
            self.inactive_id.sort()
            self.count-=1
            return None

    def set_mesh(self, mesh:zenmesh) -> None:
        if mesh.id <= self.max and mesh.id != -1:
            self.vbo[mesh.id]=mesh.vbo
            self.vao[mesh.id]=mesh.vao
            self.shader[mesh.id]=mesh.shader
            self.texture[mesh.id]=mesh.texture
            self.m_model[mesh.id]=mesh.m_model
            self.vformat[mesh.id]=mesh.vformat
            self.vertices[mesh.id]=mesh.vertices
            self.vattribs[mesh.id]=mesh.vattribs

    def get_mesh(self, mesh_id:int) -> None|zenmesh|zenresource:
        if isinstance(mesh_id, int) and mesh_id <= self.max and mesh_id != -1:
            m:zenmesh=zenmesh(id=mesh_id)
            m.vbo=self.vbo[mesh_id]
            m.vao=self.vao[mesh_id]
            m.shader=self.shader[mesh_id]
            m.texture=self.texture[mesh_id]
            m.m_model=self.m_model[mesh_id]
            m.vformat=self.vformat[mesh_id]
            m.vertices=self.vertices[mesh_id]
            m.vattribs=self.vattribs[mesh_id]
            return m
        else: return None

    def make_mesh(self, vertices: list[tuple[float]], indices: list[tuple[int]] = None, colors: list[tuple[float]] = None, vformat: str = "3f", vattribs: tuple[str] = ('position',), shader_id:int=None) -> int:
        if self.count+1 <= self.max:
            if self.count in self.active_id:
                mesh_id:int=self.inactive_id.pop()
            else: mesh_id:int=self.count
            
            self.vformat[mesh_id]=vformat
            self.vattribs[mesh_id]=vattribs
            self.m_model[mesh_id]=glm.identity(glm.mat4)

            vertices_np=np.array(vertices, dtype="float32") if not isinstance(vertices, np.ndarray) else vertices
            colors_np=np.array(colors, dtype="float32") if colors is not None else None
            
            if colors is not None: vertex_data=np.hstack([vertices_np, colors_np], dtype="float32")
            else: vertex_data=vertices_np
                
            if indices is not None: vertex_data=np.array([vertex_data[ind] for triangle in indices for ind in triangle], dtype="float32")

            self.vertices[mesh_id]=vertex_data

            self.vbo[mesh_id]=self.context.GL.buffer(self.vertices[mesh_id])

            self.shader[mesh_id]=self.zenresources.shaders["default001"] if shader_id is None else shader_id
    
            self.vao[mesh_id]=self.context.GL.vertex_array(
                self.zenresources.shaderbank.get_shader(self.shader[mesh_id]).program,
                [(self.vbo[mesh_id], self.vformat[mesh_id], *self.vattribs[mesh_id])], skip_errors=True
            )
            self.active_id.append(mesh_id)
            self.active_id.sort()
            try:
                self.inactive_id.remove(mesh_id)
                self.inactive_id.sort()
            except (ValueError) as err: ...
            self.count += 1; return mesh_id
