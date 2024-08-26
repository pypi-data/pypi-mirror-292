from ..globs import glm, np
from ..resource.zvxbank import zvxchunkbank

class zvxterraingen:
    def __init__(self, noise_function, scale=0.1, height_scale=48):
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

def simple_fill(vec:glm.vec2) -> float:
    """ simple zvx terrain generation (fills an entire chunk) """
    return 1.0

def ridged_noise(vec: glm.vec2) -> float:
    """ Generates ridged noise for mountainous terrain """
    noise_value = glm.simplex(vec)
    ridged_value = 1.0 - abs(noise_value)
    return ridged_value ** 2

def plateau_noise(vec: glm.vec2) -> float:
    """ Generates plateau noise for flat terrain with small hills """
    noise_value = glm.simplex(vec * 0.5)
    plateau_value = glm.smoothstep(0.4, 0.6, noise_value)
    return plateau_value

def hybrid_terrain(vec: glm.vec2) -> float:
    """ Combines multiple noise functions for varied terrain """
    simplex_value = glm.simplex(vec * 0.1)
    ridged_value = ridged_noise(vec * 0.2) * 0.5
    return simplex_value + ridged_value

def octave_noise(vec: glm.vec2, octaves=4, persistence=0.5) -> float:
    """ Generates terrain with multiple noise layers (octaves) """
    frequency = 1.0
    amplitude = 1.0
    max_value = 0.0
    total = 0.0
    for _ in range(octaves):
        total += glm.simplex(vec * frequency) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= 2.0
    return total / max_value

def biome_noise(vec: glm.vec2) -> float:
    """ Generates terrain based on different biomes """
    biome_selector = glm.simplex(vec * 0.01)
    if biome_selector < -0.23:
        return plateau_noise(vec)
    elif biome_selector < 0.23:
        return ridged_noise(vec)
    else:
        return octave_noise(vec)

def heightmap_noise(vec: glm.vec2, heightmap: np.ndarray) -> float:
    """ Generates terrain using a heightmap """
    heightmap_value = heightmap[int(vec.x % heightmap.shape[0]), int(vec.y % heightmap.shape[1])]
    return heightmap_value / 255.0
