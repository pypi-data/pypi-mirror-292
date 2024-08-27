import PyPDF2
import argparse
import itertools
import string


def try_decrypt_pdf(pdf_reader: PyPDF2.PdfReader, password: str) -> bool:
    if not pdf_reader.is_encrypted:
        print("The PDF is not encrypted.")
        return True

    if pdf_reader.decrypt(password):
        print(f"Successfully decrypted the PDF with password: {password}")
        return True

    return False


def generate_passwords(length: int = 4) -> itertools.product:
    chars = string.digits  # Use only digits
    for password in itertools.product(chars, repeat=length):
        yield "".join(password)


def main():
    parser = argparse.ArgumentParser(
        description="Crack PDF password using brute force."
    )
    parser.add_argument("file", help="Path to the PDF file")
    parser.add_argument(
        "-l", "--length", type=int, required=True, help="Length of the password to try"
    )
    args = parser.parse_args()

    with open(args.file, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        for password in generate_passwords(args.length):
            if try_decrypt_pdf(pdf_reader, password):
                print(f"The PDF has {len(pdf_reader.pages)} pages.")
                print("First few characters of the first page:")
                print(pdf_reader.pages[0].extract_text()[:100])
                break
        else:
            print("Failed to decrypt the PDF. No matching password found.")


if __name__ == "__main__":
    main()
