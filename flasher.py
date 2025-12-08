import os,sys

class Flasher:
    """
    Interact with xfel,transfer firmware to device.
    """
    def __init__(self):
        self.config = {}

    # exec configs
    def generate_config(self, path) -> None:
        """
        Execute the config file to get xfel config.

        :param path: path to the config file.
        :type path: str
        """
        dict_globals = {}
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code,dict_globals)
        self.config = dict_globals["fel"]()
        del dict_globals
        return
 
    def generate_summary(self) -> str:
        """
        Generate summary of config loaded.
        
        :return: human readable summary string
        :rtype: str
        """
        d = self.config
        s = "\n"
        if d["erase_nand"]:
            s += "擦除闪存: 是\n"
            s += f"擦除大小: {str(d["erase_size"]//1048576)} MB\n"
        s += "\n将写入的数据:\n"
        if d["splwrite"] != []:
            s += "spl引导:\n"
            s += "    地址    长度    文件名\n"
            for w in d["splwrite"]:
                s += f"    {hex(w[1])}    {w[0]}    {w[2]}\n"
        if d["write"] != []:
            s += "固件:\n"
            s += "    地址          文件名\n"
            for w in d["write"]:
                s += f"    {hex(w[0])}    {w[1]}\n"
        return s
    
    def exec_cmd(self,cmd: str) -> None:
        """
        execute xfel command for windows users and linux大佬.
        
        :param cmd: command
        :type cmd: str
        """
        try:
            if os.name == "nt":
                os.system(f"xfel.exe {cmd}")
            elif os.name == "posix":
                os.system(f"xfel {cmd}")
        except Exception as e:
            print(f"错误: {e}")
            sys.exit(1)

    def download_firmware(self) -> None:
        """
        Let's rock'n'roll
        """
        d = self.config
        try:
            if d["erase_nand"]:
                print("擦除闪存...")
                self.exec_cmd(f"spinand erase 0 {str(d["erase_size"])}")
            if d["splwrite"] != []:
                print("写入spl引导...")
                for w in d["splwrite"]:
                    print(f"写入{w[2]}")
                    self.exec_cmd(f"spinand splwrite {str(w[0])} {str(w[1])} {w[2]}")
            if d["write"] != []:
                print("写入固件...")
                for w in d["write"]:
                    print(f"写入{w[1]}")
                    self.exec_cmd(f"spinand write {str(w[0])} {w[1]}")
        except Exception as e:
            print(f"烧录失败:{e}")
            print("设备目前无法启动，请重新进入fel进行一次成功的烧录")


