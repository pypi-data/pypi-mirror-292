import math
from .__init__ import glm

class zencam3D:
    def __init__(self):
        self.speed:float=0.005
        self.rotspeed:float=0.003
        self.sensitivity:float=0.002
        self.location:glm.vec3=glm.vec3(16,32,48)

        self.yaw:float=glm.radians(-90)
        self.pitch:float=glm.radians(0)
        self.pitchmax:float=glm.radians(89)
        
        self.fov:float=50.0
        self.znear:float=0.1
        self.zfar:float=2000.0
        self.aspect:float=800/600
        self.fovx:float=glm.radians(self.fov)
        self.fovy:float=2*math.atan(math.tan(self.fovx*0.5)*self.aspect)
        
        self.m_view:glm.mat4=glm.mat4()
        self.up:glm.vec3=glm.vec3(0,1,0)
        self.right:glm.vec3=glm.vec3(1,0,0)
        self.forward:glm.vec3=glm.vec3(0,0,-1)
        self.m_proj:glm.mat4=glm.perspective(self.fovy, self.aspect, self.znear, self.zfar)

    def rotate_x(self, delta) -> None:
        self.pitch -= delta
        self.pitch = glm.clamp(self.pitch, -self.pitchmax, self.pitchmax)
    
    def rotate_y(self, delta) -> None:
        self.yaw += delta

    def move_up(self, delta) -> None:
        self.location+=self.up*delta
    def move_down(self, delta) -> None:
        self.location-=self.up*delta
    
    def move_left(self, delta) -> None:
        self.location-=self.right*delta
    def move_right(self, delta) -> None:
        self.location+=self.right*delta
    
    def move_in(self, delta) -> None:
        self.location+=self.forward*delta
    def move_out(self, delta) -> None:
        self.location-=self.forward*delta

    def _update_view(self) -> None: self.m_view = glm.lookAt(self.location, self.location+self.forward, self.up)

    def _update_vectors(self) -> None:
        self.forward.x = glm.cos(self.yaw) * glm.cos(self.pitch)
        self.forward.y = glm.sin(self.pitch)
        self.forward.z = glm.sin(self.yaw) * glm.cos(self.pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0,1,0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self) -> None: self._update_vectors(); self._update_view()
