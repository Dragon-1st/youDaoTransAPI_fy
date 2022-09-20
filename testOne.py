# -*- coding: utf-8 -*-
import sys
import os

print('Start.\n')
path_1 = './ini.json'
print(path_1)
# route=os.path.dirname(sys.argv[0])
# print((os.path.dirname(sys.argv[0])))
# print(type(os.path.dirname(sys.argv[0])))


if __name__ == "__main__":
    path_now = os.getcwd()
    print('os.getcwd:' + path_now)
    path_1 = path_now
    print(path_1)

# cmd中无效
