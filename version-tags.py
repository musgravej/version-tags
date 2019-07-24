import os
import math
import shutil
import datetime
import configparser
import fpdf
import collections


def main():
    lst = ['t1', 't1', 't2', 't2', 't2', 't1', 't3', 't4', 't4']

    dic = collections.Counter(lst)

    print(dic)

if __name__ == '__main__':
    main()
