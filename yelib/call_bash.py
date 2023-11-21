#!/usr/bin/jython

import os, urllib
from java.util import Random

str = os.popen("ls").read()
print ("str:"  + str)
a = str.split("\n")

print(len(a))
for b in a:
  print(":" + b)

r = Random()
print(r.nextInt())


