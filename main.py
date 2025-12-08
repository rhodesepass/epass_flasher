import sys,os

BIN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "bin"))
os.environ["PATH"] += os.pathsep + BIN_PATH

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

def main():
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
