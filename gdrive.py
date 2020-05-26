#! /Users/gml/Library/Caches/pypoetry/virtualenvs/mypydrive-NpopQ0MI-py3.7/bin/python
"""
    Hell yeah !
"""

import os
import sys
import argparse
import toml

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from typing import List,Dict,NoReturn,Any,Callable,Optional,Union

from Drive import Drive
from customobjs import objdict

DEFAULT_CONFIG_FILE = ".gdrive.toml"

def parse_congfig(config_file: Optional[str] = None) -> objdict:
    """
        Parse configuration from a TOML file,
        config_file parameter defaults to global DEFAULT_CONFIG_FILE
    """
    global DEFAULT_CONFIG_FILE
    config_file = config_file or DEFAULT_CONFIG_FILE
    with open(config_file, "r") as f:
        _conf = toml.load(f, _dict=objdict)
    return _conf
##

def pull(d: Drive, config: objdict, verbose: bool = True) -> NoReturn:
    """
    """
    gfiles = d.ez_query(directory=config.info.id)
    remote_filenames = set([
        f['title'] for f in gfiles if not 'vnd' in f['mimeType']
    ])
    local_filenames = set([
        f for f in os.listdir('.') if os.path.isfile(f)
    ])
    names_to_pull = remote_filenames - local_filenames
    files_to_pull = [
        f for f in gfiles if f['title'] in names_to_pull
    ]
    for file in files_to_pull:
        try:
            if verbose: print(f"Downloading `{file['title']}` ...", end="\t")
            file.GetContentFile(file['title'])
            if verbose: print("Done")
        except Exception as e:
            print(f"\n\n ERROR: File `{file['title']}` could not be downloaded.")
            print(f"Error details : {e}\n")
##

def push(d: Drive, config: objdict, verbose: bool = True) -> NoReturn:
    """
    """
    gfiles = d.ez_query(directory=config.info.id)
    remote_filenames = set([
        f['title'] for f in gfiles if not 'vnd' in f['mimeType']
    ])
    local_filenames = set([
        f for f in os.listdir('.') if os.path.isfile(f)
    ])
    names_to_push = local_filenames - remote_filenames
    names_to_push -= set(config.ignore.file_list)
    for name in names_to_push:
        d.upload_simple(
            source=name,
            title=name,
            parent_id=config.info.id,
            verbose=verbose
        )
##

def generate_config_interactive() -> objdict:
    """
        Returns:
            True  : Upon successful config generation.
            False : Upon failure.
    """
    global DEFAULT_CONFIG_FILE

    print("\n\nWelcome to the simplest and most stupid way to interact with Google Drive!")
    print("This function will help you set the configuration interactively!")
    print("\n1. Input the folder/directory's name (so that you know its remote name)")
    name = input("\tname : ")
    print("\n2. Input the folder/directory id (MANDATORY) ")
    print("https://drive.google.com/drive/u/0/folders/{THIS IS THE ID} ")
    id = input("\tid : ")
    print("\n3. Input a description (optional) ")
    description = input("\tdescription : ")
    print("\n4. Input the the parent's id (if any)")
    print("This can be an id as in step 2, or 'root', or it can be left blank")
    parent_id = input("\tparent_id : ")

    _config = {
        "name": name,
        "id": id,
        "description": description,
        "parent_id": parent_id
    }

    print(f"\n{_config}\n")
    _is_correct = input("Is this configuration correct? [y/n] : ")
    if _is_correct:
        _config = objdict({
            "info": _config,
            "ignore": {
                "file_list": [".gdrive.toml"],
                "glob": []
            }
        })
        try:
            print(f"\nWriting configuration to {DEFAULT_CONFIG_FILE} ...", end="\t")
            with open(DEFAULT_CONFIG_FILE, "w") as f:
                toml.dump(_config, f)
            print("DONE")
        except:
            print(f"Could not write configuration to {DEFAULT_CONFIG_FILE}")
            exit()

##

if __name__ == "__main__":
    if ".gdrive.toml" not in os.listdir('.'):
        print(f"\n\nNo {DEFAULT_CONFIG_FILE} file was found on this directory.")
        gen_conf = input("Interactively generate config? [y/n] : ")
        if gen_conf == 'y':
            generate_config_interactive()
        else:
            print("Bye!")
            exit()
    else:
        config = parse_congfig()
        d = Drive()

    if len(sys.argv) == 2:
        if sys.argv[1] == "pull":
            pull(d, config)
        elif sys.argv[1] == "push":
            push(d, config)
        else:
            print(f"Unkown option {sys.argv[1]}")
    else:
        print("gdrive action")
        print("action can be pull or push")

    """
    parser = argparse.ArgumentParser(
        description='Basic git-like Google Drive management',
        epilog=""
    )
    """
