# -*- coding: utf-8 -*-
'''Download pre-build MMseqs pmaf profile DB files.'''
import os
import sys
import logging

# This logger will used for the main
logger: logging.Logger = logging.getLogger()



########### FUNCTIONS ############
def get_params():
    """Parse and analyse command line parameters."""
    # define the parameter list
    import argparse
    parser = argparse.ArgumentParser(description="Download PFam profile DBs", usage='%(prog)s', prog='get-pfam-profiles')
    #start adding the command line options
    parser.add_argument('-o', '--output-directory', type=str, required=True, help='Directory in which the results will be stored.', default='')

    parser.add_argument('-d', '--debug', required=False, help='Output debug information.', default=False, action='store_true')
    # return list with params
    return parser.parse_args()



def download_pfam_profiles(file_id: str, outpath: str):
    """Download the profile database from GDrive"""
    logging.debug("download_pfam_profiles :: START")
    logging.debug(f"GDrive file ID: {file_id}")
    logging.debug(f"Output path: {outpath}")

    import gdown

    '''
    gdown is a python package to download files from Google Drive
    pypi page: https://pypi.org/project/gdown/
    github repository: https://github.com/wkentaro/gdown
    '''

    url: str = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, outpath)



def set_main_logger(loggerName: str, lev: int, propagate: bool) -> None:
    """Set the logger for the main module"""
    global logger
    logger = logging.getLogger(loggerName)
    logger.setLevel(lev)
    logger.propagate = propagate
    # Create the handler and
    clsLogger: logging.StreamHandler = logging.StreamHandler(stream=sys.stdout)
    # This makes sure that the log file is created even if not in debug mode
    clsLogger.setLevel(logger.level)
    # Set the formatter
    if lev == logging.DEBUG:
        clsLogger.setFormatter(logging.Formatter("{levelname} :: {name} :: ln{lineno}:\n{message}", style="{"))
    else:
        clsLogger.setFormatter(logging.Formatter("{levelname}:\n{message}", style="{"))
    # Add llogger
    logger.addHandler(clsLogger)
    # write some log about it!
    logger.debug(f"General logger for {loggerName} loaded!")



########### MAIN ############
def main() -> None:

    #Get the parameters
    args = get_params()
    #start setting the needed variables
    sp2_install_dir: str = os.path.dirname(__file__)
    profile_db_dir: str = os.path.join(sp2_install_dir, "pfam_files/profile_db")
    outdir: str = ""
    if len(args.output_directory) > 0:
        outdir = os.path.realpath(args.output_directory)
    else:
        outdir = os.getcwd()

    # Initialize root Logger
    debug: bool = args.debug
    if debug:
        logging.basicConfig(format='{levelname} :: {name}:\n{message}', style="{", level=logging.DEBUG)
    else:
        # logging.basicConfig(level=logging.INFO)
        logging.basicConfig(format='{levelname}:\n{message}', style="{", level=logging.INFO)

    # set the url and file IDs
    # https://drive.google.com/file/d/1eV3t2FINOUPJI1132w3bmBrHnO3_bpfJ/view?usp=sharing
    # or
    # https://drive.google.com/file/d/1eV3t2FINOUPJI1132w3bmBrHnO3_bpfJ/view?usp=drive_link
    gdrive_file_id: str = "1eV3t2FINOUPJI1132w3bmBrHnO3_bpfJ"
    gdrive_url: str = f"https://drive.google.com/file/d/{gdrive_file_id}/view?usp=sharing"
    outname: str = "sonicparanoid2_pfam_mmseqs_profile_db.tar.gz"
    outpath: str = os.path.join(outdir, outname)

    print("\nsonicparanoid-get-profiles will be executed with the following parameters:")
    print(f"Output directory: {outdir}")
    print(f"Output path:\t{outpath}")
    print(f"SonicParanoid installation path: {sp2_install_dir}")
    print(f"PFamA DB files url: {gdrive_url}")
    print(f"Google Drive file ID:\t{gdrive_file_id}")

    # Start the download
    if os.path.isfile(outpath):
        logger.warning(f"The profile DB was previously downloaded in\n{outpath}\nand it will not be downloaded again.\n")
        logger.info(f"If you want to download the profile DB again please remove the\n{outpath}\n")
    else:
        download_pfam_profiles(file_id=gdrive_file_id, outpath=outpath)

    # Send a message in case the file cannot be downloaded
    if not os.path.isfile(outpath):
        logger.error("Something went wrong while downloading the PFamA profile DB files.")
        logger.info(f"Please download the file manually using your browser.\nFollowing is the download link from Google Drive:\n{gdrive_url}")
    else:
        print("To complete the installation of the PFamA profile DB.\n")
        print(f"Copy the content of the archive\n{outpath}")
        print(f"Inside the directory\n{profile_db_dir}\n")


if __name__ == "__main__":
    main()
