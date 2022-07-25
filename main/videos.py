import multiprocessing as mp
from tqdm import tqdm
from mmp import Mmp
import logging
import sys
import cv2


def update_bar(process_bar):
    process_bar.update()


def video(video_path: str, frame_interval: int, pool_procs: int, pixel_size: float, pixel_interval: int):
    capture = cv2.VideoCapture(video_path)
    fps = capture.get(cv2.CAP_PROP_FPS)  # 获取视频帧率
    total_frame = capture.get(cv2.CAP_PROP_FRAME_COUNT)  # 获取视频总帧数
    video_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)  # 获取视频的宽
    video_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 获取视频的高
    count = 0  # 总共写出的帧数
    frame_interval_count = 0  # 现在写正在写的帧数
    processed_frames = int(total_frame // frame_interval)
    function_name = str.lower(video_path.split('/')[-1].split('.')[:-1][0])
    logging.info(f"当前视频的名称是{video_path.split('/')[-1].split('.')[:-1][0]}")
    logging.info(f"当前视频的宽高是{video_width}x{video_height}")
    logging.info(f"当前视频的帧数是{total_frame}")
    logging.info(f"当前视频的帧率是{fps}")
    logging.info(f"当前以每{frame_interval}帧输出一个文件")
    logging.info(f"共是需要处理{processed_frames}个文件")

    pool = mp.Pool(pool_procs)
    function_main_path, function_frames_path = Mmp.creat_function_file(video_path, function_name)

    if capture.isOpened():
        ret, frame = capture.read()
    else:
        ret = False
    process_bar = tqdm(total=processed_frames, desc="正在处理", unit="帧")
    # 用于更新进度条
    while ret:
        ret, frame = capture.read()
        if frame_interval_count % frame_interval == 0:
            pool.apply_async(Mmp.write_frame_info,
                             (frame, function_frames_path, count, pixel_size, pixel_interval, True),
                             callback=update_bar(process_bar))
            count += 1
        frame_interval_count += 1
    pool.close()
    pool.join()
    Mmp.load_function(function_main_path, function_name, True, processed_frames)
    Mmp.tick_function(function_main_path, function_name, True)
    Mmp.play_function(function_main_path, function_name,
                      fps, processed_frames, frame_interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    PIXEL_SIZE: float = 0.1  # 像素点的大小, 最大为1
    PIXEL_INTERVAL: int = 20  # 每像素点的间隔

    FRAME_INTERVAL: int = 3  # 每帧的间隔, 注意, 这个值必须是能被视频帧数整除的值
    POOL_PROCS: int = 10  # 线程池的最大线程数, 可以根据电脑性能自行修改

    try:
        video(sys.argv[1], FRAME_INTERVAL, POOL_PROCS, PIXEL_SIZE, PIXEL_INTERVAL)
        logging.info("结束")
    except KeyboardInterrupt:
        logging.error("进程终止")
        sys.exit(0)
