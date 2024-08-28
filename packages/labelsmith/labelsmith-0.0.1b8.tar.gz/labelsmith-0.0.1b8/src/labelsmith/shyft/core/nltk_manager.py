import nltk
from nltk.corpus import wordnet
from pathlib import Path
import logging
import sys
import zipfile
import os
from labelsmith.shyft.constants import APP_DATA_DIR

logger = logging.getLogger("labelsmith")

sys.path.append(APP_DATA_DIR)

def ensure_nltk_data():
    nltk_data_path = APP_DATA_DIR / "nltk_data"
    nltk.data.path.append(str(nltk_data_path))
    logger.debug(f"NLTK data path: {nltk.data.path}")

    wordnet_dir = nltk_data_path / "corpora" / "wordnet"
    wordnet_zip = nltk_data_path / "corpora" / "wordnet.zip"

    if not wordnet_dir.exists():
        try:
            # Download WordNet
            nltk.download("wordnet", download_dir=nltk_data_path)
            logger.info("WordNet data downloaded successfully.")
            
            # Unzip the wordnet.zip file
            if wordnet_zip.exists():
                with zipfile.ZipFile(wordnet_zip, 'r') as zip_ref:
                    zip_ref.extractall(nltk_data_path / "corpora")
                logger.info("WordNet data unzipped successfully.")
                # Optionally remove the zip file if space is a concern
                # os.remove(wordnet_zip)
            else:
                logger.warning(f"wordnet.zip file not found at {wordnet_zip}. Skipping unzip step.")
        except Exception as e:
            logger.error(f"Failed to download or extract WordNet data: {e}")
            return False

    # Verify that WordNet can be loaded
    try:
        wordnet.synsets('test')
        logger.info("WordNet data loaded successfully.")
        return True
    except LookupError as e:
        logger.error(f"WordNet data not found or corrupted: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error loading WordNet: {e}")
        return False

def initialize_nltk():
    if ensure_nltk_data():
        logger.info("NLTK WordNet is ready for use.")
        return True
    else:
        logger.warning("NLTK WordNet is not available. Dictionary feature will be disabled.")
        return False