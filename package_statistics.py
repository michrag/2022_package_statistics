#!/usr/bin/env python3

import argparse
import pathlib
import sys
import shutil
import urllib.request as request
import gzip
from tqdm import tqdm
from collections import defaultdict


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def main():
    repository_base_url = "http://ftp.uk.debian.org/debian/dists/stable/main/"

    desired_architecture = parse_input_argument()

    dst_folder = create_destination_folder(desired_architecture)

    gz_file_path = download_contents_index_file(repository_base_url, desired_architecture, dst_folder)

    uncompressed_file_path = unzip_contents_index_file(gz_file_path)

    package_occurrences_dict = parse_contents_index_file(uncompressed_file_path)

    print_statistics(package_occurrences_dict)

    remove_destination_folder(dst_folder)


def parse_input_argument():
    parser = argparse.ArgumentParser("package_statistics")
    parser.add_argument("arch", help="architecture (amd64, arm64, mips, etc...)", type=str)
    args = parser.parse_args()

    print("arch = " + args.arch)

    return args.arch


def create_destination_folder(architecture):
    dst_path = "tmp/" + architecture + "/"

    try:
        pathlib.Path(dst_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        sys.exit(e)

    print("created destination folder = " + dst_path)

    return dst_path


def download_contents_index_file(repository_base_url, architecture, destination_folder):
    contents_index_filename = "Contents-" + architecture + ".gz"
    print("contents_index_filename = " + contents_index_filename)

    return download_from_ftp(repository_base_url, contents_index_filename, destination_folder)


def download_from_ftp(repository_base_url, contents_index_filename, destination_folder):
    download_url = repository_base_url + contents_index_filename

    print("downloading from URL = " + download_url)

    contents_index_file_path = destination_folder + contents_index_filename

    try:
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=download_url.split('/')[-1]) as t:
            request.urlretrieve(download_url, filename=contents_index_file_path, reporthook=t.update_to)
    except Exception as e:
        print(e)
        remove_destination_folder(destination_folder)
        sys.exit(e)

    print("downloaded file = " + contents_index_file_path)

    return contents_index_file_path


def unzip_contents_index_file(gz_file_path):
    print("decompressing file = " + gz_file_path)

    out_file_path = gz_file_path[:-3]  # discard ".gz"

    try:
        with gzip.open(gz_file_path, 'rb') as f_in:
            with open(out_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    except Exception as e:
        sys.exit(e)

    print("uncompressed file = " + out_file_path)

    return out_file_path


def parse_contents_index_file(contents_index_file):
    print("parsing file = " + contents_index_file)

    package_occurrences_dict = defaultdict(int)  # default value for each key will be 0

    with open(contents_index_file) as f:
        content = f.readlines()

    qualified_packages_names = []
    for line in content:
        # "package names cannot include white space characters" : the following split is safe
        tokenized_line = line.split()  # split line on whitespace characters
        if tokenized_line:  # if not empty
            second_column_entry = tokenized_line[-1]  # "A list of qualified package names, separated by comma"
            if ',' in second_column_entry:  # there is more than one qualified package name in this line
                for qualified_package_name in second_column_entry.split(','):  # split entry on commas
                    qualified_packages_names.append(qualified_package_name)
            else:  # exactly one qualified package name in this line
                qualified_packages_names.append(second_column_entry)

    for qualified_package_name in qualified_packages_names:
        if '/' in qualified_package_name:
            package_name = qualified_package_name.split('/')[-1]  # take substring after last '/'
        else:  # no "[[$AREA/]$SECTION/]" prefix
            package_name = qualified_package_name

        package_occurrences_dict[package_name] += 1

    return package_occurrences_dict


def get_top_10_packages(package_occurrences_dict):
    sorted_dict = sort_dictionary_by_value_in_descending_order(package_occurrences_dict)

    sorted_dict_items = list(sorted_dict.items())

    last_value = None
    if sorted_dict_items:  # if not empty
        last_value = sorted_dict_items[0][1]  # start with the first value

    position = 1
    index = 0
    top_10_packages = []

    # "fair" ranking: packages with an equal number of occurrences are given the same position,
    # and the ranking takes into account the first 10 positions, not the first 10 packages.

    while position < 11 and index < len(sorted_dict_items):
        current_key = sorted_dict_items[index][0]
        current_value = sorted_dict_items[index][1]

        if index > 0 and current_value != last_value:
            position += 1

        if position < 11:
            out_line = str(position) + ". " + current_key + " " + str(current_value)
            top_10_packages.append(out_line)

        last_value = current_value
        index += 1

    return top_10_packages


def sort_dictionary_by_value_in_descending_order(orig_dict):
    sorted_dict = {}

    for k, v in sorted(orig_dict.items(), key=lambda item: item[1], reverse=True):
        sorted_dict[k] = v

    return sorted_dict


def print_statistics(package_occurrences_dict):
    print("Here are the top 10 packages that have the most files associated with them:\n")

    for line in get_top_10_packages(package_occurrences_dict):
        print(line)

    print("\n")


def remove_destination_folder(destination_folder):
    print("removing destination folder = " + destination_folder)

    try:
        shutil.rmtree(destination_folder, ignore_errors=False)
    except Exception as e:
        sys.exit(e)

    print("removed destination folder = " + destination_folder)


if __name__ == "__main__":
    main()
