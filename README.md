# minecraft-map-data-gen
Converts an image sequence to Minecraft map data for in-game use.

Compatible with Minecraft 26.2. *(This program is not responsible for the datapack part btw)*

## How to use

1. Install required modules, including `nbtlib`, `dithering`, `numpy` and `pillow`(PIL). All of these should be available via `pip` command.

2. Fine the `image_path` variable and change it according to your files. For an image sequence with continuous integer namings such as `D:/im/frame_00xx.png`, you can write it as `r'D:/im/frame_{:0>4d}.png'`, with the `{:0>4d}` meaning that the frame index will be added leading 0's into a length of 4.

3. Right below `image_path`, there's a `image_frame_range` variable, change it into `(minimum, maximum + 1)`. E.g. your file is from `frame_0100.png` to `frame_0167.png`, then the tuple should be (100, 168).

4. Now the program should be OK to run, and when it finishes, all the .dat files you need should be under a `result` folder. Copy everything inside into the `.minecraft/saves/<save name>/data/minecraft/maps` folder (create one if not exist).

5. Open that save and give yourself a map with command: `/give @s minecraft:filled_map[minecraft:map_id=XXXX]`, with XXXX changed to one of the .dat file name numbers. If you see the image, you're done!
