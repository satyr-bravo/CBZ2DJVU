# CBZ2DJVU
A tool to convert CBZ comics to DJVU books for better reading experience on electronic books and smartphones

[Take me to installation](#installation)

## Features
- Hopefully painless conversion 
- Can auto-detect volumes and chapters structure and write them as a table of contents (disabled by default since results are often messy, see advanced usage)
- Allows adjustment of DPI for converted document
- May serve as a replacement for my old Manga2Djvu project
- Since compression is used, greatly reduces file size and hence, responsiveness while reading

## Anti-features
- Linux (and maybe bsd?) only
- Currently allows only black-and-white output
- May compress images
- Ungodly slow
- Does not clean up after itself

## Installation
1. Download `cbz2djvu.py` and place it into any empty folder
2. Install `unzip`, `djvulibre-bin` and `python3` dependencies if you don't have them

## Usage
1. Place your .cbz book into the folder you placed cbz2djvu script
2. Make sure you have at least twice as much free space on your drive as your .cbz file takes, because this program creates a lot of temporary files
3. Start the script by typing `python3 cbz2djvu.py FILENAME` _**without .cbz extension**_ into the terminal
4. Wait for a very long time (can take up to 30 minutes for 2GB .cbz file), until the program prints "Done!" and exits
5. FILENAME.djvu will be your converted comic, you can delete everything else if not needed

## Advanced usage
type `python3 cbz2djvu.py -h` and experiment with flags

# If something went wrong and errors are being spitted out
  1. Kill the program (unfortunately it is not responsive for ^C, so you'd need to use htop or any other tool)
  2. Read what the errors say
  3. Can't help you much more unfortunately, but there are links for documentation of tools used in the script:
  https://linux.die.net/man/1/djvu
  https://linux.die.net/man/1/unzip
