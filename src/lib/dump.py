def print_vbr(data, offset):
        print(
        "---------------Volume Information---------------\n"
        f"Offset: {hex(offset)}\n"
        f"Sector: {offset/data['bytesPerSector']:.0f}\n"
        f"Filesystem: {bytearray.fromhex(data['fs']).decode()}\n"
        f"Number of Sectors: {data['sectors']}\n"
        f"Bytes per Sector: {data['bytesPerSector']} Bytes\n"
        f"Sectors per Cluster: {data['sectorsPerCluster']}\n"
        f"Total space: {data['totalVol']} GB\n"
        f"ReFS Version: {data['majVer']}.{data['minVer']}\n"
        f"Volume Serial Number: {data['volSerialNum']:X}\n"
        f"Bytes per Container: {data['bytesPerContainer']}\n"
        # f"VBR Backup: Offset {hex(offset+sectors*bytesPerSector-bytesPerSector)}"
        "-------------End Volume Information-------------\n"
    )

def print_supb(data):
        print(
        "-------------------Superblock-------------------\n"
        f"Offset: {data['offset']}\n"
        f"Volume Signature: {data['pageHeader']['vol_sig']:08X}\n"
        f"Logical Cluster Number: {data['pageHeader']['lcn0']}\n"
        f"Table Identifier: {data['pageHeader']['tableIdHigh']:08X}{data['pageHeader']['tableIdLow']:08X}\n"
        f"GUID: {data['guidResult']['guid3']:04X}{data['guidResult']['guid2']:04X}{data['guidResult']['guid1']:04X}{data['guidResult']['guid0']:04X}\n"
        f"Page status: {data['guidResult']['message']}\n"
        f"Superblock Version: {data['superblockVersion']}\n"
        f"Checkpoint offsets: {data['checkpointPtr0']}, {data['checkpointPtr1']}\n"
        "-----------------End Superblock-----------------\n"
        )

def print_chkp(data, ptrData):
    page_header = data['pageHeader']

    print(
        "-----------------Checkpoint Data-----------------\n"
        "Page Header Information:\n"
        f"  Volume Signature      : {page_header['vol_sig']}\n"
        f"  LCN0                  : {page_header['lcn0']}\n"
        f"  LCN1                  : {page_header['lcn1']}\n"
        f"  LCN2                  : {page_header['lcn2']}\n"
        f"  LCN3                  : {page_header['lcn3']}\n"
        f"  Table ID High         : {page_header['tableIdHigh']}\n"
        f"  Table ID Low          : {page_header['tableIdLow']}\n\n"
        f"Version: {data['majVer']}.{data['minVer']}\n"
        f"CHKP Virtual Clock: {data['chkpVirtualClock']}\n"
        f"Allocator Virtual Clock: {data['allocVirtualClock']}\n"
        "---------------End Checkpoint Data---------------\n\n"
        
        "------------------Pointer Data------------------\n"
        f"Object ID Table: {hex(ptrData['objIdTable'])}\n"
        f"Medium Allocator Table: {hex(ptrData['medAllocTable'])}\n"
        f"Container Allocator Table: {hex(ptrData['containerAllocTable'])}\n"
        f"Schema Table: {hex(ptrData['schemaTable'])}\n"
        f"Parent Child Table: {hex(ptrData['parentChildTable'])}\n"
        f"Object ID Table Duplicate: {hex(ptrData['objIdTableDup'])}\n"
        f"Block Reference Count Table: {hex(ptrData['blockRefCountTable'])}\n"
        f"Container Table: {hex(ptrData['containerTable'])}\n"
        f"Container Table Duplicate: {hex(ptrData['containerTableDup'])}\n"
        f"Schema Table Duplicate: {hex(ptrData['schemaTableDup'])}\n"
        f"Container Index Table: {hex(ptrData['containerIndexTable'])}\n"
        f"Integrity State Table: {hex(ptrData['integrityStateTable'])}\n"
        f"Small Allocator Table: {hex(ptrData['smallAllocTable'])}\n"
        "----------------End Pointer Data----------------\n"
        )
    
def print_container_table(data):
    page_header = data['rootData']['pageHeader']
    print(
        "----------------Container Table----------------\n"
        "Page Header Information:\n"
        f"  Volume Signature      : {page_header['vol_sig']}\n"
        f"  LCN0                  : {page_header['lcn0']}\n"
        f"  LCN1                  : {page_header['lcn1']}\n"
        f"  LCN2                  : {page_header['lcn2']}\n"
        f"  LCN3                  : {page_header['lcn3']}\n"
        f"  Table ID High         : {page_header['tableIdHigh']}\n"
        f"  Table ID Low          : {page_header['tableIdLow']}\n\n"
        f"Size of Table: {data['rootData']['size']}\n"
        f"Size of Fixed Component: {data['rootData']['sizeOfFixedComponent']}\n"
        f"Table Schema: {data['rootData']['tableSchema']}\n"
        f"Extent Count: {data['rootData']['extents']}\n"
        f"No. of Rows: {data['rootData']['rows']}\n"
        f"Offset of Start Data: {hex(data['headerData']['startData'])}\n"
        f"Offset of End Data: {hex(data['headerData']['endData'])}\n"
        f"Free Space: {hex(data['headerData']['freeBytes'])}\n"
        f"Height: {hex(data['headerData']['height'])}\n"
        f"Flag: {hex(data['headerData']['flag'])}\n"
        f"Start Key: {hex(data['headerData']['startKey'])}\n"
        f"Key Entries Count: {hex(data['headerData']['keyEntriesCount'])}\n"
        f"End Key: {hex(data['headerData']['endKey'])}\n"
        "--------------End Container Table--------------\n"
    )
