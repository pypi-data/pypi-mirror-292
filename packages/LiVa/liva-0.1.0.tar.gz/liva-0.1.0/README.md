# linkvalidator: URL-Check-Utility

A python based utility to search, validate, calculate stats and export URLs. 

## Info

You can use this package with github-actions to check if links on your hosted website or docs are outdated.

## Install

```bash
git clone https://github.com/protogia/linkvalidator.git
cd linkvalidator
poetry install
```

## Run

To parse all files in given directory recursively for URLs and print results:

```bash
poetry run linkvalidator -d <path> 
```

If you want to show only failures:

```bash
poetry run linkvalidator -d <path> --only-failures
```


