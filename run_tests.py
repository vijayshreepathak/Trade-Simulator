import pytest
import sys
from src.utils.logging_config import setup_logging

def main():
    # Set up logging
    setup_logging()
    
    # Run tests
    args = [
        "tests",
        "-v",
        "--asyncio-mode=auto"
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main()) 