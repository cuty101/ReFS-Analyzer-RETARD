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
    print(
        "-----------------Checkpoint Data-----------------\n"
        f"Page Header: {data['pageHeader']}\n"
        f"Version: {data['majVer']}.{data['minVer']}\n"
        f"CHKP Virtual Clock: {data['chkpVirtualClock']}\n"
        f"Allocator Virtual Clock: {data['allocVirtualClock']}\n"
        f"Last Log Record Pointer: {data['oldestLogRecordPtr']}\n"
        "---------------End Checkpoint Data---------------\n\n"
        
        "------------------Pointer Data------------------\n"
        f"Object ID Table: {ptrData['objIdTable']}\n"
        f"Medium Allocator Table: {ptrData['medAllocTable']}\n"
        f"Container Allocator Table: {ptrData['containerAllocTable']}\n"
        f"Schema Table: {ptrData['schemaTable']}\n"
        f"Parent Child Table: {ptrData['parentChildTable']}\n"
        f"Object ID Table Duplicate: {ptrData['objIdTableDup']}\n"
        f"Block Reference Count Table: {ptrData['blockRefCountTable']}\n"
        f"Container Table: {ptrData['containerTable']}\n"
        f"Container Table Duplicate: {ptrData['containerTableDup']}\n"
        f"Schema Table Duplicate: {ptrData['schemaTableDup']}\n"
        f"Container Index Table: {ptrData['containerIndexTable']}\n"
        f"Integrity State Table: {ptrData['integrityStateTable']}\n"
        f"Small Allocator Table: {ptrData['smallAllocTable']}\n"
        "----------------End Pointer Data----------------\n"
        )