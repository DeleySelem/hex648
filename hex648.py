import argparse
import os
import ctypes
import subprocess

# Load the shared library
if os.name == 'nt':  # Windows
    hex64hash_lib = ctypes.CDLL('hex64hash.dll')
else:  # Linux/Mac
    hex64hash_lib = ctypes.CDLL('/usr/lib/hex64hash.so')  # Use the system-wide path

# Define the function signature for Hex64Hash
hex64hash_lib.Hex64Hash.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
hex64hash_lib.Hex64Hash.restype = None

def hex64hash(ctx):
    """Call the Hex64Hash assembly function."""
    ctx_array = (ctypes.c_uint32 * len(ctx))(*ctx)
    hex64hash_lib.Hex64Hash(ctx_array)
    return list(ctx_array)

trigram_symbols = {
    '000': '☰', '001': '☱', '010': '☲', '011': '☳',
    '100': '☵', '101': '☶', '110': '☴', '111': '☷',
}

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
    '110100': '䷴', '110101': '䷵', '110110': '䷶', '110111': '䷸',
    '111000': '䷹', '111001': '䷺', '111010': '䷻', '111011': '䷼',
    '111100': '䷽', '111101': '䷾', '111110': '䷿', '111111': '䷿',
}

def generate_seed_from_passphrase(passphrase, length):
    """Generates seed using hex64hash algorithm"""
    seed = []
    ctx = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
           0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    
    pass_bytes = passphrase.encode('utf-8')
    for i in range(0, len(pass_bytes), 4):
        chunk = pass_bytes[i:i+4].ljust(4, b'\0')
        ctx[i//4 % 8] ^= int.from_bytes(chunk, 'big')
    ctx = hex64hash(ctx)
    
    while len(seed) < length:
        bits = ''.join(f"{x:032b}" for x in ctx)
        seed.extend([int(bit) for bit in bits])
        ctx = hex64hash(ctx)
    return seed[:length]

def apply_seed_to_binary(binary, seed, reverse=False):
    binary_list = list(binary)
    binary_length = len(binary_list)
    
    for idx in range(len(seed)):
        if idx >= binary_length:
            break
        if reverse:
            original_idx = len(seed) - 1 - idx
            if original_idx >= binary_length:
                continue
            s = seed[original_idx]
            current_i = original_idx
        else:
            s = seed[idx]
            current_i = idx
        
        if s == 1:
            swap_index = (current_i + 1) % binary_length
            binary_list[current_i], binary_list[swap_index] = binary_list[swap_index], binary_list[current_i]
    
    return ''.join(binary_list)

def text_to_binary(text):
    utf_bytes = text.encode('utf-8')
    return ''.join(f"{byte:08b}" for byte in utf_bytes)

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
        if len(byte_bits) < 8:
            continue
        byte_array.append(int(byte_bits, 2))
    return byte_array.decode('utf-8', errors='ignore')

def run_in_memory(content, language):
    """Run the decoded content in memory."""
    if language == "bash":
        subprocess.run(content, shell=True, executable="/bin/bash")
    elif language == "python":
        exec(content, globals())

def main():
    parser = argparse.ArgumentParser(description='Multirole I Ching Hexagram Combat Encoder/Decoder')
    parser.add_argument('-f', '--file', type=str, help='File to encode')
    parser.add_argument('-d', '--decode', type=str, help='File to decode')
    parser.add_argument('-p', '--passphrase', type=str, help='Encryption passphrase')
    parser.add_argument('-x', '--iterations', type=int, default=1)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-rb', '--run-bash', action='store_true', help='Run decoded content as Bash')
    parser.add_argument('-rp', '--run-python', action='store_true', help='Run decoded content as Python')
    args = parser.parse_args()

    if args.decode:
        with open(args.decode, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        for _ in range(args.iterations):
            binary_str = ''.join(
                next((k for k, v in hexagram_symbols.items() if v == hs), '000000')
                for hs in content
            )
            
            if args.passphrase:
                seed = generate_seed_from_passphrase(args.passphrase, len(binary_str))
                binary_str = apply_seed_to_binary(binary_str, seed, reverse=True)

            trigrams = [binary_str[i:i+3] for i in range(0, len(binary_str), 3)]
            pad_pos = binary_str.rfind('1')
            if pad_pos != -1 and all(c == '0' for c in binary_str[pad_pos + 1:]):
                binary_str = binary_str[:pad_pos]
            content = decode_binary(binary_str)

        if args.run_bash or args.run_python:
            print("Executing decoded content...")
            if args.run_bash:
                run_in_memory(content, "bash")
            elif args.run_python:
                run_in_memory(content, "python")
        else:
            decoded_file = f'decoded_{os.path.basename(args.decode)}'
            with open(decoded_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Decoded file saved as {decoded_file}")

    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            original_content = f.read()

        content = original_content
        for _ in range(args.iterations):
            binary = text_to_binary(content)
            trigrams = binary_to_trigrams(binary)
            binary_padded = ''.join(trigrams)
            
            if args.passphrase:
                seed = generate_seed_from_passphrase(args.passphrase, len(binary_padded))
                binary_padded = apply_seed_to_binary(binary_padded, seed)
                trigrams = [binary_padded[i:i+3] for i in range(0, len(binary_padded), 3)]

            hexagrams = trigrams_to_hexagrams(trigrams)
            hex_symbols = [hexagram_symbols.get(h, '?') for h in hexagrams]
            content = ''.join(hex_symbols)

        output_file = f'hexed_{os.path.basename(args.file)}'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Encoded file saved as {output_file}")

if __name__ == "__main__":
    main()
