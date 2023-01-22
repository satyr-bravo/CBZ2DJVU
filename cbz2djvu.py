import os
import shutil
import argparse
import subprocess

def s_sub(s1, s2):
	return s1.replace(s2,'')
def es(s):
	return s.replace(' ','\ ')

parser = argparse.ArgumentParser(description='Hopefully converts CBZ files to djvu')
parser.add_argument('filename', help='cbz file you want to process')
parser.add_argument('--dpi', type=int)
parser.add_argument('--nocleanup', help ='disable file removal from previous runs', action="store_true")
parser.add_argument('--detectTOC', help ='attempt to detect volumes and chapters', action="store_true")
parser.add_argument('--justTOC', help ='attempt to add TOC to already existing books', action="store_true")
args = parser.parse_args()

FILENAME = s_sub(args.filename, '.cbz')
CLEAN = not args.nocleanup
if args.justTOC:
	CLEAN = False

if (args.dpi == None):
	DPI = 212
else:
	if (args.dpi < 25) or (args.dpi > 1200):
		print("DPI value should be in range from 25 to 1200")
		exit()
	DPI = args.dpi
if not CLEAN:
	print("Cleanup disabled. This may lead to unpredicted errors")
W_DIR = os.getcwd()
T_DIR = W_DIR + "/temp"
DEPS = ['convert', 'djvm', 'cjb2', 'unzip']
PAGES_LIST = []
PBMS_LIST = []

print("Checking dependencies")
for d in DEPS:
	if subprocess.run(f"which {d}", shell = True, capture_output=True).returncode != 0:
		print(f"You are missing {d}! Please install it, or the program will not be able to do its job.")
		exit()
print("All dependencies checked, should be ok to proceed")


if CLEAN:
	shutil.rmtree(T_DIR, ignore_errors = True)
	os.mkdir(T_DIR)
	print("temp directory created")
	os.system(f"unzip {FILENAME}.cbz -d {T_DIR}")
	if os.path.exists(f"{T_DIR}/pbms"):
		shutil.rmtree(f"{T_DIR}/pbms")
	os.mkdir(f"{T_DIR}/pbms")

for dirname, dirnames, filenames in os.walk(T_DIR):
	if "pbms" in dirnames:
		dirnames.remove('pbms')
	for filename in filenames:
		PAGES_LIST.append(os.path.join(dirname, filename))		
PAGES_LIST = sorted(PAGES_LIST)
if args.detectTOC or args.justTOC:
	TABLE = {}
	for pgi in range(len(PAGES_LIST)):
		pgid = s_sub(PAGES_LIST[pgi], T_DIR).split("/")
		for pt in pgid:
			if ("Vol" in pt) or ("Том" in pt) and not(("Ch" in pt) or ("Глава" in pt)):
				vol = pt
			if ("Ch" in pt) or ("Глава" in pt):
				ch = pt
		if vol not in TABLE.keys():
			TABLE[vol] = {}
		else:
			if ch not in TABLE[vol].keys():
				TABLE[vol][ch] = pgi
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
if not args.justTOC:
	pi = 0
	page = PAGES_LIST[pi]
	if os.path.exists(f"{T_DIR}/pbms/{pi}.djvu"):
		print(f"page {pi} already exists, skipping...")
	else:
		os.system(f"convert {es(page)} {T_DIR}/pbms/{pi}.pbm")
		os.system(f"cjb2 -clean -dpi {DPI} {T_DIR}/pbms/{pi}.pbm {T_DIR}/pbms/{pi}.djvu")
	if CLEAN or not os.path.exists(f'{W_DIR}/{FILENAME}.djvu'):
		os.system(f"djvm -c {W_DIR}/{FILENAME}.djvu {T_DIR}/pbms/{pi}.djvu")
	for pi in range(1, len(PAGES_LIST)):
		page = PAGES_LIST[pi]
		if os.path.exists(f"{T_DIR}/pbms/{pi}.pbm"):
			print(f"page {pi} already exists, skipping...")
			os.system(f"djvm -i {W_DIR}/{FILENAME}.djvu {T_DIR}/pbms/{pi}.djvu")
			continue
		os.system(f"convert {es(page)} {T_DIR}/pbms/{pi}.pbm")
		os.system(f"cjb2 -clean -dpi {DPI} {T_DIR}/pbms/{pi}.pbm {T_DIR}/pbms/{pi}.djvu")
		if CLEAN or not os.path.exists(f'{W_DIR}/{FILENAME}.djvu'):
			os.system(f"djvm -i {W_DIR}/{FILENAME}.djvu {T_DIR}/pbms/{pi}.djvu")
		print(f"Making page {pi+1}")
if args.detectTOC or args.justTOC:
	os.system(f'djvused {W_DIR}/{FILENAME}.djvu -e "set-outline TOC.txt" -s')

print("Done!")
