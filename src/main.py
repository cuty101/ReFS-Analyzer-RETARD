# Local Import
import lib.ReFScan as ReFScan
import lib.dump as dump
import argparse
import traceback

def main():
    # Argument Parser
    parser = argparse.ArgumentParser(description="Scan and analyze a ReFS image file")
    parser.add_argument(
        "-i", "--image", 
        required=True,
        help="Path to the ReFS image file", 
    )
    parser.add_argument(
        "-v", "--vbr",
        action="store_true",
        help="Dump the Volume Boot Record (VBR)",
    )
    parser.add_argument(
        "-s", "--supb",
        action="store_true",
        help="Dump the Superblock (SUPB)",
    )
    parser.add_argument(
        "-c", "--chkp",
        action="store_true",
        help="Dump the Checkpoint (CHKP)",
    )
    parser.add_argument(
        "-ct", "--conTable",
        action="store_true",
        help="Dump the Container Table",
    )

    args = parser.parse_args()

    action = [args.vbr, args.supb, args.chkp, args.conTable]

    if not any(action):
        print("\nError: No action specified. Use -h or --help for help.\n")
        parser.print_help()
        return

    image = args.image
    try:
        with open(image, "rb") as f:
            print (f"Analysing image: {image}")

            vbrOffset = ReFScan.get_offset(f, "52654653000000")                                                     # Get Volume Boot Record (VBR) Offset
            vbrData = ReFScan.dump_vbr(f, vbrOffset)                                                                # VBR Data
            cluster = vbrData["bytesPerSector"] * vbrData["sectorsPerCluster"]                                      # Cluster Size
            supbData = ReFScan.dump_supb(f, vbrOffset, cluster)                                                     # Superblock Data
            chkpData, ptrData = ReFScan.dump_chkp(f, int(supbData["checkpointPtr0"],16), vbrOffset, cluster)        # Checkpoint
            chkpData1, ptrData1 = ReFScan.dump_chkp(f, int(supbData["checkpointPtr1"],16), vbrOffset, cluster)      # 2nd Checkpoint
            containerTable, containerTableRows = ReFScan.dump_container_table(f, ptrData["containerTable"])                             # Container Table

            if args.vbr:
                dump.print_vbr(vbrData, vbrOffset)                                                               # Dump results
            if args.supb:
                dump.print_supb(supbData)                                                                        # Dump Superblock
            if args.chkp:
                print("-----------------Checkpoint 0-----------------\n")
                dump.print_chkp(chkpData, ptrData)                                                               # Dump Checkpoint
                print("-----------------Checkpoint 1-----------------\n")
                dump.print_chkp(chkpData1, ptrData1)                                                             # Dump Checkpoint 1
            if args.conTable:
                dump.print_container_table(containerTable, containerTableRows)                                                        # Dump Container Table
            
    except FileNotFoundError:
        print(f"Error: The file '{image}' was not found.")
    except Exception as e:
        print(f"An error occurred: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
