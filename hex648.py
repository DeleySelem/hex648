#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import ctypes
import ctypes.util

# Trigram symbols
trigram_symbols = {
    '000': '☰',  '001': '☱',  '010': '☲',  '011': '☳',
    '100': '☵',  '101': '☶',  '110': '☴',  '111': '☷'
}

# Hexagram symbols
hexagram_symbols = {
    '000000': '䷀', '000001': '䷁', '000010': '䷂', '000011': '䷃',
    '000100': '䷄', '000101': '䷅', '000110': '䷆', '000111': '䷇',
    '001000': '䷈', '001001': '䷉', '001010': '䷊', '001011': '䷋',
    '001100': '䷌', '001101': '䷍', '001110': '䷎', '001111': '䷏',
    '010000': '䷐', '010001': '䷑', '010010': '䷒', '010011': '䷓',
    '010100': '䷔', '010101': '䷕', '010110': '䷖', '010111': '䷗',
    '011000': '䷘', '011001': '䷙', '011010': '䷚', '011011': '䷛',
    '011100': '䷜', '011101': '䷝', '011110': '䷞', '011111': '䷟',
    '100000': '䷠', '100001': '䷡', '100010': '䷢', '100011': '䷣',
    '100100': '䷤', '100101': '䷥', '100110': '䷦', '100111': '䷧',
    '101000': '䷨', '101001': '䷩', '101010': '䷪', '101011': '䷫',
    '101100': '䷬', '101101': '䷭', '101110': '䷮', '101111': '䷯',
    '110000': '䷰', '110001': '䷱', '110010': '䷲', '110011': '䷳',
    '110100': '䷴', '110101': '䷵', '110110': '䷶', '110111': '䷷',
    '111000': '䷸', '111001': '䷹', '111010': '䷺', '111011': '䷻',
    '111100': '䷼', '111101': '䷽', '111110': '䷾', '111111': '䷿'
}

# Load hex64hash library
class HashContext(ctypes.Structure):
    _fields_ = [("ctx", ctypes.c_uint32 * 8)]

lib_path = ctypes.util.find_library('hex64hash')
if not lib_path:
    raise RuntimeError("hex64hash library not found. Run install.sh first.")
hex64hash = ctypes.CDLL(lib_path)
hex64hash.Hex64Hash.argtypes = [ctypes.POINTER(HashContext)]
hex64hash.Hex64Hash.restype = None

def text_to_binary(text):
    return ''.join(f"{byte:08b}" for byte in text.encode('utf-8'))

def binary_to_trigrams(binary):
    pad_len = (3 - (len(binary) % 3)) % 3
    if pad_len > 0:
        binary += '1' + '0' * (pad_len - 1)
    return [binary[i:i+3] for i in range(0, len(binary), 3)]

def trigrams_to_hexagrams(trigrams):
    if len(trigrams) % 2 != 0:
        trigrams.append('000')
    return [trigrams[i] + trigrams[i+1] for i in range(0, len(trigrams), 2)]

def decode_binary(binary_str):
    pad_pos = binary_str.rfind('1')
    if pad_pos != -1 and all(c == '0' for c in binary_str[pad_pos + 1:]):
        binary_str = binary_str[:pad_pos]
    byte_array = bytearray()
    for i in range(0, len(binary_str), 8):
        byte_bits = binary_str[i:i+8]
        if len(byte_bits) == 8:
            byte_array.append(int(byte_bits, 2))
    return byte_array.decode('utf-8', errors='ignore')

def generate_seed_from_passphrase(passphrase, length, iterations):
    ctx = HashContext()
    ctx.ctx = (ctypes.c_uint32 * 8)(
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    )
    pass_bytes = passphrase.encode('utf-8')
    for i in range(0, len(pass_bytes), 4):
        chunk = pass_bytes[i:i+4].ljust(4, b'\0')
        ctx.ctx[i // 4 % 8] ^= int.from_bytes(chunk, 'big')
    for _ in range(iterations):
        hex64hash.Hex64Hash(ctypes.byref(ctx))
    seed = []
    while len(seed) < length:
        for word in ctx.ctx:
            seed.extend(f"{word:032b}")
        hex64hash.Hex64Hash(ctypes.byref(ctx))
    return [int(bit) for bit in ''.join(seed)[:length]]

def apply_seed_to_binary(binary, seed, iterations=1, reverse=False):
    binary_list = list(binary)
    seed_len = len(seed)
    for _ in range(iterations):
        indices = reversed(range(len(binary_list))) if reverse else range(len(binary_list))
        for idx in indices:
            if seed[idx % seed_len]:
                swap_idx = (idx + 1) % len(binary_list)
                binary_list[idx], binary_list[swap_idx] = binary_list[swap_idx], binary_list[idx]
    return ''.join(binary_list)

def main():
    parser = argparse.ArgumentParser(description='Hex64 Encoder/Decoder', add_help=False)
    parser.add_argument('-f', '--file', help='File to encode')
    parser.add_argument('-d', '--decode', help='File to decode')
    parser.add_argument('-p', '--pass', dest='passphrase', help='Encryption passphrase')
    parser.add_argument('-x', '--iter', type=int, default=1, help='Seed iterations')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-rp', '--run-py', help='Run encoded Python script')
    parser.add_argument('-rb', '--run-sh', help='Run encoded Bash script')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')
    args = parser.parse_args()

    if args.help:
        print("""Hex64 - I Ching Encoder
Options:
  -f, --file FILE    Encode file
  -d, --decode FILE  Decode file
  -p, --pass PHRASE  Encryption passphrase
  -x, --iter NUM     Seed iterations (default: 1)
  -v, --verbose      Show detailed processing
  -rp, --run-py FILE Run Python script from memory
  -rb, --run-sh FILE Run Bash script from memory
  -h, --help         Show this help""")
        return

    try:
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()

            if args.verbose:
                print("\nOriginal Text:")
                print(content)

            binary = text_to_binary(content)
            
            if args.passphrase:
                seed = generate_seed_from_passphrase(args.passphrase, len(binary), args.iter)
                if args.verbose:
                    print("\nHash seed:")
                    print(f"<{len(seed)} bits>")
                binary = apply_seed_to_binary(binary, seed, args.iter)

            if args.verbose:
                print("\nBinary Representation:")
                print(binary)

            trigrams = binary_to_trigrams(binary)
            if args.verbose:
                print("\nTrigram Symbols:")
                print(''.join(trigram_symbols.get(t, '?') for t in trigrams))

            hexagrams = trigrams_to_hexagrams(trigrams)
            hex_symbols = ''.join(hexagram_symbols.get(h, '?') for h in hexagrams)
            if args.verbose:
                print("\nHexagram Symbols:")
                print(hex_symbols)

            output_file = f"hexed_{os.path.basename(args.file)}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(hex_symbols)
            print(f"\nEncoded file saved as {output_file}")

        elif args.decode:
            with open(args.decode, 'r', encoding='utf-8') as f:
                hex_content = f.read().strip()

            if args.verbose:
                print("\nHexagram Symbols:")
                print(hex_content)

            binary_str = ''.join(
                next((k for k, v in hexagram_symbols.items() if v == hs), '000000')
                for hs in hex_content
            )
            trigrams = [binary_str[i:i+3] for i in range(0, len(binary_str), 3)]
            if args.verbose:
                print("\nTrigram Symbols:")
                print(''.join(trigram_symbols.get(t, '?') for t in trigrams))
                print("\nBinary Representation:")
                print(binary_str)

            if args.passphrase:
                seed = generate_seed_from_passphrase(args.passphrase, len(binary_str), args.iter)
                binary_str = apply_seed_to_binary(binary_str, seed, args.iter, reverse=True)
                if args.verbose:
                    print("\nDecrypted Binary:")
                    print(binary_str)

            content = decode_binary(binary_str)
            if args.verbose:
                print("\nDecoded Text:")
                print(content)

            output_file = f"decoded_{os.path.basename(args.decode)}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\nDecoded file saved as {output_file}")

        elif args.run_py or args.run_sh:
            target = args.run_py or args.run_sh
            with open(target, 'r') as f:
                hex_content = f.read().strip()

            binary_str = ''.join(
                next((k for k, v in hexagram_symbols.items() if v == hs), '000000')
                for hs in hex_content
            )
            trigrams = [binary_str[i:i+3] for i in range(0, len(binary_str), 3)]
            binary = ''.join(trigrams)

            if args.passphrase:
                seed = generate_seed_from_passphrase(args.passphrase, len(binary), args.iter)
                binary = apply_seed_to_binary(binary, seed, args.iter, reverse=True)

            content = decode_binary(binary)
            if args.run_py:
                subprocess.run(['python3', '-c', content])
            else:
                subprocess.run(['bash', '-c', content])

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
