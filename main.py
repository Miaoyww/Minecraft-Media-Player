# -- coding=utf-8 -- #

from numpy import array
from tqdm import tqdm
import multiprocessing as mp
import logging
import json
import sys
import cv2
import os


def exists_path(path: str) -> str:
    if not os.path.exists(path):
        os.mkdir(path)
        logging.info(f"创建函数文件夹{path}")
    return path


def creat_function_file(video_path: str, function_name: str):
    function_path = "./functions"
    function_path_for_video = f"./functions/{video_path.split('/')[-1].split('.')[:-1][0]}"
    exists_path(function_path)
    function_all_path = exists_path(function_path_for_video)  # 对于每个视频的总函数文件夹
    data_path = exists_path(f"{function_all_path}/data")

    minecraft_path = exists_path(f"{data_path}/minecraft")
    exists_path(f"{data_path}/{function_name}")
    functions_path = exists_path(f"{data_path}/{function_name}/functions")

    minecraft_tags_path = exists_path(f"{minecraft_path}/tags")
    minecraft_functions_path = exists_path(f"{minecraft_tags_path}/functions")
    global function_frames_path
    function_frames_path = exists_path(f"{functions_path}/frames")
    global function_main_path
    function_main_path = exists_path(f"{functions_path}/main")
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
                ":frames/frame_0_info'} \n")
            w.writelines(
                "execute as @a at @s if score @s use matches 1.. run scoreboard players set @s use 0 \n")


def play_function(functions_path: str, function_name: str, fps: int, processed_frames: int):
    with open(functions_path + "/play.mcfunction", "w", encoding="utf-8") as w:
        for i in range(processed_frames):
            time = int(20 / (fps / FRAME_INTERVAL)) * i
            w.writelines(
                f"execute as @e[tag=screen] at @s if score time time matches {time} run function {function_name}:frames/frame_{i}_info \n")


# 将帧信息写到函数中
def write_frame_info(frame: array, path: str, count: int):
    try:
        frame = frame[::-1]
        # 将图像翻转,因为图像的像素点是从上往下排列的
        # 常规的for loop会输出一个反转的图像
        with open(path.format(count), "w") as w:
            for height, frame_item in enumerate(frame):
                for width, color_item in enumerate(frame_item):
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

                    # width 于 height 前后都可以修改
                    # 前面的数可以更改图像的位置
                    # 后面的数可以更改图像的显示大小
                    # 同时, 0.25这个数也是可以更改的, 它是像素点的大小
                    w.writelines(
                        f"particle minecraft:dust {red} {green} {blue} 0.25 ~{1 + (width / 25)} ~{1 + (height / 25)} ~ 0 0 0 0 1 force \n"
                    )
    except KeyboardInterrupt:
        sys.exit(0)


def video(video_path: str):
    capture = cv2.VideoCapture(video_path)
    fps = capture.get(cv2.CAP_PROP_FPS)  # 获取视频帧率
    total_frame = capture.get(cv2.CAP_PROP_FRAME_COUNT)  # 获取视频总帧数
    video_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)  # 获取视频的宽
    video_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 获取视频的高
    count = 0  # 总共写出的帧数
    frame_interval_count = 0  # 现在写正在写的帧数
    processed_frames = int(total_frame // FRAME_INTERVAL)
    function_name = str.lower(video_path.split('/')[-1].split('.')[:-1][0])
    logging.info(f"当前视频的名称是{video_path.split('/')[-1].split('.')[:-1][0]}")
    logging.info(f"当前视频的宽高是{video_width}x{video_height}")
    logging.info(f"当前视频的帧数是{total_frame}")
    logging.info(f"当前视频的帧率是{fps}")
    logging.info(f"当前以每{FRAME_INTERVAL}帧输出一个文件")
    logging.info(f"共是需要处理{processed_frames}个文件")

    pool = mp.Pool(POOL_PROCS)
    creat_function_file(video_path, function_name)

    if capture.isOpened():
        ret, frame = capture.read()
    else:
        ret = False
    process_bar = tqdm(total=processed_frames, desc="正在处理", unit="帧")
    # 用于更新进度条
    update_bar = lambda *args: process_bar.update()
    while ret:
        ret, frame = capture.read()
        if frame_interval_count % FRAME_INTERVAL == 0:
            global function_frames_path
            pool.apply_async(write_frame_info, (frame, function_frames_path + "/frame_{0}_info.mcfunction", count),
                             callback=update_bar)
            count += 1
        frame_interval_count += 1
    pool.close()
    pool.join()
    load_function(function_main_path, function_name, True, processed_frames)
    tick_function(function_main_path, function_name, True)
    play_function(function_main_path, function_name,
                  fps, processed_frames, FRAME_INTERVAL)


def image(image_path: str):
    img = cv2.imread(image_path)
    # opencv读取的图像是BGR格式, 需要转换为RGB格式以便程序运行
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width, channel = img.shape
    logging.info(f"当前图片的宽高是{width}x{height}")
    if height * width > 10000:
        # 若图片太大, 无论电脑性能的高低, 都会卡死
        logging.info(f"图片太大, 建议缩小图片, 当前处理像素为{height * width}")
        logging.info("是否继续处理？(y/n)")
        flag = str.lower(input())
        if flag == "y":
            pass
        else:
            return
    creat_function_file(image_path, str.lower(
        image_path.split('/')[-1].split('.')[:-1][0]))
    write_frame_info(img, function_frames_path + "/frame_0_info.mcfunction", 0)
    load_function(function_main_path, str.lower(
        image_path.split('/')[-1].split('.')[:-1][0]), False)
    tick_function(function_main_path, str.lower(
        image_path.split('/')[-1].split('.')[:-1][0]), False)
    logging.info(f"图片处理完成")


def main(args):
    if args[1].split('.')[-1] == "mp4":
        video(args[1])
    elif args[1].split('.')[-1] == "png" or args[1].split('.')[-1] == "jpg":
        image(args[1])


if __name__ == "__main__":
    # 不要动
    function_frames_path: str
    function_main_path: str
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    ###

    # 图片设置
    PIXEL_SIZE: int = 0.25  # 像素点的大小, 最大为1
    PIXEL_INTERVAL: int = 25  # 每像素点的间隔
    # 视频设置
    FRAME_INTERVAL: int = 15  # 每帧的间隔, 注意, 这个值必须是能被视频帧数整除的值
    # 性能设置
    POOL_PROCS: int = 10  # 线程池的最大线程数, 可以根据电脑性能自行修改

    try:
        main(sys.argv)
        logging.info("结束")
    except KeyboardInterrupt:
        logging.error("进程终止")
        sys.exit(0)
