from ..globs import glm
from ..resource.zvxbank import zvxchunkbank

class zvxterraingen:
    def __init__(self, noise_function, scale=0.01, height_scale=64):
        self.scale=scale
        self.height_scale=height_scale
        self.noise_function=noise_function

    def generate(self, chunk_id: int, chunkbank:zvxchunkbank) -> None:
        """ Generate terrain using the provided noise function """
        localx, localy, localz = chunkbank.chunks.location[chunk_id]
        for x in range(chunkbank.chunks.size[chunk_id]):
            for z in range(chunkbank.chunks.size[chunk_id]):
                relx = x + localx
                relz = z + localz
                noise_value = self.noise_function(glm.vec2(relx, relz) * self.scale)
                relheight = int(noise_value * self.height_scale/2+self.height_scale/2)
                localheight = min(relheight - localy, chunkbank.chunks.size[chunk_id])
                for y in range(int(localheight)):
                    rely = y + localy
                    chunkbank.chunks.voxels[chunk_id][x + chunkbank.chunks.size[chunk_id] * z + chunkbank.chunks.area[chunk_id] * y] = rely + 1


""" TERRAIN GENERATION ALGORITHMS """
def simplexGL(vec:glm.vec2) -> glm.vec2: return glm.simplex(vec)
    

# def simple_fill(self, chunk_id:int) -> None:
#     """ simple zvx terrain generation (fills an entire chunk) """
#     if chunk_id <= self.max and chunk_id != -1:
#         for x in range(self.chunks.size[chunk_id]):
#             for z in range(self.chunks.size[chunk_id]):
#                 for y in range(self.chunks.size[chunk_id]):
#                     self.chunks.voxels[chunk_id][x+self.chunks.size[chunk_id]*z+self.chunks.area[chunk_id]*y]=x+y+z

# def simple_noise(self, chunk_id:int) -> None:
#     """ simple 3D noise terrain generation using the simplex wave function """
#     if chunk_id <= self.max and chunk_id != -1:
#         for x in range(self.chunks.size[chunk_id]):
#             for z in range(self.chunks.size[chunk_id]):
#                 for y in range(self.chunks.size[chunk_id]):
#                     self.chunks.voxels[chunk_id][x+self.chunks.size[chunk_id]*z+self.chunks.area[chunk_id]*y]=(
#                         x + y + z if int(glm.simplex(glm.vec3(x, y, z) * 0.1) + 1) else 0
#                     )

# def simplexPB(self, chunk_id:int) -> None:
#     """ 3D noise terrain generation using the simplex wave function based on voxel position """
#     if chunk_id <= self.max and chunk_id != -1:
#         localx, localy, localz = self.chunks.location[chunk_id]
#         for x in range(self.chunks.size[chunk_id]):
#             for z in range(self.chunks.size[chunk_id]):
#                 relx = x + localx
#                 relz = z + localz
#                 relheight = int(glm.simplex(glm.vec2(relx, relz) * 0.01) * self.chunks.size[chunk_id]+self.chunks.size[chunk_id])
#                 localheight = min(relheight - localy, self.chunks.size[chunk_id])
#                 for y in range(int(localheight)):
#                     rely = y + localy
#                     self.chunks.voxels[chunk_id][x+self.chunks.size[chunk_id]*z+self.chunks.area[chunk_id]*y]=rely+1
