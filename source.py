def process_subtitle_file(filename: str):
    """
    Processes the subtitle file. 
    Returns True on success, False on failure.
    """
    if not filename or not filename.endswith('.srt'):
        print(f"\n[ERROR] Invalid input. Please provide a valid .srt file name.")
        return False

    print(f"\n--- Attempting to process subtitle file: {filename} ---")
    # In a real application, you would add logic here to read the file,
    # parse it, and perform the necessary actions.
    print(f"--- Successfully processed {filename}. Next step... ---")
    return True