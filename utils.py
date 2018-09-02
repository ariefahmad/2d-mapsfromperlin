import numpy as np
import random
import tqdm
from noise import snoise2  # simplex noise for 2d points

class colour:
    """
    Colours for the map
    """

    def __init__(self, r = 0., g = 0., b = 0., a =1.):
        """
        setting r, g, b & a (opacity) default values
        """
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def make_tuple(self):
        """
        ordering rgb
        """
        return (int(self.r), int(self.g), int(self.b))

    def set_colour(self, r, g, b):
        """
        change colour to specified values
        """
        self.r = r
        self.g = g
        self.b = b

    def copy_colour(self, spec_colour):
        """
        copy from known colour
        """
        self.set_colour(spec_colour.r, spec_colour.g, spec_colour.b)

class vector:
    """for maths operations"""
    def __init__(self, x1 = 0., y1 = 0., x2 = 0., y2 = 0.):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def dist_calc(self):
        x = (self.x1 - self.x2) ** 2
        y = (self.y1 - self.y2) ** 2
        return np.sqrt(x + y)

    def norm_dist_calc(self, size = 256):
        return self.dist_calc() / size

class map_generator_base:

    def __init__(self, map_size = 2048):
        self.map_size = map_size  # pixels
        self.map_centre = (self.map_size * 0.5, self.map_size * 0.5)
        self.height_map = [[0] * self.map_size for x in range(0, self.map_size)]
        self.colour_map = [[colour() for j in range(0, self.map_size)] for i in range(0, self.map_size)]
        self.paper_colour = colour(102, 255, 153)
        self.water_colour = colour(51, 153, 255)

        self.perlin_scale = 0.0025
        self.perlin_colourscale = 0.025
        self.perlin_waterscale = 0.10
        self.perlin_offset = random.random() * self.map_size
        self.land_threshold = 0.1
        self.random_colour_range = 10

        self.progress_bar = tqdm.tqdm(total = self.map_size ** 2)
        self.progress_bar.clear()

        self.x = 0
        self.y = 0

    def generate(self, x, y):
        """
        Function to procedurally generate map;
        Only 2 terrains; land & water
        If above a certain elevation (land_threshold), make land
        & if below, make water
        """

        perlin_base = (snoise2(float(x) * self.perlin_scale, float(y) * self.perlin_scale,
                        octaves = 8, persistence = 0.5, lacunarity = 2.,
                        repeatx = self.map_size, repeaty = self.map_size, base = self.perlin_offset) + 1.) / 2.

        # calculate pixel height
        distance1 = vector(x, y, self.map_centre[0], self.map_centre[1]).norm_dist_calc(self.map_size)

        perlin_base -= distance1 ** 0.5
        if perlin_base <= 0:
            perlin_base = 0

        self.height_map[x][y] = perlin_base

        # generate land
        if self.height_map[x][y] > self.land_threshold:
            perlin_detail = (snoise2(float(x) * self.perlin_scale, float(y) * self.perlin_scale,
                            octaves = 12, persistence = 0.8, lacunarity = 2.,
                            repeatx = self.map_size, repeaty = self.map_size, base = self.perlin_offset) + 1.) / 2.

            norm_height = (perlin_detail - self.land_threshold) ** 3

            noise_value = (snoise2(float(x) * self.perlin_colourscale, float(y) * self.perlin_colourscale,
                            octaves = 2, persistence = 0.5, lacunarity = 2.,
                            repeatx = self.map_size, repeaty = self.map_size, base = self.perlin_offset) + 1.) / 2.
            random_colour_offset = (random.random() - 0.5) * 8 + 24. * noise_value + norm_height * 256.

            r = self.paper_colour.r + random_colour_offset
            g = self.paper_colour.g + random_colour_offset
            b = self.paper_colour.b + random_colour_offset
            self.colour_map[x][y].set_colour(r, g, b)

        # generate water
        else:
            norm_height = self.height_map[x][y]
            if norm_height < 0:
                norm_height = 0

            noise_value = (snoise2(float(x) * self.perlin_waterscale, float(y) * self.perlin_waterscale,
                            octaves = 2, persistence = 0.5, lacunarity = 2.,
                            repeatx = self.map_size, repeaty = self.map_size, base = self.perlin_offset) + 1.) / 2.

            random_colour_offset = (random.random() - 0.5) * 4. + 12. * noise_value + norm_height * 96.

            r = self.water_colour.r + random_colour_offset
            if r < 0:
                r = 0
            g = self.water_colour.g + random_colour_offset
            if g < 0:
                g = 0
            b = self.water_colour.b + random_colour_offset
            if b < 0:
                b = 0

            self.colour_map[x][y].set_colour(r, g, b)

        self.progress_bar.update(1)  # update that ting

    def full_generate(self):
        """
        just generate through all space
        """
        [[self.generate(x, y) for x in range(0, self.map_size)] for y in range(0, self.map_size)]
