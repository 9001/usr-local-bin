# usr-local-bin
scripts

## cloning this repo
```
cd /usr/local/bin
git init
git remote add origin git@github.com:9001/usr-local-bin.git
git fetch
git checkout -t origin/master
```

# overview (the good stuff)
| Command | Description
| --- | ---
| **`allsmart`**  | display a short SMART summary for all disks
| **`alpchk`**    | verify the state alpine packages
| **`anime`**     | verify crc32 in filename
| **`bindiff`**   | compare two files, print hexdump of differences
| **`cdiff`**     | colored diff
| **`dircmp`**    | compare current and another directory, listing unique and modified files
| **`dshred`**    | writes predictable yet random-looking data to a disk
| **`dvdimport`** | copy stuff off optical media (prefer miso if the disk is bad)
| **`etasync`**   | shows ETA until all pending writes have flushed to disk
| **`fd-eta`**    | monitor access to a filedescriptor, show read/write speed, provide eta if read
| **`ffchk`**     | look for corruption in multimedia files
| **`hashtar`**   | checksum tar contents without unpacking
| **`hashwalk`**  | recursive checksum/filesize/modes/owner/lastmod
| **`jointar`**   | unpack an archive which is split across multiple disks
| **`mcmp`**      | verify that the decoded contents in multimedia files are equal
| **`mdircmp`**   | compare multiple directores
| **`miso`**      | rescue the contents of scratched/rotten optical media
| **`misomap`**   | correlates a ddrescue mapfile with an iso,
| **`newcrypt`**  | luks-encrypt a device + create btrfs filesystem on it
| **`revert`**    | revert changes in a file based on a(?: compressed)? backup
| **`rfl`**       | recursive file listing with symlink-target, modes, size, owner/group, lastmod
| **`uclose`**    | interactively unmounts and closes one or more luks partitions
| **`uopen`**     | decrypts and mounts one or more luks partitions,
| **`vmdm`**      | mount a virtual-machine disk image (virtualbox, qemu, ...)
| **`xcode-dir`** | transcode all multimedia files in a folder

# overview (the rest)
| Command | Description
| --- | ---
| **`cpr`**       | resume copying a file or blockdevice to a file
| **`famon`**     | monitor access to small files from a process
| **`ileave`**    | display two files interleaved
| **`isotoc`**    | shows file listing for iso file or an inserted cd/dvd/blurei
| **`ms2s`**      | convert gnu-style time(1) into seconds
| **`rdircmp`**   | ranger directory compare
| **`rfl2tvf`**   | convert between two snowflake file listing formats
| **`rimgcmp`**   | ranger image compare
| **`sbs`**       | show two files side by side
| **`smartmon`**  | periodically collect SMART data from disks to logfile
| undup-sc...     | find duplicate split-rar folders
