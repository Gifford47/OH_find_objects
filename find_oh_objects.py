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

def read_json(files):
    for file_key in files:
        if os.path.isfile(files[file_key]):
            with open(files[file_key]) as json_file:
                json_data = json.load(json_file)
                if search in str(json_data):
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

def read_file(files):
    for file_key in files:
        if os.path.isdir(files[file_key]):
            for root, dirs, file_path in os.walk(files[file_key]):
                # diese skriptdatei ignorieren
                if os.path.basename(__file__) in file_path:
                    file_path.remove(os.path.basename(__file__))
                for file in file_path:
                    #print(os.path.join(root, file))
                    try:
                        with open(os.path.join(root, file), 'r') as file_opened:
                            filedata = file_opened.read()
                            file_opened.close()
                        if search in filedata:
                            #print('Found in:' + os.path.join(root, file))
                            occ = re.findall(r"\b%s\b" % search, filedata)  # "\b" = represents the backspace character
                            if len(occ) > 0:
                                print("Found " + str(len(occ)) + "x in: '" + os.path.join(root, file))
                                occ = 0
                    except:
                        pass

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument("search_string", help="Search this string in jsondb and in defined conf files.", type=str)
    parser.add_argument("-r", help="Replace search string with this string in jsondb and in defined conf files.", type=str, nargs=1)
    args = parser.parse_args()
    #print(args)
    search = args.search_string
    print("Search String: '" + args.search_string + "'")

    print("\nIn Conf-Files:")
    read_file(conf_files)

    print("\nIn UI-Files:")
    read_json(jsondb_files)
    print(table.get_string()+'\n\n')

    # if replace argument exists:
    if args.r:
        replace_str = args.r[0]                                             # get replace str from list
        print("<<<< Replacing String '" + search + "' with '" + replace_str + "'>>>>\n")
        os.system(replace_script + ' -r ' + search + ' ' + replace_str + ' -p ' + jsondb_dir + ' -depth 0')     # replace only in root dir
        print('\n')
        os.system(replace_script + ' -r ' + search + ' ' + replace_str + ' -p ' + conf_dir)
