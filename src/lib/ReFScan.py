import struct

# Function to convert a string to little endian
def unpack(s, type):
    s = bytes.fromhex(s)
    s = struct.unpack_from(type, s)
    return s[0]


# Scans the filesystem for the first hit of a substring
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

# Dump page_header
def dump_page_header(f, cursor):
    f.seek(cursor)
    hexdump = f.read(4096).hex()
    data = {                                            # Offset    Length  Description
        "vol_sig": unpack(hexdump[24:32], "<L"),        # 0x0c      4       Volume Signature
        "lcn0": unpack(hexdump[64:80], "<Q"),           # 0x20      8       Logical Cluster Number 0
        "lcn1": unpack(hexdump[80:96], "<Q"),           # 0x28      8       Logical Cluster Number 1
        "lcn2": unpack(hexdump[96:112],"<Q"),           # 0x30      8       Logical Cluster Number 2
        "lcn3": unpack(hexdump[112:128],"<Q"),          # 0x38      8       Logical Cluster Number 3
        "tableIdHigh": unpack(hexdump[128:144], "<Q"),  # 0x40      8       Table Identifier High
        "tableIdLow": unpack(hexdump[144:160], "<Q"),   # 0x48      8       Table Identifier Low
    }
    lcn0 = struct.pack("<Q", int(hexdump[64:80],16))
    lcn1 = struct.pack("<Q", int(hexdump[80:96],16))
    lcn2 = struct.pack("<Q",int(hexdump[96:112],16))
    lcn3 = struct.pack("<Q",int(hexdump[112:128],16))
    lcn = lcn3+lcn2+lcn1+lcn0
    data["lcn"]=int.from_bytes(lcn)
    return data

# vol_sig = g1 xor g2 xor g3 xor g4 (used in pages)
def compute_guid(guid, vol_sig):
    data = {
        "guid0": unpack(guid[0:8], "<L"),
        "guid1": unpack(guid[8:16], "<L"),
        "guid2": unpack(guid[16:24], "<L"),
        "guid3": unpack(guid[24:32],"<L"),
    }
    signature = data["guid0"] ^ data["guid1"] ^ data["guid2"] ^ data["guid3"]
    if signature==vol_sig:
        message = "Volume header verified to be correct!"
    else:
        message = "Corruption detected!"
    data["message"] = message
    return data

def dump_vbr(f, offset):
    chunk=4096
    f.seek(offset)
    fData = f.read(chunk).hex()
    data = {                                                # Offset    Length  Description
        "fs": fData[6:6+16],                                # 0x03      8       Filesystem Name
        "sectors": unpack(fData[48:48+16], "<Q"),           # 0x18      8       Sectors in volume
        "bytesPerSector": unpack(fData[64:64+8], "<L"),     # 0x20      4       Bytes per sector
        "sectorsPerCluster": unpack(fData[72:72+8], "<L"),  # 0x24      4       Sectors per cluster
        "majVer": unpack(fData[80:82], "<B"),               # 0x28      1       Filesystem Major Version
        "minVer": unpack(fData[82:84], "<B"),               # 0x29      1       Filesystem Minor Version
        "volSerialNum": unpack(fData[112:112+16], "<Q"),    # 0x38      8       Volume Serial Number
    }
    data["totalVol"]=data["sectors"]*data["bytesPerSector"]/(1024**3)
    print(
        "---------------Volume Information---------------\n"
        f"Offset: {hex(offset)}\n"
        f"Sector: {offset/data["bytesPerSector"]:.0f}\n"
        f"Filesystem: {bytearray.fromhex(data["fs"]).decode()}\n"
        f"Number of Sectors: {data["sectors"]}\n"
        f"Bytes per Sector: {data["bytesPerSector"]} Bytes\n"
        f"Sectors per Cluster: {data["sectorsPerCluster"]}\n"
        f"Total space: {data["totalVol"]} GB\n"
        f"ReFS Version: {data["majVer"]}.{data["minVer"]}\n"
        f"Volume Serial Number: {data["volSerialNum"]:X}\n"
        # f"VBR Backup: Offset {hex(offset+sectors*bytesPerSector-bytesPerSector)}"
    )
    return data

# Superblock Retrieval
# In cluster 30 of ReFS filesystem
def dump_supb(f, offset, cluster):
    substring="53555042"            # SUPB
    cursor = offset+30*cluster      # Cluster 30 + offset
    f.seek(cursor)
    hexdump = f.read(cursor).hex()
    # Failed to find SUPB signature
    if substring!=hexdump[0:8]:
        print("The superblock seems to be in the wrong spot! Performing manual scan!")
        cursor = get_offset(f, substring, offset)
        f.seek(cursor)
        hexdump = f.read(cursor).hex()
    pageHeader = dump_page_header(f, cursor)
    data={                                                                      # Offset    Length  Description
        "pageHeader": pageHeader,                                               # 0x00      50      Page Header
        "guidResult":compute_guid(hexdump[160:192], pageHeader["vol_sig"]),     # 0x50      16      GUID (Used to compute volume signature)
        "superblockVersion": unpack(hexdump[208:224],"<Q"),                     # 0x68      8       Superblock version (Used to determine recency)
    }
    checkpointPtr = unpack(hexdump[224:232], "<L")*2                            # 0x70      4       Offset to checkpoint references
    checkpointPtr0 = unpack(hexdump[checkpointPtr:checkpointPtr+16], "<Q")      # 0x00      8       0x00 from offset pointed by 0x70
    data["checkpointPtr0"] = hex(checkpointPtr0*cluster+offset)
    checkpointPtr1 = unpack(hexdump[checkpointPtr+16:checkpointPtr+32],"<Q")    # 0x08      8       0x08 from offset pointed by 2nd value pointed by 0x70
    data["checkpointPtr1"] = hex(checkpointPtr1*cluster+offset)
    print(
        "-------------------Superblock-------------------\n"
        f"Offset: {hex(cursor)}\n"
        f"Volume Signature: {data["pageHeader"]["vol_sig"]:08X}\n"
        f"Logical Cluster Number: {data["pageHeader"]["lcn"]}\n"
        f"Table Identifier: {data["pageHeader"]["tableIdHigh"]:08X}{data["pageHeader"]["tableIdLow"]:08X}\n"
        f"GUID: {data["guidResult"]["guid3"]:04X}{data["guidResult"]["guid2"]:04X}{data["guidResult"]["guid1"]:04X}{data["guidResult"]["guid0"]:04X}\n"
        f"Page status: {data["guidResult"]["message"]}\n"
        f"Superblock Version: {data["superblockVersion"]}\n"
        f"Checkpoint offsets: {checkpointPtr0}, {checkpointPtr1}"
        )
    return data
    
def dump_chkp(f, offset):
    pageHeader = dump_page_header(f, offset)
    print(pageHeader)
    return 0