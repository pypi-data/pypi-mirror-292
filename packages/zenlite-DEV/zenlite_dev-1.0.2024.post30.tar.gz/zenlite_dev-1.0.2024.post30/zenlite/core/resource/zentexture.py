import moderngl as GL
from .__init__ import zenbank, zenresource
from zenlite.core.globs import pg

class zentexture(zenresource):
    def __init__(self, id:int) -> None:
        super().__init__(id=id)
        self.tag:str=None
        self.src:str=None
        self.data:pg.Surface=None
        self.globj=None
        self.unitloc:int=0

    def set_unit(self) -> bool:
        try: self.globj.use(self.unitloc); return True
        except () as err: print(err); return False

ZEN_TEXTURE_MAX:int=100
class zentexturebank(zenbank):
    def __init__(self, zencontext, *args, **kwargs) -> None:
        super().__init__(max=ZEN_TEXTURE_MAX, *args, **kwargs)
        self.context=zencontext
        self.tag:list[str]=["NULL" for _ in range(self.max)]
        self.src:list[str]=["NULL" for _ in range(self.max)]
        self.unitloc:list[int]=[-1 for _ in range(self.max)]
        self.data:list[pg.Surface]=[None for _ in range(self.max)]
        self.globj:list[GL.Texture]=[None for _ in range(self.max)]

    def get_texture(self, tex_id:int) -> None|zentexture|zenresource:
        if isinstance(tex_id, int) and tex_id <= self.max and tex_id != -1:
            t:zentexture=zentexture(tex_id)
            t.tag=self.tag[tex_id]
            t.src=self.src[tex_id]
            t.data=self.data[tex_id]
            t.globj=self.globj[tex_id]
            t.unitloc=self.unitloc[tex_id]
            return t
        else: return None

    def make_texture(self, tsrc:str, tag:str, unitloc:int=0) -> int:
        if self.count+1 <= self.max:
            tex_id:int=self.count
            self.tag[tex_id]=tag
            self.src[tex_id]=tsrc
            self.unitloc[tex_id]=unitloc
            self.data[tex_id]=pg.transform.flip(pg.image.load(tsrc), True, False)
            
            self.globj[tex_id]=self.context.GL.texture(
                size=self.data[tex_id].get_size(),
                components=4,
                # TODO:          make configureable for jpg 'RGB'/'RGBA'
                data=pg.image.tostring(self.data[tex_id], 'RGBA', False)
            )

            self.globj[tex_id].anisotropy=32.0
            self.globj[tex_id].build_mipmaps()
            self.globj[tex_id].filter = (GL.NEAREST, GL.NEAREST)
            
            self.count+=1; return tex_id
