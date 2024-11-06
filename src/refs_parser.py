import os
import struct

# Local Import
import lib.ReFScan as ReFScan

def main():
    # Provide the path to your ReFS image file
    # Example path (uncomment and replace as needed):
    # image = r"\\.\D:/VM/ReFS/ReFS-0-flat.vmdk"
    # image = r"\\.\D:\Virtual Machines\Windows 10 x64/ReFS-flat.vmdk"
    # image = r"\\.\D:"
    # image = r"\\.\C:/Users/yhcha/Documents/Virtual Machines/Windows 10 x64/Windows 10-x64-0-ReFS-flat.vmdk"
    
   
    if 'image' not in locals():
        print("Error: Please set the path to your ReFS image file.")
        return 1

    try:
        with open(image, "rb") as f:  # Open the ReFS image
            vbrOffset = ReFScan.get_offset(f, "52654653000000")  # Get Volume Boot Record offset
            vbrData = ReFScan.dump_vbr(f, vbrOffset)             # Dump VBR results
            cluster = vbrData["bytesPerSector"] * vbrData["sectorsPerCluster"]  # Calculate cluster size
            
            # Dump other ReFS structures
            supbData = ReFScan.dump_supb(f, vbrOffset, cluster)                     # Dump Superblock
            chkpData = ReFScan.dump_chkp(f, int(supbData["checkpointPtr0"], 16), vbrOffset, cluster)  # First Checkpoint
            chkpData1 = ReFScan.dump_chkp(f, int(supbData["checkpointPtr1"], 16), vbrOffset, cluster) # Second Checkpoint
            
           
            print("\nFirst Checkpoint Data:\n")
            for i in chkpData.keys():
                print(f"{i: <30}: {ReFScan.dump_page_header(f, chkpData[i])}")

            print("\nSecond Checkpoint Data:\n")
            for i in chkpData1.keys():
                print(f"{i: <30}: {ReFScan.dump_page_header(f, chkpData1[i])}")
                
            print("\nProcessing Specific Fields (0x94 - 0xa0):\n")
            obj_id_table_ref = ReFScan.extract_field(f, vbrOffset + 0x94, 8)
            container_alloc_table_ref = ReFScan.extract_field(f, vbrOffset + 0x9C, 8)
            print(f"Object ID Table Reference (0x94): {obj_id_table_ref}")
            print(f"Container Allocator Table Reference (0x9C): {container_alloc_table_ref}")

    except FileNotFoundError:
        print(f"Error: File '{image}' not found.")
        return 1

    return 0

if __name__ == "__main__":
    main()
