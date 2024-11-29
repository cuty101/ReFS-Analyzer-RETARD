import os, struct

# Local Import
import lib.ReFScan as ReFScan
import argparse

def main():
    # Argument Parser
    parser = argparse.ArgumentParser(description="Scan and analyze a ReFS image file")
    parser.add_argument(
        "-i", "--image", 
        required=True,
        help="Path to the ReFS image file", 
    )
    args = parser.parse_args()

    image = args.image
    try:
        with open(image, "rb") as f:

            vbrOffset = ReFScan.get_offset(f, "52654653000000")                                         # Get Volume Boot Record
            vbrData = ReFScan.dump_vbr(f, vbrOffset)                                                    # Dump results
            cluster = vbrData["bytesPerSector"]*vbrData["sectorsPerCluster"]                            # Cluster size
            supbData = ReFScan.dump_supb(f, vbrOffset, cluster)                                         # Dump Superblock
            chkpData = ReFScan.dump_chkp(f, int(supbData["checkpointPtr0"],16), vbrOffset, cluster)     # Checkpoint
            chkpData1 = ReFScan.dump_chkp(f, int(supbData["checkpointPtr1"],16), vbrOffset, cluster)    # 2nd Checkpoint
            containerTable = ReFScan.dump_container_table(f, chkpData["containerTable"])
            smallAllocTable = ReFScan.dump_container_table(f, chkpData["smallAllocTable"])
            # schemaTable = ReFScan.dump_schema_table(f, chkpData["schemaTable"])
            
            # print("\n\n")
            # for i in chkpData.keys():
            #     print(f"{i: <30}: {ReFScan.dump_page_header(f, chkpData[i])}")
            # print("\n\n")
            # for i in chkpData1.keys():
            #     print(f"{i: <30}: {ReFScan.dump_page_header(f, chkpData1[i])}")
            # return 0
    except FileNotFoundError:
        print(f"Error: The file '{image}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
