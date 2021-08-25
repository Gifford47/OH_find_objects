# OH_find_objects
A Python3 script that finds items or other objects in the conf directory or in the jsondb.
<br><br>Usage:<br>
usage: ./find_oh_objects.py [-h] [-f F] [-r R] [-o] [-l]

optional arguments:
  -h, --help  show this help message and exit<br>
  -f F        Search this string in JSONDB and in defined conf files.<br>
  -r R        Requires '-f <search_str>'!. Replace search string with the
              string after '-r' in JSONDB and in defined conf files. Please
              stop OpenHab before!<br>
  -o          Find orphaned items in conf and JSONDB dir.<br>
  -l          List all active items in conf and JSONDB dir (hidden files are
              ignored).<br>

<br><br> Example Output:<br>
![Output](https://user-images.githubusercontent.com/49484063/130794856-79dacb85-db0d-448e-87e7-893dd010495a.JPG)
