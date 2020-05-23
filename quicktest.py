
from Drive import Drive
import sys

def main():
    """ Stupid test. """
    x = Drive()
    x.download_directory(f"{sys.argv[1]}", "Carelink_data")
##

if __name__ == "__main__":
    main()
