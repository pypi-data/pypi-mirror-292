# CommonMark Website

This is a Python package that provides the command line utility `cmw`.

It stands for "CommonMark Website".

It converts `.md` CommonMark files into HTML then deploys to GitHub.

## Installation

    pip install cmw

## Usage

Place your `.md` CommonMark files into the `input` directory like this:

    input/index.md
    input/About.md
    input/Contact_Us.md

Then run:

    cmw git@github.com:your_username/example.org

Please note this will force-push and wipe the `example.org` repository history.

## Dependencies

- [mistletoe](https://github.com/miyuchina/mistletoe), one of the Python
  CommonMark implementations listed on the CommonMark spec
  [wiki](https://github.com/commonmark/commonmark-spec/wiki/List-of-CommonMark-Implementations)
