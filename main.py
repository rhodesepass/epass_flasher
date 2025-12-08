import sys,os,pickle,argparse

BIN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "bin"))
os.environ["PATH"] += os.pathsep + BIN_PATH

from pathlib import Path
from dt_patcher import Patcher
from interact import Interact
from flasher import Flasher
import traceback

header = """
电子通行证烧录程序。
罗德岛工程部 (c)1097
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
烧录将会清除设备内所有数据，请提前备份好资源文件！
请确认你的设备的版本并选择正确的配置文件！
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
.
请按住设备开关旁的按钮（FEL按钮），并打开设备电源，
等待几秒钟后松开FEL按钮，将设备连接上电脑。
"""

def download_with_preset_file(config):
    dt_patcher = config["dt_patcher"]
    flasher = config["flasher"]
    dt_patcher.export_devicetree("devicetree.dts")
    dt_patcher.compile_devicetree("devicetree.dts", "devicetree.dtb")
    flasher.download_firmware()


def check_exist_dtb():
    last_config_path_file = Path("last_config_path")
    last_config = pickle.load(open("last_config_path", "rb"))
    if last_config_path_file.exists():
        print("检测到上次生成的设备树和使用的烧录配置，是否直接使用？")
        print("上次保存的配置:")
        print("----------------------------------------")
        print(last_config["interact"].summary)
        print("----------------------------------------")
        choice = input("输入Y使用已有文件，输入其他任意键重新生成: ")
        if choice.lower() != "y":
            os.remove("last_config_path")
            return
        else:
            print("使用上次保存的设置进行烧录...")
            download_with_preset_file(last_config)
            print("烧录完成！请断开设备电源，拔掉数据线，然后重新上电启动设备。")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description='Epass flasher')
    parser.add_argument('--config_path', help='Path to input config file',default=None)
    args = parser.parse_args()
    if args.config_path is not None:
        last_config = pickle.load(open(args.config_path, "rb"))
        print("量产模式: 已加载配置文件")
        print("上次保存的配置:")
        print("----------------------------------------")
        print(last_config["interact"].summary)
        print("----------------------------------------")
        input("准备好后按下回车键继续，关闭程序退出: ")
        download_with_preset_file(last_config)
        input("烧录完成,断开该设备并插入下一个已进入FEL的设备，准备好后按下回车键继续，关闭程序退出: ")
        while True:
            last_config["flasher"].download_firmware()
            input("烧录完成,断开该设备并插入下一个已进入FEL的设备，准备好后按下回车键继续，关闭程序退出: ")

    check_exist_dtb()

    interact = Interact()
    config_path = interact.get_config()
    

    dt_patcher = Patcher()
    dt_patcher.generate_config(config_path)
    dt_patcher.apply_patches()
    dt_patcher.export_devicetree("devicetree.dts")
    dt_patcher.compile_devicetree("devicetree.dts", "devicetree.dtb")
    interact.log_summary(dt_patcher.summary)

    flasher = Flasher()
    flasher.generate_config(config_path)
    interact.log_summary(flasher.generate_summary())

    interact.show_summary()
    flasher.download_firmware()

    #os.remove("devicetree.dtb")
    pickle.dump({"config_path":config_path,
                 "interact":interact,
                 "dt_patcher":dt_patcher,
                 "flasher":flasher
                 }, open("last_config_path", "wb+"))

    print("烧录完成！请断开设备电源，拔掉数据线，然后重新上电启动设备。")

if __name__ == "__main__":
    try:
        print(header)
        main()
    except Exception as e:
        print("出现错误",e)
        traceback.print_exc()

        pass
    
    print("请按回车键继续.....")
    input()
