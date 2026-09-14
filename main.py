import nbtlib, dithering, os
from nbtlib.tag import Compound, ByteArray, Int, List, String, Byte # bool values are converted to byte when saving
import numpy as np
from PIL import Image

B_TRUE = Byte(1)
B_FALSE = Byte(0)

image_path = r"D:\Blender\Projects\Output\grassBlockPirouetteFrames\f{:0>4d}.png"
image_frame_range = (1, 13)

result_path = 'result'
data_version = 4903 # JE 26.2
map_id_from = 1000

palette_path = 'palette.txt'
palette = np.zeros((244, 3), np.uint8)
transparent_thres = 127 # <=

def read_palette():
    with open(palette_path, 'r', encoding = 'utf-8') as palette_file:
        palette_lines = [_x.replace('\n', '') for _x in palette_file.readlines()]
    for idx, line in enumerate(palette_lines):
        if not line: pass
        cval = int(line, 16)
        r, g, b = [(cval >> _d) & 0xff for _d in (16, 8, 0)]
        palette[(idx << 2) | 2] = (r, g, b)
        palette[(idx << 2) | 0] = (r * 180 // 255, g * 180 // 255, b * 180 // 255)
        palette[(idx << 2) | 1] = (r * 220 // 255, g * 220 // 255, b * 220 // 255)
        palette[(idx << 2) | 3] = (r * 135 // 255, g * 135 // 255, b * 135 // 255)

def rgb_to_palette(im: np.ndarray) -> np.ndarray:
    palette_ = palette.astype(np.uint32)
    palette_enc = (palette_[..., 0] << 16) | (palette_[..., 1] << 8) | palette_[..., 2]
    palette_order = np.argsort(palette_enc) # Since palette colors do not repeat, unstable sorting is OK
    palette_enc_sorted = palette_enc[palette_order]

    im_ = np.ascontiguousarray(im).astype(np.uint32, copy = False)
    im_enc = (im_[..., 0] << 16) | (im_[..., 1] << 8) | im_[..., 2]

    pos = np.searchsorted(palette_enc_sorted, im_enc)
    np.clip(pos, 0, len(palette_enc_sorted) - 1, out = pos)
    im_index = palette_order[pos]

    return np.where(im[..., 3] <= transparent_thres, 0, im_index + 4).astype(np.uint8) # This operation is specific to Minecraft map data

if __name__ == '__main__':
    # last_id.dat
    last_id = nbtlib.File(
        Compound({
            'data': Compound({'map': Int(map_id_from + image_frame_range[1] - image_frame_range[0] - 1)}),
            'DataVersion': Int(data_version)
        }),
        gzipped = True
    )
    with open(os.path.join(result_path, 'last_id.dat'), 'wb') as last_id_dat:
        last_id.write(last_id_dat)
    # make the map data
    read_palette()
    for idx in range(image_frame_range[0], image_frame_range[1]):
        im = np.array(Image.open(image_path.format(idx)).convert('RGBA').resize((128, 128), Image.Resampling.NEAREST))
        im_dither = dithering.dither(im, 'floyd_steinberg', palette = palette)
        im_index = rgb_to_palette(im_dither)
        map_data = nbtlib.File(
            Compound({
                'data': Compound({
                    'banners': List(), # No banners
                    'colors': ByteArray(im_index.flatten()),
                    'dimension': String('minecraft:overworld'),
                    'frames': List(), # No item frame
                    'locked': B_TRUE,
                    'scale': Byte(0),
                    'trackingPosition': B_FALSE,
                    'unlimitedTracking': B_FALSE,
                    'xCenter': Int(1048576),
                    'zCenter': Int(1048576)
                }),
                'DataVersion': Int(data_version)
            }),
            gzipped = True
        )
        with open(os.path.join(result_path, f'{idx + map_id_from}.dat'), 'wb') as map_data_dat:
            map_data.write(map_data_dat)
