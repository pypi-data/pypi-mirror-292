# crack-pdf

crack-pdf is a command-line tool for attempting to decrypt password-protected PDF files using a brute-force approach.

## Features

- Attempts to crack PDF passwords using digit combinations
- Configurable password length
- Command-line interface for easy use

## Installation

To install crack-pdf, follow these steps:

1. Clone the repository:

```sh
git clone <https://github.com/szpatrichard/crack-pdf.git>
cd crack-pdf
```

2. Install the package:

```sh
pip install -e .
```

## Usage

After installation, you can use the `crack-pdf` command from anywhere in your terminal:

```sh
crack-pdf /path/to/your/pdf -l <password_length>
```

Where:

- `/path/to/your/pdf` is the path to the PDF file you want to decrypt
- `<password_length>` is the length of the password to try (e.g., 4 for a 4-digit password)

Example:

```sh
crack-pdf ~/user/documents/locked.pdf -l 4
```

This command will attempt to crack a PDF password using all 4-digit combinations.

## Limitations

- This tool only attempts numeric passwords.
- It uses a brute-force approach, which can be time-consuming for longer passwords.
- It's intended for educational purposes and should not be used for illegal activities.

## Contributing

Contributions to crack-pdf are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENCE](LICENCE) file for details.

## Disclaimer

This tool is for educational purposes only. Only use it on PDF files that you own or have explicit permission to access. The authors are not responsible for any misuse or damage caused by this program.
