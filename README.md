# Data-Runner
Forensic tool to decode data runs and extract files from disk images

# DataRunner: Forensic Data Run Analyzer

DataRunner is a powerful forensic analysis tool designed to reconstruct files from data runs extracted from NTFS (New Technology File System) disk images. It simplifies the process of analyzing and piecing together fragmented files, making it an invaluable resource for digital forensics investigators and enthusiasts. This document provides an overview of how to analyze data runs manually and explains how the DataRunner script operates.

## Understanding Data Runs

In NTFS, files can be stored non-contiguously on a disk, leading to fragmentation. Information about where these fragments, or "runs," are located is stored in the file's Master File Table (MFT) entry. Each run specifies a starting cluster (LCN - Logical Cluster Number) and the number of clusters the run spans. Analyzing data runs manually involves interpreting this information to locate and extract the file's fragments.

### Manual Analysis of Data Runs

```
00000000  80 00 00 00 50 00 00 00 01 00 00 00 01 00 01 00  |....P...........|
00000010  00 00 00 00 00 00 00 00 0f 00 00 00 00 00 00 00  |................|
00000020  48 00 04 00 00 00 00 00 00 00 01 00 00 00 00 00  |H...............|
00000030  00 2a 00 00 00 00 00 00 00 2a 00 00 00 00 00 00  |.*.......*......|
00000040  00 20 00 00 00 00 00 00 **21 02 ef 07 01 0e** 00 00  |. ......!.ï.....|
00000050  ff ff ff ff 82 79 47 11 ff ff ff ff 82 79 47 11  |ÿÿÿÿ.yG.ÿÿÿÿ.yG.|
```

**Data Runs Overview:** Each data run entry consists of three main components:

1. **Header**: Indicates the offset size and length size in bytes.
2. **Length**: Specifies the number of clusters the run spans.
3. **Offset**: Indicates the starting cluster (LCN - Logical Cluster Number) for the run. Positive values indicate a forward movement on the disk, while negative values indicate backward movement.

### Example Data Run Analysis

Given data runs:

`Header| Length (Hex -> Dec)  | Offset (Hex -> Dec)        ||    32 | 43 03 -> 0343 (835)  | d1 bd 0b -> 0bbdd1 (769489)||    32 | c2 02 -> 02c2 (706)  | 44 80 01 -> 018044 (98372) ||    21 | 6d    -> 6d (109)    | bf 36    -> 36bf (14015)   ||    21 | 69    -> 69 (105)    | 39 f5    -> f539 (-2759)   ||`

**Step-by-Step Analysis:**

1. **First Run Calculation:**
    
    - **Starting Location**: Multiply the NTFS cluster size (4096 bytes) by the first run's starting LCN.
        - `4096 * 769489 = 3151826944 bytes | BBDD1000`
    - **Length of the Run**: Multiply the NTFS cluster size by the run's length in clusters.
        - `4096 * 835 = 3420160 bytes | 343000`
    - **End Point**: Add the starting location to the length of the run and subtract 1.
        - `3151826944 + 3420160 - 1 = 3155247103 bytes | BC113FFF`
2. **Second Run Calculation:**
    
    - **Starting Point**: Add the offset of the second run to the LCN of the first run to calculate the new LCN.
        - `769489 + 98372 = 867861`
        - Convert to bytes: `867861 * 4096 = 3554758656 bytes | D3E15000`
    - **End Point**: Add the length of the run to the starting point and subtract 1.
        - `3554758656 + (706 * 4096) - 1 = 3557650431 bytes | D40D6FFF`
3. **Third Run Calculation:**
    
    - **Starting Point**: Calculate the LCN by adding the offset of the third run to the LCN of the second run.
        - `867861 + 14015 = 881876`
        - Convert to bytes: `881876 * 4096 = 3612164096 bytes | D74D4000`
    - **End Point**: Add the length of the run to the starting point and subtract 1.
        - `3612164096 + (109 * 4096) - 1 = 3612610559 bytes | D7540FFF`
4. **Fourth Run Calculation:**
    
    - **Starting Point**: Adjust the LCN by adding the negative offset of the fourth run to the LCN of the third run.
        - `881876 + (-2759) = 879117`
        - Convert to bytes: `879117 * 4096 = 3600863232 bytes | D6A0D000`
    - **End Point**: Add the length of the run to the starting point and subtract 1.
        - `3600863232 + (105 * 4096) - 1 = 3601293311 bytes | D6A75FFF`

### Understanding Offsets:

- Offsets can be positive or negative. A positive offset indicates that the run starts forward from the previous LCN, while a negative offset indicates a backward movement.
- Offsets are interpreted based on their first bit. If the first bit is 1 (in binary representation), the number is negative. Otherwise, it's positive.

### Manual Reconstruction:

Following the above steps allows for the manual calculation of start and end points for each data run. To reconstruct the file, extract data from each calculated start point to the end point from the disk image and concatenate these segments in order.
    

## How DataRunner Works

DataRunner automates the manual process described above, providing a user-friendly interface for analyzing data runs and reconstructing files from NTFS disk images.

### Features

- **Data Run Analysis**: Automatically interprets hexadecimal data run information, calculating start and end points for each run.
- **File Reconstruction**: Reconstructs files from specified data runs, handling fragmented files spread across different locations on the disk.
- **Output Customization**: Allows users to specify the output file's name and location.
- **Cluster Size Customization**: Supports specifying a custom cluster size for analysis.
- **Verbose Mode**: Offers a verbose mode for detailed output, aiding in understanding the process and for debugging purposes.

### Usage

1. **Install Dependencies**: Ensure you have Python installed on your system. DataRunner requires no external dependencies beyond the Python standard library.
    
2. **Prepare Data Run Information**: Extract the hexadecimal data run information for the file you wish to reconstruct from the NTFS MFT entry.
    
3. **Run DataRunner**: Use the command line to run DataRunner, providing the data run information and, optionally, the path to the disk image and output file settings.
    
    Example command to analyze data runs and print start/end points:
    
    `python datarunner.py -dr "324303d1bd0b32c202448001216dbf36216939f52169d2f721600603315fd0f2fe315ec50f01211662a4"`
    
    Example command to reconstruct a file from a disk image:
    
    `python datarunner.py -dr "data run hex string" -f "/path/to/image.dd" -o "/path/to/output/file"`
    
4. **Review Output**: DataRunner will print detailed information about the analyzed data runs and save the reconstructed file to the specified location.
