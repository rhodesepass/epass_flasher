import os, sys
from typing import Union

from pydevicetree import Devicetree
from pydevicetree.ast import *



class Patcher:
    """
    Patcher class to modify devicetree based on given patches.
    """
    def __init__(self):
        self.summary = ""
        self.tree: Devicetree
        self.patchlist = []

    def get_node(self, path: str) -> Union[Node, None]:
        """
        Get a node by its path from devicetree.

        Returns None if the node does not exist.
        
        :param path: Path to the node.
        :type path: str
        :return: Node at the given path or None.
        :rtype: Node | None
        """

        if path == "/":
            return self.tree.children[0]
        else:
            return self.tree.get_by_path(path)

    def delete_node(self, path: str, nodename: str) -> None:
        """
        Delete a node by its path from devicetree.
        
        :param path: Path to the parent node of the node to be deleted.
        :type path: str
        :param nodename: Name of the node to be deleted.
        :type nodename: str
        """
        print("删除节点...")
        node = self.get_node(path)
        if node is None:
            return
        if nodename.endswith('@0'):
            nodename = nodename[:-2]
        for child in node.children:
            if child.name == nodename:
                node.remove_child(child)
                return

    def insert_node(self, path: str, node_path: str) -> None:
        """
        read a dts file and insert all nodes in dts file into devicetree with given path.

        Will not do anything if the parent node does not exist.
        
        :param path: Path to the parent node of the node to be inserted.
        :type path: str
        :param node_path: Path to the **DTS FILE** containing the node to be inserted.
        :type node_path: str
        """
        print("插入节点...")
        parent = self.get_node(path)
        if parent is None:
            return
        with open(node_path, 'r', encoding='utf-8') as f:
            node_dts = f.read()
        parent.add_child(Devicetree.from_dts(node_dts))
        return

    def delete_prop(self, path: str, propname :str) -> None:
        """
        delete a property by its name from devicetree.
        
        :param path: Path to the node
        :type path: str
        :param propname: Property name
        :type propname: str
        """

        print("删除属性...")
        node = self.get_node(path)
        if node is None:
            return
        idx = 0
        for prop in node.properties:
            if prop.name == propname:
                del node.properties[idx]
                return
            else:
                idx += 1
        return

    def insert_prop(self, path, propname: str, propvalue: PropertyValues):
        """
        Insert a property by its name and value into devicetree.

        Will not do anything if the parent node does not exist.
        
        :param path: Path to the node
        :param propname: Property name
        :type propname: str
        :param propvalue: Property value
        :type propvalue: PropertyValues
        """
        print("插入属性...")
        node = self.get_node(path)
        if node is None:
            return
        if propvalue is None:
            node.properties.append(Property(propname, PropertyValues([])))
        else:
            node.properties.append(Property(propname, propvalue))
        return
   
    # exec configs
    def generate_config(self, path) -> None:
        """
        Execute the config file to get patchlist and devicetree path.

        :param path: path to the config file.
        :type path: str
        """
        dict_globals = {}
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
            exec(code,dict_globals)
        self.patchlist,dt_path,self.summary = dict_globals["patch"]()
        print(f"将运行{len(self.patchlist)}条修补指令")
        del dict_globals
        self.tree = Devicetree.parseFile(dt_path)
        return

    def __remove_duplicate_props(self, node):
        if node.properties is not None or []:
            props = node.properties
            props.reverse()
            seen = []
            new_props = []
            for prop in props:
                name = getattr(prop, 'name', None)
                if name not in seen:
                    new_props.append(prop)
                    seen.append(prop.name)
            new_props.reverse()
            node.properties = new_props
        if node.children is None or []:
            return
        for child in node.children:
            self.__remove_duplicate_props(child)

    # apply configs
    def apply_patches(self):
        """
           apply all patches instructions to devicetree.

           Patches instructions:
           delete_node path nodename
           insert_node path node_path
           delete_prop path propname
           insert_prop path propname propvalue"""
        print("应用修补...")
        self.__remove_duplicate_props(self.tree)
        try:
            for patch in self.patchlist:
                if patch[0] == "delete_node":
                    self.delete_node(patch[1], patch[2])
                elif patch[0] == "insert_node":
                    self.insert_node(patch[1], patch[2])
                elif patch[0] == "delete_prop":
                    self.delete_prop(patch[1], patch[2])
                elif patch[0] == "insert_prop":
                    self.insert_prop(patch[1], patch[2], patch[3])
        except Exception as e:
            print("修补过程中出现错误:", e)
            sys.exit(1)
        return

    def export_devicetree(self, output_file_name):
        """
        Export the patched devicetree to a DTS file.
        
        :param output_file_name: file name of the output DTS file.
        :type output_file_name: str
        """
        print("导出修补后的设备树...")
        with open(output_file_name, 'w+', encoding='utf-8') as f:
            f.write(self.tree.to_dts())
        return

    def compile_devicetree(self, input_file_name, output_file_name):
        """
        Simply call dtc to compile the DTS file to DTB file.
        
        :param input_file_name: File name of the input DTS file.
        :type input_file_name: str
        :param output_file_name: File name of the output DTB file.
        :type output_file_name: str
        """

        print("编译设备树...")
        if os.name == 'nt':
            returncode = os.system(f"dtc.exe -I dts -O dtb {input_file_name} -o {output_file_name}")
            if returncode != 0:
                print("错误:找不到dtc\n请检查是否完整解压刷机工具")
                sys.exit(1)
        elif os.name == 'posix':
            returncode = os.system(f"dtc -I dts -O dtb {input_file_name} -o {output_file_name}")
            if returncode != 0:
                print("错误:找不到dtc\nLinux大佬自有办法")
                sys.exit(1)
        elif os.name == 'java':
            print("找个正经cpython运行环境来☕️☕️☕️")
            sys.exit(1)
        print("设备树编译完成!")
        return