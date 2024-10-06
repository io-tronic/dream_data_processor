import csv
import wave
import numpy as np
import argparse
from tqdm import tqdm

def csv_to_wav(csv_file, sample_rate, columns, output_file, interp):
    print(f"Reading columns {columns} from file")
    # Read CSV data
    data = []
    with open(csv_file, 'r') as file:
        total_rows = sum(1 for _ in file)  # Get total number of rows in the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        i = 0
        for row in tqdm(reader, total=total_rows, desc='Loading from File'):
            if row:
                row_data = []
                for column in columns:
                    if len(row) > column and row[column].strip():  # Ignore empty values in the specified column
                        try:
                            row_data.append(float(row[column]))
                        except ValueError:
                            print(f"non-numerical data on row {i}")
                            pass
                if row_data:
                    data.append(row_data)
                else:
                    print(f"skipping row {i+1}")
            i += 1

    # Convert data to numpy array
    data = np.array(data)

    # Scale the data if requested
    if interp:
        min_int16 = np.iinfo(np.int16).min
        max_int16 = np.iinfo(np.int16).max
        for column in range(data.shape[1]):
            column_data = data[:, column]
            min_value = np.min(column_data)
            max_value = np.max(column_data)
            print(f"scaling data in column {column} from {min_value},{max_value} to {min_int16},{max_int16}")
            column_data = np.interp(column_data, (min_value, max_value), (min_int16, max_int16))
            data[:, column] = column_data

    # Create WAV file
    with wave.open(output_file, 'w') as wav_file:
        print("Writing wav file")
        wav_file.setnchannels(len(columns))  # Number of channels
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data.astype(np.int16).tobytes())

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Convert CSV data to WAV file')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('sample_rate', type=float, help='Sample rate in Hz')
    parser.add_argument('output_file', help='Path to the output WAV file')
    parser.add_argument('-c', '--columns', nargs='+', type=int, help='Column indices to convert')
    parser.add_argument('-s', '--scale', action='store_true', help='Scale the data between min/max signed 16-bit values')
    args = parser.parse_args()

    # Call the conversion function
    csv_to_wav(args.csv_file, args.sample_rate, args.columns, args.output_file, args.scale)