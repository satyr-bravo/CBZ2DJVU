# CBZ2DJVU
A tool to convert CBZ comics to DJVU books for better reading experience on e-readers

[Take me to installation](#installation)

## Features
- Three modes of conversion: 
    - color - ~75% the size of CBZ (on average)
    - grayscale - ~60% 
    - b&w - ~10% 
- Can auto-detect volumes and chapters structure and write them as a table of contents (disabled by default, see [advanced usage](#advanced-usage))
- Allows adjustment of DPI for converted document
- May serve as a replacement for my old Manga2Djvu project

## Anti-features
- Linux (and maybe bsd?) only
- Ungodly slow
- Does not clean up after itself

## Installation
1. Download `cbz2djvu.py` and place it into any empty folder
2. Install `unzip`, `djvulibre-bin` and `python3` dependencies if you don't have them

## Usage
1. Place your .cbz book into the folder you placed cbz2djvu script
2. Make sure you have at least twice as much free space on your drive as your .cbz file takes, because this program creates a lot of temporary files
3. Start the script by typing `./cbz2djvu.py FILENAME` into the terminal (color mode is assumed by default, see [advanced usage](#advanced-usage))
4. Wait for a very long time (can take up to 45 minutes), until the program prints "Done!" and exits
5. FILENAME.djvu will be your converted comic, you can delete everything else if not needed

## Advanced usage
|Flag           | What for                                                                                                          |
|---------------|-------------------------------------------------------------------------------------------------------------------|
|`-h`           | Displays help message                                                                                             |
|`--dpi=DPI`    | Set DPI value for a final document                                                                                |
|`--gs`         | Set document conversion mode to grayscale for smaller file size                                                   |
|`--bw`         | Set document conversion mode to black&white for smallest possible file size                                       |
|`--detectTOC`  | Guess table of contents from the folder structure (very unstable, likely to crash, better to use "justTOC" flag)  |
|`--justTOC`    | Guess table of contents and append it to the already made file without re-generating it                           |
|`--nocleanup`  | Do not delete files from previous runs (likely to mess things up, use at your own risk)                           |

## TODO
1. Improve table of contents detection 
2. Somehow increase program's speed (maybe multi-threading would help?)
3. Iron out UI and small bugs (just for satisfaction, it's not like anybody is going to use the thing)


# If something went wrong and errors are being spit out
  1. Kill the program (unfortunately it is not responsive to ^C, so you'd need to use htop or any other tool)
  2. Read what the errors say
  3. Can't help you much more unfortunately, but there are links for documentation of tools used in the script:
  
  https://linux.die.net/man/1/djvu
  
  https://linux.die.net/man/1/unzip
