import os,sys    

class Interact:
    """
    handle user interaction for selecting configs.

    """
    def __init__(self):
        self.summary = ""

    def log_summary(self, input_str: str) -> None:
        """
        Append input_str to the summary inside instance.
        
        :param input_str: summary generated from other module.
        :type input_str: str
        """
        self.summary += input_str

    def get_config(self) -> str:
        """
        Let user choose a config file from configs folder.
        :return: path to the chosen config file.
        :rtype: str
        """
        configs = os.listdir("configs")
        idx = 0
        print("请选择设备版本:")
        for config in configs:
            idx += 1
            print(f"{idx} : {config[:-3]}")
        choice = input("输入设备版本: ")
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(configs):
            print("无效的设备版本")
            sys.exit(1)
        else:
            self.summary += "设备版本: " + configs[int(choice) - 1][:-3] + "\n"
            return os.path.abspath("configs/" + configs[int(choice) - 1])
        
    def show_summary(self):
        """
        Print summary from summary
        """
        print("以下是选择的设备配置信息，请仔细核对，错误配置可能导致无法启动和功能异常")
        print("----------------------------------------")
        print(self.summary)
        print("----------------------------------------")
        print("数据被写入/覆盖后无法恢复，请提前备份")
        input("确认无误后按回车键继续，烧录将立即开始，若有误请关闭程序重新运行: ")
        
