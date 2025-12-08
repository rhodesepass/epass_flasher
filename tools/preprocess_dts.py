from pydevicetree import Devicetree
import argparse
import sys
import os

def remove_duplicate_props(node):
    if node.properties:
        props = list(node.properties)
        props.reverse()
        seen = set()
        new_props = []
        for prop in props:
            name = getattr(prop, 'name', None)
            if name not in seen:
                new_props.append(prop)
                seen.add(name)
        new_props.reverse()
        node.properties = new_props
    if not node.children:
        return
    for child in node.children:
        remove_duplicate_props(child)


def main():
    parser = argparse.ArgumentParser(description='Preprocess DTS: remove duplicate properties')
    parser.add_argument('input_path', help='Path to input .dts file')
    parser.add_argument('output_path', nargs='?', default=None, help='Path to output .dts file (default: overwrite input)')
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path or input_path

    if not os.path.exists(input_path):
        print(f"Error: input file '{input_path}' does not exist", file=sys.stderr)
        sys.exit(2)

    a = Devicetree.parseFile(input_path)
    remove_duplicate_props(a)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(a.to_dts())


if __name__ == '__main__':
    main()