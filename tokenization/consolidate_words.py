import os
import time
import pandas as pd
from collections import defaultdict, Counter
from tqdm import tqdm
from multiprocessing import Pool, cpu_count, Manager
from functools import partial
from clean_description import PodcastDescriptionCleaner

def process_single_row(row, error_counter, desc_column='description', podcast_id_column='podcast_id'):
    """
    Process a single row and return tokenized word counts.
    
    Args:
        row (pd.Series): DataFrame row to process
        error_counter (multiprocessing.Value): Shared counter for errors
        desc_column (str): Column name for description
        podcast_id_column (str): Column name for podcast ID
    
    Returns:
        tuple: (podcast_id, word_counts) or None if processing fails
    """
    try:
        desc = row.get(desc_column)
        podcast_id = row.get(podcast_id_column)
        
        # Skip rows with missing values
        if not isinstance(desc, str) or not isinstance(podcast_id, str):
            return None
        
        # Clean description and tokenize
        tokens = PodcastDescriptionCleaner(desc).clean_description()
        
        return (podcast_id, Counter(tokens))
    
    except Exception as error:
        with error_counter.get_lock():
            error_counter.value += 1
        print(f"Error processing row: {error}")
        return None

def parallel_process_podcast_descriptions(input_csv, output_folder, num_processes=None):
    """
    Parallelize podcast description processing.
    
    Args:
        input_csv (str): Path to input CSV file
        output_folder (str): Folder to save token count files
        num_processes (int, optional): Number of processes to use. Defaults to CPU count.
    """
    # Set default to number of CPU cores if not specified
    if num_processes is None:
        num_processes = cpu_count()
    
    # Ensure the podcast_tokens folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Load your data
    df = pd.read_csv(input_csv, low_memory=False)
    
    # Start timing
    start_time = time.time()
    
    # Use multiprocessing Manager for shared error counter
    with Manager() as manager:
        error_counter = manager.Value('i', 0)  # Shared error counter

        # Use multiprocessing to process rows
        print(f"Processing with {num_processes} processes...")
        with Pool(processes=num_processes) as pool:
            # Partial function to include error_counter
            partial_process_row = partial(process_single_row, error_counter=error_counter)
            
            # Use tqdm to show progress
            results = list(tqdm(
                pool.imap(partial_process_row, [row for _, row in df.iterrows()]), 
                total=len(df), 
                desc="Processing Podcast Descriptions", 
                unit="row", 
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
            ))

        # Remove None values (failed rows)
        results = [r for r in results if r is not None]
        
        # Combine results
        podcast_word_counts = defaultdict(Counter)
        for podcast_id, word_count in results:
            podcast_word_counts[podcast_id].update(word_count)
        
        # Save the word counts for each podcast to a CSV file
        print("\nSaving word count files...")
        for podcast_id, word_count in tqdm(podcast_word_counts.items(), 
                                            desc="Saving Podcast Word Counts", 
                                            unit="podcast"):
            try:
                # Convert to DataFrame and sort by count in descending order
                word_count_df = pd.DataFrame(list(word_count.items()), columns=["Word", "Count"])
                word_count_df = word_count_df.sort_values(by="Count", ascending=False)
                
                # Save to CSV
                file_path = os.path.join(output_folder, f"{podcast_id}.csv")
                word_count_df.to_csv(file_path, index=False)
            
            except Exception as e:
                print(f"Error saving for podcast_id {podcast_id}: {e}")
        
        # Print total processing time and error count
        total_time = time.time() - start_time
        print(f"\nTotal processing time: {total_time:.2f} seconds")
        print(f"Processed {len(results)} podcast descriptions")
        print(f"Total errors encountered: {error_counter.value}")

# Main execution
if __name__ == "__main__":
    input_csv = "combined_episodes.csv"
    output_folder = "podcast_tokens"
    
    # You can specify the number of processes if desired
    # parallel_process_podcast_descriptions(input_csv, output_folder, num_processes=8)
    parallel_process_podcast_descriptions(input_csv, output_folder)
    print("Completed token aggregation and sorting for all podcasts.")
