import argparse
import sys
import os

def preprocess_hex_string(data_runs_hex):
    if " " not in data_runs_hex:
        data_runs_hex = ' '.join(data_runs_hex[i:i+2] for i in range(0, len(data_runs_hex), 2))
    return data_runs_hex

def correct_signed_offset(hex_str):
    bin_str = bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)
    if bin_str[0] == '1':
        return -((1 << len(bin_str)) - int(bin_str, 2))
    else:
        return int(bin_str, 2)

def extract_and_correct_runs_v3(data_runs_hex):
    data_runs_hex = preprocess_hex_string(data_runs_hex)
    parts = data_runs_hex.split(" ")
    runs = []
    i = 0
    print("Detailed calculations for each run:")
    while i < len(parts):
        header = parts[i]
        offset_size = int(header[0], 16)
        length_size = int(header[1], 16)
        i += 1
        length_hex = "".join(parts[i:i + length_size][::-1])
        length = int(length_hex, 16)
        i += length_size
        offset_hex = "".join(parts[i:i + offset_size][::-1])
        offset = correct_signed_offset(offset_hex) if offset_size > 0 else 0
        i += offset_size

        # Print detailed calculation for the current run
        print(f"Header: {header}, Length: {length_hex} - {length} | Offset: {offset_hex} - {offset}")

        runs.append({
            "header": header,
            "length": length,
            "offset": offset,
            "length_hex": length_hex,
            "offset_hex": offset_hex,
        })

    return runs


NTFS_CLUSTER_SIZE = 4096

def calculate_start_end_points(runs):
    current_lcn = 0
    results = []
    for run in runs:
        length = run['length']
        offset = run['offset']
        if results:
            current_lcn += offset
        else:
            current_lcn = offset
        start_point = NTFS_CLUSTER_SIZE * current_lcn
        end_point = start_point + (NTFS_CLUSTER_SIZE * length) - 1
        results.append({
            'run_number': len(results) + 1,
            'start_point_dec': start_point,
            'end_point_dec': end_point,
            'start_point_hex': format(start_point, 'X'),
            'end_point_hex': format(end_point, 'X'),
            'LCN': current_lcn
        })
    return results

def reconstruct_file_from_runs(dd_file_path, runs, output_file_path, verbose):
    try:
        with open(dd_file_path, 'rb') as dd_file:
            with open(output_file_path, 'wb') as output_file:
                for run in runs:
                    start_point = run['start_point_dec']
                    end_point = run['end_point_dec']
                    length = end_point - start_point + 1
                    dd_file.seek(start_point)
                    data_segment = dd_file.read(length)
                    output_file.write(data_segment)
                    if verbose:
                        print(f"Writing segment: Start {start_point}, End {end_point}, Length {length}")
        print(f"Reconstructed file saved as: {output_file_path}")
    except IOError as e:
        print(f"Error accessing file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Forensic Tool for Reconstructing Files from Data Runs.")
    parser.add_argument("-dr", "--datarun", help="Hexadecimal string of the data run.", required=True)
    parser.add_argument("-f", "--file", help="Path to the .dd file to carve from.", required=False)
    parser.add_argument("-o", "--output", help="Output file path for the reconstructed file.", default="reconstructed_file.bin")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-c", "--clustersize", help="Cluster size in bytes. Default is 4096 bytes.", type=int, default=4096)
    
    args = parser.parse_args()

    global NTFS_CLUSTER_SIZE
    NTFS_CLUSTER_SIZE = args.clustersize

    if args.verbose:
        print(f"Verbose mode enabled. Using cluster size: {NTFS_CLUSTER_SIZE} bytes")

    if not args.datarun:
        print("Data run is required. Use -dr to specify the data run.")
        sys.exit(1)

    try:
        corrected_runs = extract_and_correct_runs_v3(args.datarun)
        start_end_points = calculate_start_end_points(corrected_runs)

        if args.file:
            if not os.path.isfile(args.file):
                raise FileNotFoundError(f"File {args.file} does not exist.")
            if args.verbose:
                print(f"Starting file reconstruction from {args.file}...")
            reconstruct_file_from_runs(args.file, start_end_points, args.output, args.verbose)
        else:
            print("Calculated start and end points for each run:")
            for result in start_end_points:
                print(f"Run {result['run_number']}: Starting Location = {result['start_point_dec']} | {result['start_point_hex']}, "
                      f"End Point = {result['end_point_dec']} | {result['end_point_hex']}, LCN = {result['LCN']}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
