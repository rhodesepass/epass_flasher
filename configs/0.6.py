from pydevicetree import Devicetree
from pydevicetree.ast import *
import os,sys,subprocess
import re

summary = ""

# Configuration for 0.5 version device

# xfel configurations

# xfel spinand erase 0 0x8000000
# xfel spinand splwrite 1024 0 u-boot-sunxi-with-spl.bin
# xfel spinand write 0x20000 u-boot.img
# xfel spinand write 0x100000 devicetree-0.3.dtb
# xfel spinand write 0x120000 zImage-0.3
# xfel spinand write 0x680000 ubi.img

xfel_config = {
    "erase_nand": True,
    "erase_size": int(0x8000000),
    "splwrite": [
        [1024, 0, "firmware/u-boot-sunxi-with-spl.bin"]
    ],
    "write": [
        [0x20000, "firmware/u-boot.img"],
        [0x100000, "devicetree.dtb"], # generate at runtime
        [0x120000, "firmware/zImage"],
        [0x680000, "firmware/ubi.img"]
    ]
}

# put devicetree path here
dt_file = "firmware/devicetree-0.6.dts"

# delete_node path nodename
# insert_node path node_path
# delete_prop path propname
# insert_prop path propname propvalue

# command will be executed in order as listed in patchlist
# must delete nodes/properties before inserting new ones with same name

# ["delete_node", "/soc/spi@1c05000", "spi-nand@0"]
# ["insert_node", "/soc/spi@1c05000", "dts/append/spi_node.dtsa"]
# ["delete_prop", "/soc/spi@1c05000", "status"]
# ["insert_prop", "/soc/spi@1c05000", "status", StringList(["okay"])] like this


patchlist = [
]

#老王
# 老王也使用瀚彩初始化。
def laowang_patch() -> None:
    
    patchlist_laowang = [
    ["insert_prop","/soc/lcd-controller@1c0c000","srgn,swap-b-r",None],
    ["delete_node","/","st7701initseq"],
    ["insert_node","/","dts/st7701_initseq/st7701_hannstar.dtsa"],
    #V0.5 workaround
    ["delete_prop","/st7701initseq","cs-gpios"],
    ["insert_prop","/st7701initseq","cs-gpios",CellArray([LabelReference("pio"),4,11,0])],
    ]

    global patchlist,summary
    print("您已选择老王屏幕")
    summary = "屏幕型号: " + "老王" + "\n"
    for item in patchlist_laowang:
        patchlist.append(item)

#翰彩
def hannstar_patch() -> None:

    patchlist_hannstar = [
    ["delete_node","/","st7701initseq"],
    ["insert_node","/","dts/st7701_initseq/st7701_hannstar.dtsa"],
    #V0.5 workaround
    ["delete_prop","/st7701initseq","cs-gpios"],
    ["insert_prop","/st7701initseq","cs-gpios",CellArray([LabelReference("pio"),4,11,0])],
    ]

    global patchlist,summary
    print("您已选择翰彩屏幕")
    summary = "屏幕型号: " + "翰彩" + "\n"
    for item in patchlist_hannstar:
        patchlist.append(item)

#京东方
def boe_patch() -> None:

    patchlist_boe = [
    ["delete_node","/","st7701initseq"],
    ["insert_node","/","dts/st7701_initseq/st7701_BOE.dtsa"],
    #V0.5 workaround
    ["delete_prop","/st7701initseq","cs-gpios"],
    ["insert_prop","/st7701initseq","cs-gpios",CellArray([LabelReference("pio"),4,11,0])],
    ]

    global patchlist,summary
    print("您已选择京东方屏幕")
    summary = "屏幕型号: " + "京东方" + "\n"
    for item in patchlist_boe:
        patchlist.append(item)



screen_models = [
    "老王",
    "翰彩",
    "京东方",
]

screen_models_cb = [
    laowang_patch,
    hannstar_patch,
    boe_patch,
]

# will be called devicetree patcher
# will be called first
def patch():
    global patchlist,summary
    # put screen selection logic here
    # simply append to patchlist based on selection
    print("您已选择0.6版本设备")
    print("准备修补设备树...")


    print("请选择屏幕型号:")
    cnt = 0
    for i in screen_models:
        cnt += 1
        print(f"{cnt}: {i}")
    while True:
        selection = int(input("输入需要的屏幕型号前的序号: "))
        try:
            screen_models_cb[selection-1]()
            break
        except IndexError:
            print("无效输入，请重新输入。")


    print("获取闪存大小...")
    # 执行命令并捕获输出
    try:
        if os.name == "nt":
            result = subprocess.run(["xfel.exe", "spinand"], capture_output=True, text=True, check=False)
        elif os.name == "posix":
            result = subprocess.run(["xfel", "spinand"], capture_output=True, text=True, check=False)
        # jpython shall not get here.
    except Exception as e:
        print("获取失败,使用默认参数 ", e)
        summary += "闪存大小: 默认\n"
        return patchlist,dt_file,summary
    # 获取标准输出并提取闪存大小（例如: "Found spi nand flash 'W25N01GV' with 134217728 bytes"）
    output = result.stdout or ""
    m = re.search(r"Found spi nand flash '.*' with (\d+) bytes", output)
    if m == None:
        print("获取输出为:",output)
        raise Exception("错误:获取不到闪存大小,请检查设备是否已连接,是否处于FEL模式!!!")
    flash_size = int(m.group(1))
    xfel_config["erase_size"] = flash_size
    if flash_size is not None:
        summary += f"闪存大小: {str(flash_size//1048576)} MB\n"
        rootfs_size = flash_size - int(0x620000)
        patchlist.append(["delete_prop",
                          "/soc/spi@1c05000/spi-nand@0/partitions/partition@3",
                          "reg"])
        patchlist.append(["insert_prop",
                          "/soc/spi@1c05000/spi-nand@0/partitions/partition@3",
                          "reg",
                           CellArray([int(0x620000), rootfs_size])])
        
    input_usb = input("是否启用USB高速模式？(输入y启用 回车关闭): ").strip().lower()
    if input_usb == 'y':
        patchlist.append(["insert_prop","/soc/usb@1c13000","srgn,usb-hs-enabled",None])
        summary += "USB高速模式: 启用\n"
    else:
        summary += "USB高速模式: 关闭\n"

    return patchlist,dt_file,summary
    
# will be called by flasher
# will be called last
def fel():
    print("读取FEL配置...")
    return xfel_config