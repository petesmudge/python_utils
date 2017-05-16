#!/usr/bin/python -tt

import os,sys,re


#modify these filter lists as appropriate to avoid searching no-relevant code
#checked/removed on every search path:
global_except_list = ['.git','tests', 'examples']
#checked on top level only
except_list = ['kernel','bootable','docs','build','bionic','abi','out','cts','development','pdk','tools','sdk']
#list of langauges required for Vertu products
#deliberately remove en-rGB as it is not well localised! tends to roll back to default anyway
# can reduce this to reduce search scope for specific languages if required
languages = [ 'ar', 'cs', 'de', 'es', 'es-rUS', 'fr', 'hu', 'in', 'it', 'iw', 'ja', 'ko',
              'nb', 'nl', 'pt', 'ru', 'th','tr', 'uk', 'vi', 'zh-rCN', 'zh-rTW']

#Find in project defintition - DEVICE_PACKAGE_OVERLAYS and PRODUCT_PACKAGE_OVERLAYS
#added paths for tron and titan here
overlay_roots = ["vendor/Vertu/overlays/common",
                 #"vendor/Vertu/overlays/china",
                 "device/qcom/common/device/overlay",
                 "device/tct/tron/overlay",
                 "custo_wimdata_ng/wlanguage/overlay"]

string_search = r'<string\s*name\s*=\s*"(\S+?)"'

glob_part_trans = 0
glob_non_trans = 0

def findResFiles(wa):
  reslist = []
  for basedir,dirs,files in os.walk(wa):

    if basedir == wa:
      for folder in except_list:
        if folder in dirs: dirs.remove(folder)

    #filter out any generic folders not to be searched/checked
    for folder in global_except_list:
      if folder in dirs: dirs.remove(folder)
      	
    #find files to parse for strings   
    if re.search(r'res/values$',basedir):

      for file in files:

        if re.search(r'^strings\S*.xml',file):
          reslist.append(os.path.join(basedir,file))
  return reslist

# from one "string.xml", generate stats on partial translations for this files
def findResComponent(filename):
  (dir, name) = os.path.split(filename)
  #print dir

  #1. First of all create a list of string components that are translateable
  inp = open(filename, 'rU')
  #w_inp = inp.read()
  string_names = []
  # Need to check for "do not translate" in the comment the line before the string
  # also check for translatable=false, only take strings that are translateable
  dnt = False
  for line in inp:

    dnt_match = re.search(r'do not translate',line.lower())

    match = re.search(string_search,line)
    # discard the non translatable strings
    if match and not dnt:
      match2 = re.search(r'translatable\s*=\s*"false"',line)
      if not match2:
        string_names.append(match.group(1))
    #set dnt true here
    if dnt_match : dnt = True

  inp.close()

  #2. now go through all sub-paths to find localised files
  # in folders "values-*", apply any overlays,
  #and then compare to the list of vanilla strings to find 
  #if there are any non-translated
  missing_dict = {}
  #take "values" from the path
  upper_dir = os.path.dirname(dir)
  for basedir, dirs, files in os.walk(upper_dir):
    # find localised folders
    match = re.search(r'values-(\S+)', basedir)
    if match and match.group(1) in languages:
      #find all files of the same name
      in_fn = os.path.join(basedir, name)
      if os.path.isfile(in_fn):
        loc_file = open(in_fn,'rU')
        #print in_fn
        all_file = loc_file.read()
        loc_file.close()
        #look for overlay file and append it to the file if exists
        for root in overlay_roots:
          ov_fn = os.path.join(root,in_fn)
          #print ov_fn
          if os.path.isfile(ov_fn):
            #print "Overlay found : " + ov_fn
            ov_file = open(ov_fn)
            all_file += ov_file.read()
            ov_file.close()

        # create list of all string components in localised files
        loc_string_names = re.findall(string_search, all_file)

        # now search over the file for all occurences of each component of string_names
        # store locale value for missing item into dict indexed by string_name
        # { string_name, ['en','fr','de']}   < only entries for those localisations missing.
     
        #now just match names
        for strg in string_names:
          if strg not in loc_string_names:
            #print strg
            # add the missing string into the dict, with the language code
            if strg not in missing_dict:
              missing_dict[strg] = [match.group(1)]
            else:
              missing_dict[strg].append(match.group(1))

  return missing_dict

def printFileResults(file,resdict,level):
  non_lst = []
  part_lst = []
  global glob_non_trans
  global glob_part_trans
  #generate 2 lists, partial and not translated
  # print both for level 1, and not translated only for level 2
  if resdict:
    for key in sorted(resdict.keys()):
      if len(resdict[key]) == len(languages):
        non_lst.append(key)
      else:
	part_lst.append(key)

    if level < 2 and part_lst : 
      print "\n%s : %d partially translated strings:" % (file,len(part_lst))
      glob_part_trans += 1
      for key in part_lst:
        print key, resdict[key]

    if non_lst:
      if level == 2 or not part_lst : print "\n%s" % file
      print "\n%d completely non_translated :" % len(non_lst)
      glob_non_trans += 1
      print non_lst


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
          ' level 2 = list only files with NO translations '''
    sys.exit(1)

  workarea = args[0]
  level = int(args[1])

  if not os.path.exists(workarea):
    print 'invalid path to workarea'
    sys.exit(1)

  all_res_files = findResFiles(workarea)
  print all_res_files
  print '\nOut of %d components found : ' % len(all_res_files)

  findMissingResources(all_res_files,level)

  global glob_non_trans
  global glob_part_trans
  if level < 2: print "\n%d components have partially translated strings" % glob_part_trans
  print "\n%d components have non translated strings" % glob_non_trans

if __name__ == '__main__':
  main()