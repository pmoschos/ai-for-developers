# Athens University of Business and Economics
# AI for Developers
# Code Generator Lab

This sub-project contains a Python code generator built for Lab 1 of the course. It turns natural-language descriptions into Python code with OpenAI-compatible models, can optionally generate tests, and includes both a basic CLI and a richer CLI with setup, styled output, and export options.

## Current State

The project currently includes:

- a basic generation script in `code_gen.py`
- a standard CLI in `code_generator.py`
- a Rich-based CLI in `code_generator_rich.py`
- prompt templates in `prompts.py`
- lab instructions in `lab_01_instructions.md`
- a scratch notebook in `scratch.ipynb`
- pytest coverage for the Rich CLI in `tests/test_code_generator_rich.py`

## Main Features

- generate Python code from a text description
- optionally generate tests in a second prompt call
- clean markdown code fences from model output
- save generated code and tests to files
- run in interactive mode
- choose between `openai` and `ollama` in the Rich CLI
- persist default client and model settings in `.code_generator_rich_config.json`
- export generation results as JSON in the Rich CLI

## Requirements

- Python 3.10+
- packages from `../requirements.txt`
- a `.env` file in the parent lab directory if you want to use OpenAI:

```env
OPENAI_API_KEY=your_api_key_here
```

If `OPENAI_API_KEY` is not available, the Rich CLI can still work with a local Ollama server when Ollama is installed and running.

## Install

```bash
pip install -r ../requirements.txt
```

## Usage

### Basic script

```bash
python code_gen.py
```

Runs the predefined examples from the lab.

### Standard CLI

```bash
python code_generator.py "a function that reverses a string"
python code_generator.py --description "binary search" --with-tests
python code_generator.py -i
```

### Rich CLI

```bash
python code_generator_rich.py setup --show
python code_generator_rich.py setup --client ollama --model llama3.2
python code_generator_rich.py "binary search" --client openai --model gpt-4o-mini --display
python code_generator_rich.py "fibonacci" --with-tests --save_all fibonacci.py
python code_generator_rich.py "prime checker" --json_output result.json
python code_generator_rich.py -i
```

## Testing

Run the current automated tests with:

```bash
pytest yes_lab1_HatzitheodorouIason/tests/test_code_generator_rich.py
```

The existing test file focuses on the Rich CLI helpers, configuration flow, filename validation, JSON output validation, and argument parsing.

## Notes

The standard CLI and the Rich CLI both accept the description as positional text, and the standard CLI also supports `--description`. The Rich CLI stores default client and model values in `.code_generator_rich_config.json`, but `--client` and `--model` can still override them per run. Generated code is cleaned before display or saving to remove markdown fences such as ` ```python ` and ` ``` `.

## TODOs

- Add tests for `code_generator.py` and `code_gen.py`.
- Restructure code so that core CLI functionality is shared between the simple
client and the rich client.