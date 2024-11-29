import os, struct

# Local Import
import lib.ReFScan as ReFScan

def main():
    image = r"\\.\D:/VM/ReFS/ReFS-0-flat.vmdk"
    # image = r"\\.\D:\Virtual Machines\Windows 10 x64/ReFS-flat.vmdk"
    # image = r"\\.\D:"
    # image = r"\\.\C:/Users/yhcha/Documents/Virtual Machines/Windows 10 x64/Windows 10-x64-0-ReFS-flat.vmdk"
    f = open(image, "rb")                                                                       # Scan Filesystem
    vbrOffset = ReFScan.get_offset(f, "52654653000000")                                         # Get Volume Boot Record
    vbrData = ReFScan.dump_vbr(f, vbrOffset)                                                    # Dump results
    cluster = vbrData["bytesPerSector"]*vbrData["sectorsPerCluster"]                            # Cluster size
    supbData = ReFScan.dump_supb(f, vbrOffset, cluster)                                         # Dump Superblock
    chkpData = ReFScan.dump_chkp(f, int(supbData["checkpointPtr0"],16), vbrOffset, cluster)     # Checkpoint
    chkpData1 = ReFScan.dump_chkp(f, int(supbData["checkpointPtr1"],16), vbrOffset, cluster)    # 2nd Checkpoint
    containerTable = ReFScan.dump_container_table(f, chkpData["containerTable"])
    # schemaTable = ReFScan.dump_schema_table(f, chkpData["schemaTable"])
    
    # print("\n\n")
    # for i in chkpData.keys():
    #     print(f"{i: <30}: {ReFScan.dump_page_header(f, chkpData[i])}")
    # print("\n\n")
    # for i in chkpData1.keys():
    #     print(f"{i: <30}: {ReFScan.dump_page_header(f, chkpData1[i])}")
    # return 0


if __name__ == "__main__":
    main()
