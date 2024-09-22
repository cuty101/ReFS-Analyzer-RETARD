import os, struct

def unpack(s, type):
    s = bytes.fromhex(s)
    s = struct.unpack_from(type, s)
    return s[0]

# Scan for 00 00 00 52 65 46 53 (identification of start of VBR)
def get_vbr_offset(f, chunk=4096):
    substring = "00000052654653"
    i = 0
    
    # Start scanning image
    print("Scanning filesystem!")
    while True:
        fData = f.read(chunk)
        hexDump = fData.hex()
        # print(".", end="")
        if substring in hexDump:
            code = i * chunk
            message = f"\nReFS filesystem starts at offset {hex(i)}"
            break
        if not fData:
            message = "!!!EOF!!!\nThis does not seem to be an ReFS formatted drive!"
            code = -1
            break
        i += 1
    print(message)
    return code

def dump_vbr(f, offset, chunk=4096):
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
        "---------------Volume Information---------------\n"+
        f"Filesystem: {bytearray.fromhex(fs).decode()}\n"+
        f"Number of Sectors: {sectors}\n"+
        f"Bytes per Sector: {bytesPerSector} Bytes\n"+
        f"Sectors per Cluster: {sectorsPerCluster}\n"+
        f"Total space: {totalVol} GB\n"+
        f"ReFS Version: {majVer}.{minVer}\n"
        f"Volume Serial Number: {volSerialNum:X}"
    )
    return


def main():
    image = "D:/VM/ReFS/drivebackups/1addtest.txt/ReFS-0-flat.vmdk"
    # image = "D:/VM/ReFS/drivebackups/0cleandrive/ReFS-0-flat.vmdk"
    f = open(image, "rb")
    vbrOffset = get_vbr_offset(f)
    dump_vbr(f, vbrOffset)
    f.close()
    return 0


if __name__ == "__main__":
    main()
