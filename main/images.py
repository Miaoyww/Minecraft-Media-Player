from PIL import Image
from mmp import Mmp
import logging
import sys


def image(image_path: str):
    img = Image.open(image_path)
    height, width = img.size
    logging.info(f"当前图片的宽高是{width}x{height}")
    if height * width > 10000:
        # 若图片太大, 无论电脑性能的高低, 在加载图片时都会卡死
        logging.info(f"图片太大, 建议缩小图片, 当前处理像素为{height * width}")
        logging.info("是否继续处理？(y/n)")
        flag = str.lower(input())
        if flag == "y":
            pass
        else:
            return
    function_main_path, function_frames_path = Mmp.creat_function_file(image_path, str.lower(
        image_path.split('/')[-1].split('.')[:-1][0]))
    Mmp.write_frame_info(
        img,
        function_frames_path,
        0,
        pixel_size=PIXEL_SIZE, pixel_interval=PIXEL_INTERVAL)
    Mmp.load_function(function_main_path, str.lower(
        image_path.split('/')[-1].split('.')[:-1][0]), False)
    Mmp.tick_function(function_main_path, str.lower(
        image_path.split('/')[-1].split('.')[:-1][0]), False)
    logging.info(f"图片处理完成")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    PIXEL_SIZE: float = 0.25  # 像素点的大小, 最大为1
    PIXEL_INTERVAL: int = 25  # 每像素点的间隔

    try:
        image(sys.argv[1])
        logging.info("结束")
    except KeyboardInterrupt:
        logging.error("进程终止")
        sys.exit(0)
