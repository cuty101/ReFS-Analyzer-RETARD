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
    # data['lcn']=int.from_bytes(lcn, byteorder='big')
    return data

# vol_sig = g1 xor g2 xor g3 xor g4 (used in pages)
def compute_guid(guid, vol_sig):
    data = {
        "guid0": unpack(guid[0:8], "<L"),
        "guid1": unpack(guid[8:16], "<L"),
        "guid2": unpack(guid[16:24], "<L"),
        "guid3": unpack(guid[24:32],"<L"),
    }
    signature = data['guid0'] ^ data['guid1'] ^ data['guid2'] ^ data['guid3']
    if signature==vol_sig:
        message = "Volume header verified to be correct!"
    else:
        message = "Corruption detected!"
    data['message'] = message
    return data

def dump_vbr(f, offset):
    f.seek(offset)
    fData = f.read(4096).hex()
    data = {                                                # Offset    Length  Description
        "fs": fData[6:6+16],                                # 0x03      8       Filesystem Name
        "sectors": unpack(fData[48:48+16], "<Q"),           # 0x18      8       Sectors in volume
        "bytesPerSector": unpack(fData[64:64+8], "<L"),     # 0x20      4       Bytes per sector
        "sectorsPerCluster": unpack(fData[72:72+8], "<L"),  # 0x24      4       Sectors per cluster
        "majVer": unpack(fData[80:82], "<B"),               # 0x28      1       Filesystem Major Version
        "minVer": unpack(fData[82:84], "<B"),               # 0x29      1       Filesystem Minor Version
        "volSerialNum": unpack(fData[112:112+16], "<Q"),    # 0x38      8       Volume Serial Number
        "bytesPerContainer": unpack(fData[128:128+16], "<Q")
    }
    data['totalVol']=data['sectors']*data['bytesPerSector']/(1024**3)
    return data

# Superblock Retrieval
# In cluster 30 of ReFS filesystem
def dump_supb(f, offset, cluster):
    substring="53555042"            # SUPB
    cursor = offset+30*cluster      # Cluster 30 + offset
    f.seek(cursor)
    hexdump = f.read(4096).hex()
    # Failed to find SUPB signature
    if substring!=hexdump[0:8]:
        print("The superblock seems to be in the wrong spot! Performing manual scan!")
        cursor = get_offset(f, substring, offset)
        f.seek(cursor)
        hexdump = f.read(4096).hex()
    pageHeader = dump_page_header(f, cursor)
    data={                                                                      # Offset    Length  Description
        "pageHeader": pageHeader,                                               # 0x00      80      Page Header
        "guidResult":compute_guid(hexdump[160:192], pageHeader['vol_sig']),     # 0x50      16      GUID (Used to compute volume signature)
        "superblockVersion": unpack(hexdump[208:224],"<Q"),                     # 0x68      8       Superblock version (Used to determine recency)
    }
    checkpointPtr = unpack(hexdump[224:232], "<L")*2                            # 0x70      4       Offset to checkpoint references
    checkpointPtr0 = unpack(hexdump[checkpointPtr:checkpointPtr+16], "<Q")      # 0x00      8       0x00 from offset pointed by 0x70
    data['checkpointPtr0'] = hex(checkpointPtr0*cluster+offset)
    checkpointPtr1 = unpack(hexdump[checkpointPtr+16:checkpointPtr+32],"<Q")    # 0x08      8       0x08 from offset pointed by 2nd value pointed by 0x70
    data['checkpointPtr1'] = hex(checkpointPtr1*cluster+offset)
    data['offset'] = hex(cursor)

    return data

def dump_chkp(f, offset, vbrOffset, cluster):
    f.seek(offset)
    hexdump = f.read(4096).hex()

    def getContainerRows(containerPtr):
        rootData, headerData = dump_node_info(f, containerPtr)
        keyOffsetList, containerRows = dump_rows(f, containerPtr, rootData, headerData)
        return keyOffsetList, containerRows

    def getOffsetFromPtr(ptrOffset):
        ptrOffset*=2
        ptr = unpack(hexdump[ptrOffset:ptrOffset+8], "<L")*2
        ptr = hex(unpack(hexdump[ptr:ptr+4],"<H")*cluster+vbrOffset)
        ptr = int(ptr, 16)
        return ptr

    chkpVirtualClock = unpack(hexdump[192:208], "<Q")
    allocVirtualClock = unpack(hexdump[208:224], "<Q")
    oldestLogRecordPtr = unpack(hexdump[224:240], "<Q")

    data = {                                                        # Offset    Length  Description
        "pageHeader": dump_page_header(f, offset),                  # 0x00      80      Page Header
        "majVer": unpack(hexdump[168:174], "<B"),                   # 0x54      2       Filesystem Major Version
        "minVer": unpack(hexdump[172:176], "<B"),                   # 0x56      2       Filesystem Mini Version
        "chkpVirtualClock": hex(chkpVirtualClock),                  # 0x60      8       Checkpoint Virtual Clock, alternates between either CHKP
        "allocVirtualClock": hex(allocVirtualClock),                # 0x68      8       Allocator Virtual Clock, unsure, but counter seems to alternate between CHKP as well
        "oldestLogRecordPtr": hex(oldestLogRecordPtr),              # 0x70      8       Pointer to last log record written
        }
    ptrData = {
        "objIdTable": getOffsetFromPtr(0x94),                       # 0x94      4       Pointer to the Object ID Table Reference
        "medAllocTable": getOffsetFromPtr(0x98),                    # 0x98      4       Pointer to the Medium Allocator Table Reference
        "containerAllocTable": getOffsetFromPtr(0x9c),              # 0x9c      4       Pointer to the Container Allocator Table Reference
        "schemaTable": getOffsetFromPtr(0xa0),                      # 0xa0      4       Pointer to the Schema Table Reference
        "parentChildTable": getOffsetFromPtr(0xa4),                 # 0xa4      4       Pointer to the Parent Child Table Reference
        "objIdTableDup": getOffsetFromPtr(0xa8),                    # 0xa8      4       Pointer to the Object ID Table Reference
        "blockRefCountTable": getOffsetFromPtr(0xac),               # 0xac      4       Pointer to the Block Reference Count Table Reference
        "containerTable": getOffsetFromPtr(0xb0),                   # 0xb0      4       Pointer to the Container Table Reference
        "containerTableDup": getOffsetFromPtr(0xb4),                # 0xb4      4       Pointer to the Container Table Duplicate Reference
        "schemaTableDup": getOffsetFromPtr(0xb8),                   # 0xb8      4       Pointer to the Schema Table Duplicate Reference
        "containerIndexTable": getOffsetFromPtr(0xbc),              # 0xbc      4       Pointer to the Container Index Table Reference
        "integrityStateTable": getOffsetFromPtr(0xc0),              # 0xc0      4       Pointer to the Integrity State Table Reference
        "smallAllocTable": getOffsetFromPtr(0xc4),                  # 0xc4      4       Pointer to the Small Allocator Table Reference
    }
    ptrData.update(ptrData)
    return data, ptrData

def dump_container_table(f, offset):
    rootData, headerData = dump_node_info(f, offset)
    offset = offset+0x50+rootData["size"] # startOfNode + pageHeader + indexRoot = StartOfIndexHeader
    dump_rows(f, offset, rootData, headerData)
    
    data = {
        "rootData": rootData,
        "headerData": headerData,
    }
    
    return data

def dump_schema_table(f, offset):
    f.seek(offset)
    hexdump = f.read(4096).hex()

    data = {
        "pageHeader": dump_page_header(f, offset),
        "schemaID": hexdump[160:168],
        "schemaSize": hexdump[176:184],
    }
    
    print("\n-------------------Schema Table-------------------")
    for x,y in data.items():
        print(f"{x : <30}: {y}")
    return


# Dumps index root and index header for tables
def dump_node_info(f, offset):
    f.seek(offset)
    hexdump = f.read(4096).hex()
    if hexdump[160:168] == "08000000":
        rootData={
            "pageHeader": dump_page_header(f, offset),
            "size": unpack(hexdump[160:168], '<L'),                 # Non root nodes will have size of 8
        }
    else:
        rootData = {                                                # Offset    Length  Description
            "pageHeader": dump_page_header(f, offset),              # 0x00      80      Page Header
            "size": unpack(hexdump[160:168], '<L'),                 # 0x50      4       Size
            "sizeOfFixedComponent": unpack(hexdump[168:172], '<B'), # 0x54      2       Size of the fixed component of the index root (should be 0x28)
            "tableSchema": unpack(hexdump[184:192], '<L'),          # 0x5C      4       Schema of the Table
            "extents": unpack(hexdump[208:224], '<Q'),              # 0x68      8       Number of extents in the table
            "rows": unpack(hexdump[224:240], '<Q'),                 # 0x70      8       Number of rows in the table
        }

    startHeader = rootData["size"] + 0x50
    f.seek(startHeader + offset)
    hexdump = f.read(4096).hex()
    headerData = {                                                  # Offset    Length  Description
        "startData": unpack(hexdump[0:8], '<L'),                    # 0x00      4       Offset to the start of the data area
        "endData": unpack(hexdump[8:16], '<L'),                     # 0x04      4       Offset of the end of the data area
        "freeBytes": unpack(hexdump[16:24], '<L'),                  # 0x08      4       Free bytes in the node
        "height": unpack(hexdump[24:26], '<B'),                     # 0x0c      1       Height of node
        "flag": unpack(hexdump[26:28], '<B'),                       # 0x0d      1       Flag
        "startKey": unpack(hexdump[32:40], '<L'),                   # 0x10      4       Start of the key index
        "keyEntriesCount": unpack(hexdump[40:48], '<L'),            # 0x14      4       Number of entries in the key index
        "endKey": unpack(hexdump[64:72], '<L'),                     # 0x20      4       End of the key index
    }
    return rootData, headerData

def dump_rows(f, offset, rootData, headerData):
    f.seek(offset)
    hexdump=f.read(4096).hex()
    keyIndexOffset = offset+headerData['startKey']
    f.seek(keyIndexOffset)
    hexdump = f.read(4096).hex()
    keyCount = headerData['keyEntriesCount']
    keyOffsetList = []
    containerRows = {}
    for i in range(keyCount):
        x = i*8
        keyIndex = unpack(hexdump[x:x+8], '<L') & 0x0000ffff
        keyOffset = keyIndex+offset
        keyOffsetList.append(keyOffset)

    print("Offset\t\tIndexLen\tKey\tKeyLen\tFlags\tValue\tValueLen")
    for key in keyOffsetList:
        f.seek(key)
        hexdump = f.read(4096).hex() # +4 to get len of next index
        print(f"{hex(key)}\t"
              f"{hex(unpack(hexdump[0:8], '<L'))}\t\t"
              f"{hex(unpack(hexdump[8:12], '<B'))}\t"
              f"{hex(unpack(hexdump[12:16],'<B'))}\t"
              f"{hex(unpack(hexdump[16:20], '<B'))}\t"
              f"{hex(unpack(hexdump[20:24], '<B'))}\t"
              f"{hex(unpack(hexdump[24:28], '<B'))}"
              )
    for key in keyOffsetList:
        f.seek(key)
        hexdump = f.read(4096).hex()  # +4 to get len of next index
        keyValueData = dump_container_key_pair(hexdump)
        containerRows[hex(keyValueData['bandID'])] = {
            "LCN": hex(keyValueData['Container LCN']),
            "Number of Clusters": hex(keyValueData['noOfClusters'])
        }
    print(containerRows)
    return keyOffsetList, containerRows

def dump_container_key_pair(hexdump):
    keyValueData = {
        "bandID": unpack(hexdump[32:32 + 8], "<L"),
        "Container LCN": unpack(hexdump[448:464], "<Q"),
        "noOfClusters": unpack(hexdump[464:480], "<Q"),
    }

    return keyValueData