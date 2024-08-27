import argparse
import io
import os
import re
import sys
from pprint import pformat
from typing import TextIO

from witter.chain_generator import ChainGenerator


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="witter",
        description="Generate texts based on an input text.",
        epilog="For more details, refer to https://www.softwarepragmatism.com/",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--chain-length",
        type=int,
        default=10,
        help="The number of characters used to chain together and forecast the next character.",
    )

    parser.add_argument(
        "-t",
        "--text-length",
        type=int,
        default=200,
        help="The length of text sample to generate, in characters. Note: may be approximate.",
    )

    parser.add_argument(
        "-s",
        "--sample-count",
        type=int,
        default=1,
        help="The number of samples to generate",
    )

    parser.add_argument(
        "-e",
        "--encoding",
        choices=["ascii", "utf-8"],
        default="utf-8",
        help="The text encoding to use when reading the input.",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="The format for the output.",
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="Increase the verbosity of the output",
    )

    parser.add_argument(
        "input_file",
        metavar="FILE",
        nargs="?",
        default="-",
        help="The file to use as a source of text for for witter, or - for stdin.",
    )

    return parser.parse_args()


def read_source(input_stream: TextIO) -> str:
    """
    Read the text from the source stream, and drop any unwanted characters
    and substrings.

    :param input_stream:
    :return:
    """

    source = input_stream.read()
    # Remove Unicode zero-width spaces
    # source = re.sub(r"\u200b", "", source, re.MULTILINE)
    # Convert Unicode apostrophes to ASCII
    source = re.sub(r"\u2019", "'", source, re.MULTILINE)
    # Remove Unicode non-breaking spaces
    source = re.sub(r"\ufeff", " ", source, re.MULTILINE)

    # Remove any Project Gutenberg header and footer
    start_match = re.search(
        r"^[\n.]+\*+\s+START\s+OF\s+THE\s+PROJECT\s+GUTENBERG\s+EBOOK\s+.*\*+.*\n\s*",
        source,
        re.MULTILINE,
    )
    if start_match:
        source = source[start_match.end() :]

        # Only search for the footer if there was a header
        end_match = re.search(
            r"\*\*\*\sEND\sOF\sTHE\sPROJECT\sGUTENBERG\sEBOOK\s.*$",
            source,
            re.MULTILINE,
        )

        if end_match:
            source = source[: end_match.start()]

    # Replace the characters we don't want with spaces -
    # Non-characters, digits & spaces, stage directions
    pattern = re.compile(r"[^\w\s,\.\'_\?;:]+|[0-9\s\n\r]+|\[_\w+\.?_?\]?|\[?_?\w+\.?_\]")
    source = pattern.sub(" ", source)

    # Remove duplicate whitespace characters
    source = re.sub(r"\s{2,}", " ", source)

    return source


def main():
    arguments = parse_arguments()

    if not arguments.input_file or arguments.input_file == "-":
        source = read_source(
            io.TextIOWrapper(sys.stdin.buffer, encoding=arguments.encoding)
        )
    else:
        absolute_path = os.path.abspath(arguments.input_file)

        if not os.path.isfile(absolute_path):
            print(f"Not a file: {absolute_path}")
            sys.exit(1)

        with open(
            arguments.input_file, mode="r+", encoding=arguments.encoding
        ) as source:
            source = read_source(source)

    output_limit = arguments.text_length
    chain_length = arguments.chain_length
    sample_count = arguments.sample_count

    generator = ChainGenerator(source)

    results = [
        generator.generate_chain(chain_length, output_limit)
        for _ in range(0, sample_count)
    ]

    if arguments.format.casefold() == "text".casefold():
        if arguments.verbosity > 0:
            print(
                "Chains: {} created from {} characters.".format(
                    generator.chain_count, generator.character_count
                )
            )

            print(f"Chain Length: {chain_length}")
            print("")
        for attempt in results:
            print(f"{attempt}")
            print("")
    elif arguments.format.casefold() == "json".casefold():
        print(f"{pformat(results)}")


if __name__ == "__main__":
    main()
