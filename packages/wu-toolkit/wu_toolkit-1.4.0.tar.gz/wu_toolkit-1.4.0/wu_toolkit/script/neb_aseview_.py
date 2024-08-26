import sys
from pathlib import Path
from ase.io import read
from ase.visualize import view

def visualize_neb_structures(start, end, filename, base_dir="."):
    """
    读取指定范围内的文件夹中的结构文件并进行可视化。

    :param start: 起始文件夹编号
    :param end: 结束文件夹编号
    :param filename: 结构文件名
    :param base_dir: 文件夹所在的基础目录，默认为当前目录
    """
    structures = []
    base_path = Path(base_dir)

    for i in range(start, end + 1):
        folder_name = f"{i:02d}"
        folder_path = base_path / folder_name
        file_path = folder_path / filename

        if file_path.exists():
            try:
                structure = read(file_path)
                structures.append(structure)
                print(f"Read {filename} from {folder_name}")
            except Exception as e:
                print(f"Failed to read {filename} in {folder_name}: {e}")
        else:
            print(f"{filename} not found in {folder_name}")

    if structures:
        view(structures)
    else:
        print("No structures to visualize.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: script.py start end filename")
        sys.exit(1)

    start = int(sys.argv[1])
    end = int(sys.argv[2])
    filename = sys.argv[3]

    visualize_neb_structures(start, end, filename)