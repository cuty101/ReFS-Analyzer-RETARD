import struct

def read_vbr(f):
    # Read Volume Boot Record (VBR) to find the cluster offset
    f.seek(0x30)  # Offset in VBR for the cluster size
    cluster = struct.unpack("<H", f.read(2))[0]
    print(f"Cluster size: {cluster} bytes")
    return cluster

def getOffsetFromPtr(ptr, vbrOffset, cluster):
    # Translate pointer to file offset
    return (ptr * cluster) + vbrOffset

def dump_chkp(f, vbrOffset, cluster):
    # Go to checkpoint region
    f.seek(vbrOffset + 0x1000)
    chkpData = f.read(4096)
    
    objIdTable = struct.unpack("<Q", chkpData[0x94:0x9C])[0]
    medAllocTable = struct.unpack("<Q", chkpData[0x9C:0xA4])[0]
    containerAllocTable = struct.unpack("<Q", chkpData[0xA4:0xAC])[0]

    # Converting pointers to offsets
    objIdTableOffset = getOffsetFromPtr(objIdTable, vbrOffset, cluster)
    medAllocTableOffset = getOffsetFromPtr(medAllocTable, vbrOffset, cluster)
    containerAllocTableOffset = getOffsetFromPtr(containerAllocTable, vbrOffset, cluster)

    print("Checkpoint Data:")
    print(f"Object ID Table Pointer: {hex(objIdTable)} (Offset: {hex(objIdTableOffset)})")
    print(f"Medium Allocator Table Pointer: {hex(medAllocTable)} (Offset: {hex(medAllocTableOffset)})")
    print(f"Container Allocator Table Pointer: {hex(containerAllocTable)} (Offset: {hex(containerAllocTableOffset)})")

    return {
        "objIdTable": objIdTableOffset,
        "medAllocTable": medAllocTableOffset,
        "containerAllocTable": containerAllocTableOffset
    }

def dump_assigned_tables(f, chkpData, vbrOffset, cluster):
    # Access the specific tables at the pointers for 0x94 - 0x9C
    objIdTablePtr = chkpData.get("objIdTable")
    medAllocTablePtr = chkpData.get("medAllocTable")
    containerAllocTablePtr = chkpData.get("containerAllocTable")

    # Read and display headers or sample data from these locations
    print("\n-------- Assigned Tables Dump --------")
    for name, ptr in [("Object ID Table", objIdTablePtr), 
                      ("Medium Allocator Table", medAllocTablePtr), 
                      ("Container Allocator Table", containerAllocTablePtr)]:
        if ptr != -1:
            f.seek(ptr)
            hexdump = f.read(64).hex()  # Read first 64 bytes for preview
            print(f"{name} at {hex(ptr)}: {hexdump}")
        else:
            print(f"{name} pointer not found or invalid.")

def main(file_path):
    with open(file_path, "rb") as f:
        # Read VBR to determine cluster size
        cluster = read_vbr(f)

        # Assuming a VBR offset (often zero for simple cases)
        vbrOffset = 0x0

        # Dump checkpoint information
        chkpData = dump_chkp(f, vbrOffset, cluster)

        # Dump assigned table sections
        dump_assigned_tables(f, chkpData, vbrOffset, cluster)

# Replace 'your_file_path' with the path to your ReFS filesystem image
main("your_file_path")
