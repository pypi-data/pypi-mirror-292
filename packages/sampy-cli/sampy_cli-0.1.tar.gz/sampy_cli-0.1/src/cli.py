import argparse
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os

# Define the default directory and file path
default_dir = os.path.expanduser("~/.sampy")
default_file = os.path.join(default_dir, "samples.csv")

# Ensure the ~/.sampy directory exists
os.makedirs(default_dir, exist_ok=True)

def add_sample(file, value, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        df = pd.read_csv(file)
        if 'id' in df.columns:
            next_id = df['id'].max() + 1
        else:
            next_id = 1
    except FileNotFoundError:
        df = pd.DataFrame()
        next_id = 1

    new_sample = pd.DataFrame([{
        'id': next_id,
        'value': value,
        'timestamp': timestamp
    }])
    
    df = pd.concat([df, new_sample], ignore_index=True)
    df.to_csv(file, index=False)
    print(f"Sample added: id={next_id}, value={value}, timestamp={timestamp}")

def plot_data(file):
    try:
        df = pd.read_csv(file)
        if df.empty:
            print(f"No data found in {file}.")
            return
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['value'], marker='o', linestyle='-')
        plt.title('Sample Values Over Time')
        plt.xlabel('Timestamp')
        plt.ylabel('Value')
        plt.grid(True)
        plt.show()

    except FileNotFoundError:
        print(f"File {file} not found. Cannot generate plot.")

def main():
    parser = argparse.ArgumentParser(description="A simple CLI tool for creating and plotting samples.")
    subparsers = parser.add_subparsers(dest='command', help="Subcommands")

    parser_add = subparsers.add_parser('add', help="Add a new sample.")
    parser_add.add_argument("value", type=float, help="Value for the sample.")
    parser_add.add_argument("--time", type=str, help="Timestamp for the sample (optional).")
    parser_add.add_argument("--file", type=str, default=default_file, help=f"CSV file to store the samples (default: '{default_file}').")

    parser_plot = subparsers.add_parser('plot', help="Plot the sample data.")
    parser_plot.add_argument("--file", type=str, default=default_file, help=f"CSV file to plot the samples from (default: '{default_file}').")

    args = parser.parse_args()

    if args.command == 'add':
        add_sample(args.file, args.value, args.time)
    elif args.command == 'plot':
        plot_data(args.file)

if __name__ == "__main__":
    main()
