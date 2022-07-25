import logging
import json
import sys
import os



class Mmp:
    @staticmethod
    def exists_path(path: str) -> str:
        if not os.path.exists(path):
            os.mkdir(path)
            logging.info(f"创建函数文件夹{path}")
        return path

    @staticmethod
    def creat_function_file(video_path: str, function_name: str):
        function_path = "./functions"
        function_path_for_video = f"./functions/{str.lower(video_path.split('/')[-1].split('.')[:-1][0])}"
        Mmp.exists_path(function_path)
        function_all_path = Mmp.exists_path(function_path_for_video)  # 对于每个视频的总函数文件夹
        data_path = Mmp.exists_path(f"{function_all_path}/data")

        minecraft_path = Mmp.exists_path(f"{data_path}/minecraft")
        Mmp.exists_path(f"{data_path}/{function_name}")
        functions_path = Mmp.exists_path(f"{data_path}/{function_name}/functions")

        minecraft_tags_path = Mmp.exists_path(f"{minecraft_path}/tags")
        minecraft_functions_path = Mmp.exists_path(f"{minecraft_tags_path}/functions")
        function_frames_path = Mmp.exists_path(f"{functions_path}/frames")
        function_main_path = Mmp.exists_path(f"{functions_path}/main")
        pack_info = {
            "pack": {
                "pack_format": 8,
                "description": "made by Miaomiaoywww"
            }
        }
        load_info = {
            "values": [
                f"{function_name}:main/load"
            ]
        }
        tick_info = {
            "values": [
                f"{function_name}:main/tick"
            ]
        }
        with open(function_path_for_video + "/pack.mcmeta", "w") as w:
            w.write(json.dumps(pack_info, sort_keys=True,
                               indent=4, separators=(',', ':')))
        with open(minecraft_functions_path + "/load.json", "w") as w:
            w.write(json.dumps(load_info, sort_keys=True,
                               indent=4, separators=(',', ':')))
        with open(minecraft_functions_path + "/tick.json", "w") as w:
            w.write(json.dumps(tick_info, sort_keys=True,
                               indent=4, separators=(',', ':')))
        return function_main_path, function_frames_path

    @staticmethod
    def load_function(functions_path: str, function_name: str, process_video: bool = False, processed_frames: int = 0):
        with open(functions_path + "/load.mcfunction", "w", encoding="utf-8") as w:
            w.writelines("tellraw @a {\"text\": \"" +
                         function_name + "数据包已加载成功\"} \n")
            if process_video:
                w.writelines(
                    "tellraw @a {\"text\": \"共有" + str(processed_frames) + "帧可播放\"} \n")
            w.writelines(
                "tellraw @a ["
                "{\"text\": \"使用此\"},"
                "{\"text\": \"胡萝卜钓竿\",\"color\": \"green\",\"clickEvent\": {\"action\": \"run_command\",\"value\":"
                "\"/give @s minecraft:carrot_on_a_stick{'trigger':'tick'}\"}},{\"text\": \"可以生成屏幕\"}"
                "] \n"
            )
            w.writelines(
                "scoreboard objectives add use minecraft.used:minecraft.carrot_on_a_stick \n")
            if process_video:
                w.writelines("scoreboard objectives add play dummy \n")
                w.writelines("scoreboard objectives add time dummy \n")

    @staticmethod
    def tick_function(functions_path: str, function_name: str, process_vidoe: bool = False):
        with open(functions_path + "/tick.mcfunction", "w", encoding="utf-8") as w:
            if process_vidoe:
                w.writelines(
                    "execute as @a at @s if score @s use matches 1.. "
                    "run summon minecraft:armor_stand ~ ~ ~ {Invisible:1, Marker:1, Tags:[screen]} \n")
                w.writelines(
                    "execute as @a at @s if score @s use matches 1.. run scoreboard players set @s use 0 \n")
                w.writelines(
                    "execute if entity @e[tag=screen] run scoreboard players set play play 1 \n")
                w.writelines(
                    "execute if score play play matches 1.. run scoreboard players add time time 1 \n")
                w.writelines(
                    f"execute as @e[tag=screen] at @s run function {function_name}:main/play \n")
            else:
                w.writelines(
                    "execute as @a at @s if score @s use matches 1.. "
                    "run setblock ~ ~ ~ minecraft:command_block{Command: \'function " + function_name +
                    ":frames/frames_0_info'} \n")
                w.writelines(
                    "execute as @a at @s if score @s use matches 1.. run scoreboard players set @s use 0 \n")

    @staticmethod
    def play_function(functions_path: str, function_name: str, fps: int, processed_frames: int, frame_interval: int):
        with open(functions_path + "/play.mcfunction", "w", encoding="utf-8") as w:
            for i in range(processed_frames):
                time = int(20 / (fps / frame_interval)) * i
                w.writelines(
                    f"execute as @e[tag=screen] at @s if score time time matches {time} run "
                    f"function {function_name}:frames/frames_{i}_info \n")

    @staticmethod
    def process_color(color_item: list, writer, pixel_size: float,
                      pixel_interval: int, width: int = 0, height: int = 0):

        # 要求不保留详细的颜色信息,会占用大量内存
        red = str(float(color_item[0]) / 255)
        if len(red) >= 5:
            red = red[:5]
        green = str(float(color_item[1]) / 255)
        if len(green) >= 5:
            green = green[:5]
        blue = str(float(color_item[2]) / 255)
        if len(blue) >= 5:
            blue = blue[:5]
        x = str(1 + (width / pixel_interval))
        if len(x) >= 5:
            x = x[:5]
        y = str(1 + (height / pixel_interval))
        if len(y) >= 5:
            y = y[:5]

        writer.writelines(
            f"particle minecraft:dust {red} {green} {blue} {pixel_size} "
            f"~{1 + (width / pixel_interval)} ~{1 + (height / pixel_interval)} ~ "
            f"0 0 0 0 1 force \n"
        )

    @staticmethod
    # 将帧信息写到函数中
    def write_frame_info(frame, path: str, count: int, pixel_size: float, pixel_interval: int,
                         process_video: bool = False):
        try:
            path = path + f"/frames_{count}_info.mcfunction"
            with open(path, "w") as w:
                if process_video:
                    frame = frame[::-1]
                    for height, frame_item in enumerate(frame):
                        for width, color_item in enumerate(frame_item):
                            Mmp.process_color(color_item, w, pixel_size, pixel_interval, width, height)
                else:
                    image_width = frame.size[0]
                    image_height = frame.size[1]
                    img = frame.convert("RGB")
                    for wid in range(image_width):
                        for hei in range(image_height):
                            r, g, b = img.getpixel((wid, hei))
                            color_item = [r, g, b]
                            Mmp.process_color(color_item, w, pixel_size, pixel_interval, wid, abs(hei - image_height))
        except KeyboardInterrupt:
            sys.exit(0)
