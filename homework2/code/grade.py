#!/usr/bin/env python
import os
import filecmp


def file_get_contents(filename):
    with open(filename) as f:
        return f.read()

if __name__ == "__main__":
    root = os.path.dirname(os.path.realpath(__file__)).replace(" ", "\ ")
    file_names = ["sample01", "sample02", "sample03", "sample04", "sample05"]
    # file_names = ["sample02"]
    for file_name in file_names:
        os.system("python %s/main.py -i %s" % (root, file_name + ".txt"))
        file1 = "output.txt"
        file2 = file_name + ".output.txt"
        print filecmp.cmp(file1, file2, shallow=False)
