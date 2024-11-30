# ICT3215-ReFS-Analyzer
## Reliable Extraction Tool for Accurate ReFS Data (RETARD)
This tool scans and analyzes Resilient File System (ReFS) image files, extracting and dumping critical filesystem structures 
such as the Volume Boot Record (VBR), Superblock (SUPB), Checkpoint (CHKP), and Container Table. It provides insights into 
the internal layout of ReFS images, facilitating data recovery, forensic analysis, and debugging.

## Features
- Dump Volume Boot Record (VBR): Extracts and displays details about the filesystem, including cluster size, sectors per cluster, and version.
- Dump Superblock (SUPB): Retrieves and displays metadata about the filesystem, including pointers to checkpoints.
- Dump Checkpoint (CHKP): Extracts and displays checkpoint information, including pointers to various tables.
- Dump Container Table: Provides details about data containers, allocation tables, and more.
- Flexible and modular design for future expansion (e.g., schema table parsing).

## Requirements
- Python 3.1x

## Usage
```Shell
usage: main.py [-h] -i IMAGE [-v] [-s] [-c] [-ct]
```

### Options (Minimum 1 Required)
|  Argument  | Description |
| ---------  | ----------- |
| -v, --vbr | Dump the Volume Boot Record (VBR). |
| -s, --supb | Dump the Superblock (SUPB) |
| -c, --chkp | Dump the Checkpoint (CHKP) |
| -ct, --containerTable | Dump the Container Table |

### Example Usage
```Shell
python main.py -i path/ReFS-flat.vmdk -v -s
```

## File Structure
```bash
.
├── main.py              # Main script to run the tool
├── lib/
│   ├── ReFScan.py       # Core library for parsing ReFS structures
│   ├── dump.py          # Functions for pretty-printing the extracted data
└── README.md            # Documentation
```
