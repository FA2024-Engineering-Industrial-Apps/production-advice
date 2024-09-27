import time
import csv

# Function to generate CSV from given input and save with timestamped filename
def create_csv_from_input(input_data):
    # Split the input data by lines and process each line
    data = []
    for line in input_data.strip().split('\n'):
        # Split each line by the first comma only, to keep PCBs grouped together after the first item
        group, pcbs = line.split(',', 1)
        data.append([group, pcbs])

    # Generate timestamp for the file name
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_path = f'./output/user_selected_pcbs_{timestamp}.csv'

    # Write to CSV file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerows(data)

    return file_path

# def create_csv_alles_combinations(input_data):
    
# def fetch_and_clean_data(url):
#     # Fetch data from URL here, and then clean it up.
#     return data