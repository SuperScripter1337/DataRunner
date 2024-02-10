# Data-Runner
Forensic tool to decode data runs and extract files from disk images

# DataRunner: Forensic Data Run Analyzer

DataRunner is a powerful forensic analysis tool designed to reconstruct files from data runs extracted from NTFS (New Technology File System) disk images. It simplifies the process of analyzing and piecing together fragmented files, making it an invaluable resource for digital forensics investigators and enthusiasts. This document provides an overview of how to analyze data runs manually and explains how the DataRunner script operates.

## Understanding Data Runs

In NTFS, files can be stored non-contiguously on a disk, leading to fragmentation. Information about where these fragments, or "runs," are located is stored in the file's Master File Table (MFT) entry. Each run specifies a starting cluster (LCN - Logical Cluster Number) and the number of clusters the run spans. Analyzing data runs manually involves interpreting this information to locate and extract the file's fragments.

### Manual Analysis of Data Runs

1. **Extract Data Runs**: First, extract the data run information from the MFT entry of the file you're interested in. This information is in hexadecimal format, indicating the length and offset of each run.
    
2. **Interpret Data Runs**: Convert the hexadecimal values to decimal to understand the starting cluster and length of each run. Pay special attention to the offset values, as they can be positive (indicating forward movement on the disk) or negative (indicating backward movement).
    
3. **Calculate Cluster Locations**: Using the NTFS cluster size (commonly 4096 bytes), calculate the byte offset of each run's starting cluster. This will tell you where to start reading from the disk image.
    
4. **Extract File Fragments**: For each run, extract the specified number of clusters starting from the calculated byte offset. This step requires accessing the disk image file.
    
5. **Reconstruct the File**: Concatenate the extracted file fragments in the order they appear in the data run list to reconstruct the original file.
    

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
    
    arduinoCopy code
    
    `python datarunner.py -dr "324303d1bd0b32c202448001216dbf36216939f52169d2f721600603315fd0f2fe315ec50f01211662a4"`
    
    Example command to reconstruct a file from a disk image:
    
    arduinoCopy code
    
    `python datarunner.py -dr "data run hex string" -f "/path/to/image.dd" -o "/path/to/output/file"`
    
4. **Review Output**: DataRunner will print detailed information about the analyzed data runs and save the reconstructed file to the specified location.
