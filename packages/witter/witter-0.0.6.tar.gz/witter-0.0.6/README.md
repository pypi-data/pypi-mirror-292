# Witter

## What's Witter?

Witter accepts text input, splits it into sections, or "chains", and then works out which character is most likely to follow that "chain" whenever it appears in the source text.

Once it has analyzed the source text, it generates a number of random sample pieces of text based on it.

Because of the way it uses the source text, the text that it produces will be "in the style" of the original text. It may, or may not, make sense.

It's worth noting that this isn't Machine Learning (ML), or any kind of Artificial Intelligence (AI). It's statistics, with some Monte Carlo methods thrown in.

## How Do I Use Witter?

Run `witter` from within a virtual environment using the syntax:

```python
witter --help
```

or from the command line using:

```python
python -m witter --help
```

Both of these examples will display the command line options.

A simple example to get you started is:

* download a large text file - perhaps [The Complete Works of Shakespeare from Project Gutenberg](https://www.gutenberg.org/ebooks/100)
* pass the contents of the file to `witter`

In Windows or Linux, in a Python virtual environment, the following command will produce samples:

```bash
witter filepath.txt
```

or, if you want to use piping in Linux:

```bash
cat filepath.txt | witter
```

So, if you want to generate text from The Complete Works of William Shakespeare, and why wouldn't you?

```bash
wget https://www.gutenberg.org/cache/epub/100/pg100.txt
cat pg100.txt | witter
```

or if A Christmas Carol by Charles Dickens is more your thing:

```bash
wget https://www.gutenberg.org/ebooks/24022.txt.utf-8
cat 24022.txt.utf-8 | witter
```

You've probably noticed the `utf-8` extension on one of the text files. This is a way that Project Gutenberg uses to denote UTF-8-encoded text files. `witter` can handle UTF-8 with no problems.

If you'd like a list of the available options, you can type:

```bash
witter --help
```

from within your virtual environment. The output will be something like:

```bash
usage: witter [-h] [-c CHAIN_LENGTH] [-t TEXT_LENGTH] [-s SAMPLE_COUNT] [-e {ascii,utf-8}] [-f {text,json}] [-v] [FILE]

Generate texts based on an input text.

positional arguments:
  FILE                  The file to use as a source of text for for witter, or - for stdin. (default: -)

options:
  -h, --help            show this help message and exit
  -c CHAIN_LENGTH, --chain-length CHAIN_LENGTH
                        The number of characters used to chain together and forecast the next character. (default: 10)
  -t TEXT_LENGTH, --text-length TEXT_LENGTH
                        The length of text sample to generate, in characters. Note: may be approximate. (default: 200)
  -s SAMPLE_COUNT, --sample-count SAMPLE_COUNT
                        The number of samples to generate (default: 1)
  -e {ascii,utf-8}, --encoding {ascii,utf-8}
                        The text encoding to use when reading the input. (default: utf-8)
  -f {text,json}, --format {text,json}
                        The format for the output. (default: text)
  -v, --verbosity       Increase the verbosity of the output (default: 0)

For more details, refer to https://www.softwarepragmatism.com/
```

## Download Statistics
[![Downloads](https://static.pepy.tech/badge/witter)](https://pepy.tech/project/randalyze)
[![Downloads](https://static.pepy.tech/badge/witter/month)](https://pepy.tech/project/randalyze)
[![Downloads](https://static.pepy.tech/badge/witter/week)](https://pepy.tech/project/randalyze)
