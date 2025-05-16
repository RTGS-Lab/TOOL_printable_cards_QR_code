#!/usr/bin/env python3

import qrcode
import argparse
from pathlib import Path

def generate_qr_code(data: str, output_path: str, size: int = 10):
    """
    Generate a QR code from a string and save it as an image.

    Args:
        data (str): The data to encode in the QR code.
        output_path (str): File path to save the QR code image (e.g., 'output.png').
        size (int): Controls the size of the QR code (default 10).
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"✅ QR code saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a QR code from a string.")
    parser.add_argument("data", help="The string to encode into the QR code.")
    parser.add_argument("output", type=Path, help="Output image file (e.g., qr.png)")
    parser.add_argument("--size", type=int, default=10, help="Box size for the QR code")

    args = parser.parse_args()
    generate_qr_code(args.data, args.output, args.size)

if __name__ == "__main__":
    main()

