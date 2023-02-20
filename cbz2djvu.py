#!/usr/bin/python3
import os
import shutil
import argparse
import subprocess
import re

parser = argparse.ArgumentParser(
    description='Hopefully converts CBZ files to djvu')
parser.add_argument('filename', help='cbz file you want to process')
parser.add_argument('--dpi', type=int)
parser.add_argument(
    '--gs', help='Convert all images to grayscale for smaller file size', action="store_true")
parser.add_argument(
    '--clr', help='Keep color if you need it, biggest file size', action="store_true")
parser.add_argument(
    '--detectTOC', help='attempt to detect volumes and chapters', action="store_true")
parser.add_argument(
    '--nocleanup', help='disable file removal from previous runs', action="store_true")
parser.add_argument(
    '--justTOC', help='attempt to add TOC to already existing books', action="store_true")
parser.add_argument(
    '--fitscreen', help="take target device's screen size in format WIDTHxHEIGHT, scales every image so that it'll fit. Normally used to shrink file size even further", type=str)
parser.add_argument(
    '--cleanafter', help='Delete all the temporary files afterwards', action="store_true")
args = parser.parse_args()

#function defenitions
def drawProgressBar(cur, max, task=''): #Draw a progress bar with given task name, cur is a current position, max is maximum
    rat = cur/max
    col = os.get_terminal_size().columns
    bar_size = col - len(task) - len(str(max))*2 - 16
    b = int(bar_size * rat)
    a = bar_size - b
    print(
        f'{task}[{("="*b)}{" "*a}] | {cur}/{max} | {100*rat:.2f}%', end="\r", flush=True)

def s_sub(s1, s2): #"Substract" string s2 from s1
    return s1.replace(s2, '')

def es(s): #Auto-protect spaces
    return s.replace(' ', '\ ')

def sort_nicely(l): #Sort a list of filenames in a human way
    def tryint(s):
        try:
            return int(s)
        except:
            return s
    def alphanum_key(s):
        return [tryint(c) for c in re.split('([0-9]+)', s)]

    l.sort(key=alphanum_key)

#Parsing arguments and setting variables accordingly
FILENAME = s_sub(args.filename, '.cbz')

CLEAN = not args.nocleanup
CLEAN_AFT =  args.cleanafter
if args.justTOC:
    CLEAN = False

if args.clr and args.gs:
    print("Color and grayscale conversion modes are mutually exclusive, please set flags properly")
    exit()

if args.clr:
    form = 'ppm'
    tool = 'c44'
elif args.gs:
    form = 'pgm'
    tool = 'c44'
else:
    form = 'pbm'
    tool = 'cjb2 -clean'

if (args.dpi == None):
    DPI = 212
else:
    if (args.dpi < 25) or (args.dpi > 1200):
        print("DPI value should be in range from 25 to 1200")
        exit()
    DPI = args.dpi

if args.fitscreen != None:
    fit = "-filter triangle -resize "+ args.fitscreen + "\>"
else:
    fit = ''

if not CLEAN:
    print("Cleanup disabled. This may lead to unpredicted errors")
W_DIR = os.getcwd()
T_DIR = W_DIR + "/temp"
DEPS = ['convert', 'djvm', 'cjb2', 'unzip', 'c44']
PAGES_LIST = []
PBMS_LIST = []

#Checking if all needed dependencies are set
print("Checking dependencies...", end = "\r")
for d in DEPS:
    if subprocess.run(f"which {d}", shell=True, capture_output=True).returncode != 0:
        print(
            f"Couldn't fing {d} dependency! Unable to proceed further, exiting...")
        exit()
print(" "*os.get_terminal_size().columns, end = "\r")
print("Dependencies OK")

#cleaning up workspace from previous runs
if CLEAN:
    shutil.rmtree(T_DIR, ignore_errors=True)
    os.mkdir(T_DIR)
    print("Temporary directory created")
    print("Extracting file...", end = "\r")
    os.system(f"unzip -qq {FILENAME}.cbz -d {T_DIR}")
    print(" "*os.get_terminal_size().columns, end = "\r")
    print("File extracted")
    if os.path.exists(f"{T_DIR}/pbms"):
        shutil.rmtree(f"{T_DIR}/pbms")
    os.mkdir(f"{T_DIR}/pbms")

for dirname, dirnames, filenames in os.walk(T_DIR):
    if "pbms" in dirnames:
        dirnames.remove('pbms')
    for filename in filenames:
        PAGES_LIST.append(os.path.join(dirname, filename))
sort_nicely(PAGES_LIST)

#Detecting and generating table of contents
if args.detectTOC or args.justTOC:
    TABLE = {}
    for pgi in range(len(PAGES_LIST)):
        pgid = s_sub(PAGES_LIST[pgi], T_DIR).split("/")
        for pt in pgid:
            if ("Vol" in pt) or ("Том" in pt) and not (("Ch" in pt) or ("Глава" in pt)):
                vol = pt
            if ("Ch" in pt) or ("Глава" in pt):
                ch = pt
        if vol not in TABLE.keys():
            TABLE[vol] = {}
        else:
            if ch not in TABLE[vol].keys():
                TABLE[vol][ch] = pgi
        drawProgressBar(pgi, len(PAGES_LIST), "Generating TOC ")
    os.system("touch TOC.txt")
    toc = open("TOC.txt", 'w')
    toc.write("(bookmarks\n")

    for vol in TABLE.keys():
        toc.write(f'\t("{vol}" "#{TABLE[vol][list(TABLE[vol].keys())[0]]}"\n')
        for ch in TABLE[vol].keys():
            toc.write(f'\t\t("{ch}" "#{TABLE[vol][ch]}")\n')
        toc.write('\t)\n')
    toc.write(')')
    toc.close()

#Main conversion cycle
mx = len(PAGES_LIST)
if not args.justTOC:
    pi = 0
    page = PAGES_LIST[pi]
    if os.path.exists(f"{T_DIR}/pbms/{pi}.djvu"):
        print(f"page {pi} already exists, skipping...")
    else:
        os.system(f"convert {fit} {es(page)} {T_DIR}/pbms/{pi}.{form}")
        os.system(
            f"{tool} -dpi {DPI} {T_DIR}/pbms/{pi}.{form} {T_DIR}/pbms/{pi}.djvu")
    if CLEAN or not os.path.exists(f'{W_DIR}/{FILENAME}.djvu'):
        os.system(f"djvm -c {W_DIR}/{FILENAME}.djvu {T_DIR}/pbms/{pi}.djvu")
    for pi in range(1, len(PAGES_LIST)):
        page = PAGES_LIST[pi]
        if os.path.exists(f"{T_DIR}/pbms/{pi}.{form}"):
            print(f"page {pi} already exists, skipping...")
            os.system(
                f"djvm -i {W_DIR}/{FILENAME}.djvu {T_DIR}/pbms/{pi}.djvu")
            continue
        os.system(f"convert {fit} {es(page)} {T_DIR}/pbms/{pi}.{form}")
        os.system(
            f"{tool} -dpi {DPI} {T_DIR}/pbms/{pi}.{form} {T_DIR}/pbms/{pi}.djvu")
        if CLEAN or not os.path.exists(f'{W_DIR}/{FILENAME}.djvu'):
            os.system(
                f"djvm -i {W_DIR}/{FILENAME}.djvu {T_DIR}/pbms/{pi}.djvu")
        drawProgressBar(pi, mx, "Converting pages ")
drawProgressBar(mx, mx, "Converted! ")
print(" "*os.get_terminal_size().columns, end = "\r")
#Writing table of contents into the file
if args.detectTOC or args.justTOC:
    os.system(f'djvused {W_DIR}/{FILENAME}.djvu -e "set-outline TOC.txt" -s')

if CLEAN_AFT:
    print("Cleaning up...")
    shutil.rmtree(T_DIR, ignore_errors=True)
    os.system('rm TOC.txt')
    print(" "*os.get_terminal_size().columns, end = "\r")
    print("Temporary files removed")

print("Done!")
