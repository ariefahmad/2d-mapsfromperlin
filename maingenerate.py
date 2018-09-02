import utils
from PIL import Image

if __name__ == '__main__':
    mapper = utils.map_generator_base()
    image = Image.new("RGB", (mapper.map_size, mapper.map_size))

    mapper.full_generate()

    for x in range(0, mapper.map_size):
        for y in range(0, mapper.map_size):
            image.putpixel((x, y), mapper.colour_map[x][y].make_tuple())

    image.save("generated.png")
    print("Map has been generated! \n")
