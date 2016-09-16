# coding:utf-8
"""
时间:2016/5/17
说明:
"""
from math import sqrt, pow
a = (3.0, 0)
b = (0, 4.0)
c = sqrt(pow(float(a[0]-b[0]), 2) + pow(float(a[1]-b[1]), 2))
print c