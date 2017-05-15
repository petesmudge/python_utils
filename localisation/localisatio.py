#!/usr/bin/python -tt

import os,sys,re
global_except_list = ['.git','tests','overlays', 'examples']
except_list = ['kernel','bootable','docs','build','bionic','abi','out','cts','development','pdk','tools','sdk']
#deliberately remove en-rGB as it is not well localised!
languages = [ 'ar', 'cs', 'de', 'es', 'es-rUS', 'fr', 'hu', 'in', 'it', 'iw', 'ja', 'ko',
              'nb', 'nl', 'pt', 'ru', 'th','tr', 'uk', 'vi', 'zh-rCN', 'zh-rTW']
#good for Titan
overlay_root = "vendor/Vertu/overlays/common"

glob_non_trans_comp = 0

def findResFiles(wa):
  reslist = []
  for basedir,dirs,files in os.walk(wa):
    #print basedir
    if basedir == wa:
      print basedir
      for folder in except_list:
        if folder in dirs: dirs.remove(folder)

    #filter out any generic folders not to be searched/checked
    for folder in global_except_list:
      if folder in dirs: dirs.remove(folder)
      	
    #print basedir, dirs
    if re.search(r'res/values$',basedir):
      #print basedir
      for file in files:
        #print file
        if re.search(r'^strings.xml',file):
          reslist.append(os.path.join(basedir,file))
  return reslist

# from one "string.xml", generate output for this component
def findResComponent(filename):
  (dir, name) = os.path.split(filename)
  #print dir

  inp = open(filename, 'rU')
  #w_inp = inp.read()
  string_names = []
  # Need to check for "do not translate" in the comment the line before the string
  # also check for translatable=false, only take strings that are translateable
  dnt = False
  for line in inp:

    dnt_match = re.search(r'[Dd]o not translate',line)

    match = re.search(r'<string name="(\S+?)"',line)
    # discard the non translatable strings
    if match and not dnt:
      match2 = re.search(r'translatable="false"',line)
      if not match2:
        string_names.append(match.group(1))
    #set dnt true here
    if dnt_match : dnt = True


  # get all resource names and strings? (do we just need resource names?)
  #string_names = re.findall(r'<string name="(\S+?)"', w_inp)
  #

  inp.close()

  #print string_names
  missing_dict = {}
  #take "values" from the path
  upper_dir = os.path.dirname(dir)
  for basedir, dirs, files in os.walk(upper_dir):
    # find localised folders
    #print basedir
    match = re.search(r'values-(\S+)', basedir)
    if match and match.group(1) in languages:
      in_fn = os.path.join(basedir, 'strings.xml')
      if os.path.isfile(in_fn):
        loc_file = open(in_fn,'rU')
        #print in_fn
        all_file = loc_file.read()
        loc_file.close()
        #look for overlay and append it to the file if exists
        ov_fn = os.path.join(overlay_root,in_fn)
        #print ov_fn
        if os.path.isfile(ov_fn):
          #print "Overlay found : " + ov_fn
          ov_file = open(ov_fn)
          all_file += ov_file.read()
          ov_file.close()

        # now search over the file for all occurences of each component of string_names
        # only care about missing ones - once found, move on - store locale value for missing item into dict indexed by string_name
        # { string_name, ['en','fr','de']}   < only entries for those localisations missing.
        # optional - keep stats (i.e. number matched, total, number missing
        # TBD #
        #print match.group(0)
        # maybe re whole list to get list of components, then match lists?
        loc_string_names = re.findall(r'<string name="(\S+?)"', all_file)
        #now just match names?
        i = 0
        for strg in string_names:
          if strg not in loc_string_names:
            #print strg
            # add the missing string into the dict, with the language code
            if strg not in missing_dict:
              missing_dict[strg] = [match.group(1)]
            else:
              missing_dict[strg].append(match.group(1))
          else:
            i += 1
            #print i
          #print strg
        #print 'processed ' + filename + ' with ' + str(i) + ' matches out of ' + str(len(string_names))
        # TBD#
        #sys.exit(0)

  return missing_dict

def printFileResults(file,resdict,level):
  non_trans = 0
  lst = []
  if resdict:
    if level < 2 : print "\n%s: %d partially translated strings:" % (file,len(resdict.keys()))
    for key in sorted(resdict.keys()):
      if level < 2:
        print key, resdict[key]
      elif len(resdict[key]) == len(languages):
        non_trans += 1
        lst.append(key)
    if lst:
      if level == "2" : print "\n%s : %d non_translated :" % (file,non_trans)
      else : print " of which %d non translated: " % non_trans
      print lst
      global glob_non_trans_comp
      glob_non_trans_comp += 1

# given a list of string xml files and paths, find all string resource id's
# then match through all localised folders, storing if it is not found
def findMissingResources(reslist,level):
  for file in reslist:
    missing = findResComponent(file)
    printFileResults(file,missing,level)
  return


def main():
  args = sys.argv[1:]

  if not len(args) == 2:
    print 'usage: <path to workarea root i.e. android root> <level of output>'
    print ' level 0 = print all stats, level 1 = list files that miss some translations,' \
          ' level 2 = only files with NO translations '''
    sys.exit(1)

  workarea = args[0]
  level = args[1]

  if not os.path.exists(workarea):
    print 'invalid path to workarea'
    sys.exit(1)

  all_res_files = findResFiles(workarea)
  print all_res_files
  print '\nOut of %d components found : ' % len(all_res_files)

  findMissingResources(all_res_files,level)

  global glob_non_trans_comp
  print "\n%d components have non translated strings" % glob_non_trans_comp

if __name__ == '__main__':
  main()