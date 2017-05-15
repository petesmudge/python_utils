#!/usr/bin/python
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

import os
import re
import sys
import urllib

"""Logpuzzle exercise
Given an apache logfile, find the puzzle urls and download the images.

Here's what a puzzle url looks like:
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"
"""
def custom_sort(s):
  ms = re.search(r'-\S+-(\S+).jpg',s)
  if ms == None:
    return s
  else:
    return ms.group(1)

def read_urls(filename):
  """Returns a list of the puzzle urls from the given log file,
  extracting the hostname from the filename itself.
  Screens out duplicate urls and returns the urls sorted into
  increasing order."""
  # +++your code here+++
  f = open(filename, 'rU')
  index = filename.find('_')
  if index == -1:
    sys.exit(1);
  server = filename[index+1:];
  wf = f.read();
  url_list = re.findall(r'GET\s+(\S+puzzle\S+)\s+HTTP',wf)
  out_list = None
  prev = ''
  for url in sorted(url_list,key=custom_sort):
    if url != prev:
      #add it to list
      out_list.append('http://' + server + url)
    prev = url
  #print out_list
  return out_list

def download_images(img_urls, dest_dir):
  """Given the urls already in the correct order, downloads
  each image into the given directory.
  Gives the images local filenames img0, img1, and so on.
  Creates an index.html in the directory
  with an img tag to show each local image file.
  Creates the directory if necessary.
  """
  # +++your code here+++
  if not os.path.exists(dest_dir):
    os.mkdir(dest_dir)

  index_file = open(os.path.join(dest_dir,index.html),'w+')
  index_file.write("<html>\n<body>\n")

  i = 0
  for url in img_urls:
    #pull the image to dest_dir, incrementing img file number
    destfile = 'img' + str(i) + '.jpg'
    urllib.urlretrieve(url,os.path.join(dest_dir,destfile))
    print "retrieving file " + str(i)
    index_file.write('<img src="'+destfile+'">')
    i += 1

  index_file.write("</body>\n</html>")
  index_file.close()



def main():
  args = sys.argv[1:]

  if not args:
    print 'usage: [--todir dir] logfile '
    sys.exit(1)

  todir = ''
  if args[0] == '--todir':
    todir = args[1]
    del args[0:2]

  img_urls = read_urls(args[0])

  if todir:
    download_images(img_urls, todir)
  else:
    print '\n'.join(img_urls)

if __name__ == '__main__':
  main()
