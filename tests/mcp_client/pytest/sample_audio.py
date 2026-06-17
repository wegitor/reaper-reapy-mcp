import os
import requests
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

# Using a more reliable source for the sample file
SAMPLE_URL = "https://filesamples.com/samples/audio/mp3/sample3.mp3"
SAMPLES_DIR = Path("samples")

def ensure_sample_file() -> str:
    """
    Ensure the sample audio file exists, downloading it if necessary.
    
    Returns:
        str: Path to the sample audio file
    """
    try:
        # Create samples directory if it doesn't exist
        SAMPLES_DIR.mkdir(exist_ok=True)
        
        # Define the local file path
        local_path = SAMPLES_DIR / "sample.mp3"
        
        # Download if file doesn't exist
        if not local_path.exists():
            logger.info(f"Downloading sample audio file from {SAMPLE_URL}")
            
            # Configure requests with timeout and retry
            session = requests.Session()
            retries = 3
            timeout = 30  # seconds
            
            for attempt in range(retries):
                try:
                    response = session.get(SAMPLE_URL, stream=True, timeout=timeout)
                    response.raise_for_status()
                    
                    # Get total file size if available
                    total_size = int(response.headers.get('content-length', 0))
                    
                    with open(local_path, 'wb') as f:
                        if total_size == 0:
                            # If we can't get the total size, just write the content
                            f.write(response.content)
                        else:
                            # Download with progress tracking
                            downloaded = 0
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    # Log progress every 10%
                                    if total_size > 0:
                                        progress = (downloaded / total_size) * 100
                                        if int(progress) % 10 == 0:
                                            logger.info(f"Download progress: {progress:.1f}%")
                    
                    logger.info(f"Sample audio file downloaded to {local_path}")
                    break  # Success, exit retry loop
                    
                except requests.exceptions.RequestException as e:
                    if attempt < retries - 1:  # Don't sleep on the last attempt
                        wait_time = (attempt + 1) * 5  # Exponential backoff
                        logger.warning(f"Download attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        raise  # Re-raise the last exception if all retries failed
        
        if not local_path.exists():
            raise FileNotFoundError("Failed to download sample file after all retries")
            
        return str(local_path)
        
    except Exception as e:
        logger.error(f"Failed to ensure sample audio file: {e}")
        raise 