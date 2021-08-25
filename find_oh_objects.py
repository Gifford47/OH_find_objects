#!/usr/bin/python3
# -*- coding: utf-8 -*-

#pip install prettytable

import sys, json, os, re
import argparse
from prettytable import PrettyTable
table = PrettyTable()

jsondb_dir = "/var/lib/openhab/jsondb"
conf_dir = "/etc/openhab"

replace_script = '/root/openhab/tools/find_replace.py'

table.field_names = ["Object", "UID", "Name", "Label", "Description", "Tags", "File"]
table._max_width = {"Object":35, "UID":35, "Name":35, "Label":35, "Description":35, "Tags":35, "File":40}

oh_item_types = ['color', 'contact', 'dimmer', 'group', 'image', 'location', 'number', 'player', 'rollershutter', 'string', 'switch']

jsondb_files = {
    'rules' : jsondb_dir + "/automation_rules.json",
    'items' : jsondb_dir + "/org.openhab.core.items.Item.json",
    'things' : jsondb_dir + "/org.openhab.core.thing.Thing.json",
    'links' : jsondb_dir + "/org.openhab.core.thing.link.ItemChannelLink.json",
    'habpanel' : jsondb_dir + "/uicomponents_habpanel_panelconfig.json",
    'ui_page' : jsondb_dir + "/uicomponents_ui_page.json",
    'txt_files' : "Y:/"
}
conf_files = {
    'rules' : conf_dir + "/rules",
    'scripts': conf_dir + "/scripts",
    'items' : conf_dir + "/items",
    'things' : conf_dir + "/things",
    'sitemaps' : conf_dir + "/sitemaps",
    'transforms': conf_dir + "/transform",
    'persistence': conf_dir + "/persistence",
}

def find_str_in_json(search, files, quiet=False):
    found = False
    for file_key in files:
        if os.path.isfile(files[file_key]):
            with open(files[file_key]) as json_file:
                json_data = json.load(json_file)
                if search in str(json_data):
                    found = True
                    if not quiet:
                        for first_key in json_data:
                            if search == first_key or search in str(json_data[first_key]):
                                if file_key == "rules":  # for specific json files/keys
                                    table.add_row([str(file_key), str(json_data[first_key]['value']['uid']) , str(json_data[first_key]['value']['name']), "", str(json_data[first_key]['value']['description']), "", str(files[file_key])])
                                elif file_key == "items":  # for specific json files/keys
                                    table.add_row([str(file_key), str(first_key), "", str(json_data[first_key]['value']['label']), "" , str(json_data[first_key]['value']['tags']), str(files[file_key])])
                                elif file_key == "things":  # for specific json files/keys
                                    table.add_row([str(file_key), str(json_data[first_key]['value']['thingTypeUID']["uid"]) , "", str(json_data[first_key]['value']['label']), "", "", str(files[file_key])])
                                elif file_key == "links":  # for specific json files/keys
                                    table.add_row([str(file_key), str(first_key), "", "", str(json_data[first_key]['value']['itemName']), "", str(files[file_key])])
                                elif file_key == "habpanel":  # for specific json files/keys
                                    table.add_row([str(file_key), str(first_key), str(json_data[first_key]['value']['uid']), str(json_data[first_key]['value']['config']['settings']['panel_name']), "" , "", str(files[file_key])])
                                elif file_key == "ui_page":  # for specific json files/keys
                                    table.add_row([str(file_key), str(json_data[first_key]['value']['uid']), "", str(json_data[first_key]['value']['config']['label']), "" , "", str(files[file_key])])

                                #optional:
                                #if file_key == "txt_files":  # for specific json files/keys
                                    #table.add_row([str(file_key), str(json_data[first_key]['value']['uid']), "", str(json_data[first_key]['value']['config']['label']), "" , "", str(files[file_key])])
    return found

def find_str_in_file(search, files, quiet=False):
    found = False
    for file_key in files:
        if os.path.isdir(files[file_key]):
            for root, dirs, files_list in os.walk(files[file_key]):
                # diese skriptdatei ignorieren
                if os.path.basename(__file__) in files_list:
                    files_list.remove(os.path.basename(__file__))
                for file in files_list:
                    #print(os.path.join(root, file))
                    try:
                        with open(os.path.join(root, file), 'r') as file_opened:
                            filedata = file_opened.read()
                            file_opened.close()
                        if search in filedata:
                            found = True
                            if not quiet:
                                #print('Found in:' + os.path.join(root, file))
                                occ = re.findall(r"\b%s\b" % search, filedata)  # "\b" = represents the backspace character
                                if len(occ) > 0:
                                    print("Found " + str(len(occ)) + "x in: '" + os.path.join(root, file))
                                    occ = 0
                    except:
                        pass
    return found

def read_items():
    items_dict = {jsondb_files['items']:{},
                  conf_files['items']:{}}
    no_items = 0

    # read JSONDB items:
    print('Reading JSONDB items in '+jsondb_dir+' ...')
    with open(jsondb_files['items']) as json_file:
        json_data = json.load(json_file)
    for item, value in json_data.items():
        items_dict[jsondb_files['items']][item] = json_data[item]['value']['label']
        no_items += 1                                                                   # increase counter

    # read txt config items:
    print('Reading txt config items in '+conf_dir+' ...')
    if os.path.isdir(conf_files['items']):
        for root, dirs, files_list in os.walk(conf_files['items']):
            for file in files_list:
                if not file[0] == '.':                                      # ignore hidden files
                    file_data = open(os.path.join(conf_files['items'], file), 'r')
                    file_lines = file_data.readlines()
                    for line in file_lines:
                        file_split = line.split()                           # split by whitespace
                        if len(file_split) > 1:
                            item_type = file_split[0]
                            if item_type.lower() in oh_item_types:              # if first key is an oh 'item-type'
                                item_name = file_split[1]
                                item_label = ''
                                try:                                        # not every item has a label
                                    item_label = re.findall(r'\"(.+?)\"', line)[0]    # find first str between double quotes
                                except Exception:
                                    pass
                                items_dict[conf_files['items']][item_name] = item_label
                                no_items += 1  # increase counter

    print('Number of items:'+str(no_items))
    for key in items_dict:
        items_dict[key] = dict(sorted(items_dict[key].items()))
    return items_dict

def pretty_print(d, indent=0, ending='\n'):
   for key, value in d.items():
      print('\t' * indent + str(key), end=ending)
      if isinstance(value, dict):
         pretty_print(value, indent+1, ending='')
      else:
         print(' ' * (indent+1) + '"' + str(value) + '"')

def del_key(dict, key):                     # only for one indent dicts!
    try:
        dict.pop(key)
    except Exception:
        pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument("-f", help="Search this string in JSONDB and in defined conf files.", type=str, nargs=1)
    parser.add_argument("-r", help="Requires '-f <search_str>'!. Replace search string with the string after '-r' in "
                                   "JSONDB and in defined conf files. Please stop OpenHab before!", type=str, nargs=1)
    parser.add_argument("-o", help="Find orphaned items in conf and JSONDB dir.", action='store_true')
    parser.add_argument("-l", help="List all active items in conf and JSONDB dir (hidden files are ignored).", action='store_true')
    args = parser.parse_args()
    #print(args)
    if args.f:
        search_str = args.f[0]
        print("Search String: '" + search_str + "'")
        print("\nIn Conf-Files:")
        find_str_in_file(search_str, conf_files)
        print("\nIn UI-Files:")
        find_str_in_json(search_str, jsondb_files)
        print(table.get_string()+'\n\n')

        # if replace argument exists:
        if args.r:
            replace_str = args.r[0]                                             # get replace str from list
            print("<<<< Replacing String '" + search_str + "' with '" + replace_str + "'>>>>\n")
            os.system(replace_script + ' -r ' + search_str + ' ' + replace_str + ' -p ' + jsondb_dir + ' -depth 0')     # replace only in root dir
            print('\n')
            os.system(replace_script + ' -r ' + search_str + ' ' + replace_str + ' -p ' + conf_dir)

    if args.o:
        items = read_items()
        json_item_path = jsondb_files['items']
        conf_item_path = conf_files['items']
        conf_files.pop('items')  # delete items key
        jsondb_files.pop('items')  # delete items key
        orphaned_items = items.copy()

        # print('Orphaned items in ' + json_item_path)
        for item in list(items[json_item_path]):  # go through all keys
            if find_str_in_json(item, jsondb_files, quiet=True):  # if found, item is not orphaned
                del_key(orphaned_items[json_item_path], item)  # remove item from orphaned items dict
            if find_str_in_file(item, conf_files, quiet=True):  # if found, item is not orphaned
                del_key(orphaned_items[json_item_path], item)  # remove item from orphaned items dict

        # print('Orphaned items in ' + conf_item_path)
        for item in list(items[conf_item_path]):
            if find_str_in_json(item, jsondb_files, quiet=True):  # if found, item is not orphaned
                del_key(orphaned_items[conf_item_path], item)  # remove item from orphaned items dict
            if find_str_in_file(item, conf_files, quiet=True):  # if found, item is not orphaned
                del_key(orphaned_items[conf_item_path], item)  # remove item from orphaned items dict

        print('\nListing orphaned items according to their location:')
        pretty_print(orphaned_items)

    if args.l:
        print('\nListing all items according to their location:')
        items = read_items()

        pretty_print(items)
