import os, struct

# Local Import
import lib.ReFScan as ReFScan

def main():
    # image = r"\\.\D:/VM/ReFS/ReFS-0-flat.vmdk"
    # image = r"\\.\D:"
    image = r"\\.\C:/Users/yhcha/Documents/Virtual Machines/Windows 10 x64/Windows 10-x64-0-ReFS-flat.vmdk"
    f = open(image, "rb")                                               # Scan Filesystem
    vbrOffset = ReFScan.get_offset(f, "52654653000000")                 # Get Volume Boot Record
    vbrData = ReFScan.dump_vbr(f, vbrOffset)                            # Dump results
    cluster = vbrData["bytesPerSector"]*vbrData["sectorsPerCluster"]    # Cluster size
    supbData = ReFScan.dump_supb(f, vbrOffset, cluster)                 # Dump Superblock
    chkpData = ReFScan.dump_chkp(f, int(supbData["checkpointPtr0"],16)) # Checkpoint
    f.close()
    return 0


if __name__ == "__main__":
    main()
