import struct

def unpack(s, type):
    s = bytes.fromhex(s)
    s = struct.unpack_from(type, s)
    return s[0]

def get_offset(f, substring, cursor=0):
    print(f"Scanning filesystem for {substring}!")
    f.seek(cursor)
    i=0
    while True:
        fData = f.read(4096)
        hexDump = fData.hex()
        if substring in hexDump:
            offset = cursor+i*4096
            print("Hit!")
            break
        if not fData:
            print("Cannot find a match!")
            offset=-1
            break
        i+=1
    return offset

# vol_sig = g1 xor g2 xor g3 xor g4 (used in pages)
def compute_guid(guid, vol_sig):
    guid0 = unpack(guid[0:8], "<L")
    guid1 = unpack(guid[8:16], "<L")
    guid2 = unpack(guid[16:24], "<L")
    guid3 = unpack(guid[24:32],"<L")
    signature = guid0 ^ guid1 ^ guid2 ^ guid3
    if signature==vol_sig:
        message = "Volume header verified to be correct!"
    else:
        message = "Corruption detected!"
    return guid0, guid1, guid2, guid3, message

# VBR Retrieval
# Scan for 52 65 46 53 00 00 00 (identification of start of VBR)
# def get_vbr_offset(f):
#     chunk=4096
#     substring = "52654653000000"
#     i = 0
    
#     # Start scanning image
#     print("Scanning filesystem!")
#     while True:
#         fData = f.read(chunk)
#         hexDump = fData.hex()
#         # print(".", end="")
#         if substring in hexDump:
#             code = i * chunk
#             break
#         if not fData:
#             message = "!!!EOF!!!\nThis does not seem to be an ReFS formatted drive!"
#             code = -1
#             break
#         i += 1
#     return code

def dump_vbr(f, offset):
    chunk=4096
    f.seek(offset)
    fData = f.read(chunk).hex()                             # Offset    Length  Description
    fs = fData[6:6+16]                                      # 0x03      8       Filesystem Name
    sectors = unpack(fData[48:48+16], "<Q")                 # 0x18      8       Sectors in volume
    bytesPerSector = unpack(fData[64:64+8], "<L")           # 0x20      4       Bytes per sector
    sectorsPerCluster = unpack(fData[72:72+8], "<L")        # 0x24      4       Sectors per cluster
    majVer = unpack(fData[80:82], "<B")                     # 0x28      1       Filesystem Major Version
    minVer = unpack(fData[82:84], "<B")                     # 0x29      1       Filesystem Minor Version
    volSerialNum = unpack(fData[112:112+16], "<Q")          # 0x38      8       Volume Serial Number
    totalVol = sectors*bytesPerSector/(1024**3)
    
    print(
        "---------------Volume Information---------------\n"
        f"Offset: {hex(offset)}\n"
        f"Sector: {offset/bytesPerSector:.0f}\n"
        f"Filesystem: {bytearray.fromhex(fs).decode()}\n"
        f"Number of Sectors: {sectors}\n"
        f"Bytes per Sector: {bytesPerSector} Bytes\n"
        f"Sectors per Cluster: {sectorsPerCluster}\n"
        f"Total space: {totalVol} GB\n"
        f"ReFS Version: {majVer}.{minVer}\n"
        f"Volume Serial Number: {volSerialNum:X}\n"
        # f"VBR Backup: Offset {hex(offset+sectors*bytesPerSector-bytesPerSector)}"
    )
    return bytesPerSector, sectorsPerCluster

# Superblock Retrieval
# In cluster 30 of ReFS filesystem
def dump_supb(f, offset, cluster):
    substring="53555042"
    cursor = offset+30*cluster
    f.seek(cursor)
    hexdump = f.read(cursor).hex()
    if substring!=hexdump[0:8]:
        print("The superblock seems to be in the wrong spot! Performing manual scan!")
        cursor = get_offset(f, substring, offset)
        f.seek(cursor)
        hexdump = f.read(cursor).hex()
    vol_sig = unpack(hexdump[24:32], "<L")
    lcn01 = unpack(hexdump[64:96], "<Q")
    lcn23 = unpack(hexdump[96:128],"<Q")
    tableIdHigh = unpack(hexdump[128:144], "<Q")
    tableIdLow = unpack(hexdump[144:160], "<Q")
    guid0, guid1, guid2, guid3, message=compute_guid(hexdump[160:192], vol_sig)
    superblockVersion = unpack(hexdump[208:224],"<Q")
    checkpointPtr=unpack(hexdump[224:232], "<L")*2
    checkpointPtr0 = unpack(hexdump[checkpointPtr:checkpointPtr+16], "<Q")
    checkpointPtr0 = hex(checkpointPtr0*cluster+offset)
    checkpointPtr1 = unpack(hexdump[checkpointPtr+16:checkpointPtr+32],"<Q")
    checkpointPtr1 = hex(checkpointPtr1*cluster+offset)
    
    print(
        "-------------------Superblock-------------------\n"
        f"Offset: {hex(cursor)}\n"
        f"Volume Signature: {vol_sig:08X}\n"
        f"Logical Cluster Number: {"" if not 0 else lcn23}{lcn01}\n"
        f"Table Identifier: {tableIdHigh:08X}{tableIdLow:08X}\n"
        f"GUID: {guid3:04X}{guid2:04X}{guid1:04X}{guid0:04X}\n"
        f"Page status: {message}\n"
        f"Superblock Version: {superblockVersion}\n"
        f"Checkpoint offsets: {checkpointPtr0}, {checkpointPtr1}"
        )