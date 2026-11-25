# AI Usage Disclosure
## Tools used

- Google Gemini - Neon

## Conversation links

- Link 1:

## What I used them for

- Creating a step-by-step guideline for the labwork, creating drafts and asking questions related to the labwork

## Which parts of the code were AI-generated or substantially AI-assisted

- `flight_parser.py`: `argparse` setup, CLI argument handling, and `logging` handler cleanup in `main()`.
- `validator.py`: strict `YYYY-MM-DD HH:MM` datetime parsing, ASCII regex checks, and `nan`/`inf` price validation.
- `csv_loader.py`: CSV line parsing and duplicate flight tracking in `parse_files()`.
- `query.py`: query validation (including excluding booleans from numeric checks) and filtering/sorting logic.

## Key prompts

1. What is the cleanest way in Python to enforce a YYYY-MM-DD HH:MM date format, ensuring that single-digit days or hours are not accepted, while also validating that the string contains only ASCII characters? And how can I detect cases like float('nan')?

2. When writing logs to a file using logging module without basicConfig, how can I prevent duplicate lines which occurs when the function is called repeatedly within the same process by using try/finally?

3. How can I define mutually exclusive arguments like -i, -d, and -j using argparse, and how can I return an exit code from main(argv) without calling sys.exit?

4. How can I exclude true false values ​​when checking if the price or limit fields in a JSON query are numbers/integers?

## What I changed or verified myself
I adapted the code to match the required module structure and student constants, simplified the implementation, and verified all modules locally
