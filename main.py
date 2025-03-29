import random
from typing import List
import collections
import re
import heapq

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def huffman_compress(text):
    freq_dict = collections.Counter(text)
    heap = [Node(char, freq) for char, freq in freq_dict.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    def build_codes(node, prefix='', code_dict=None):
        if code_dict is None:
            code_dict = {}
        if node is None:
            return code_dict
        if node.char is not None:
            code_dict[node.char] = prefix
        build_codes(node.left, prefix + '0', code_dict)
        build_codes(node.right, prefix + '1', code_dict)
        return code_dict

    huffman_codes = build_codes(heap[0])
    compressed = ''.join(huffman_codes[char] for char in text)
    return compressed, huffman_codes

def huffman_decompress(compressed_text, codes):
    reverse_codes = {code: char for char, code in codes.items()}
    decoded_text = ""
    temp_code = ""
    for bit in compressed_text:
        temp_code += bit
        if temp_code in reverse_codes:
            decoded_text += reverse_codes[temp_code]
            temp_code = ""
    return decoded_text

class HammingCoder:
    def __init__(self, parity_bits: int = 3):
        self.parity_bits = parity_bits

    def encode(self, data: List[int]):
        encoded_data = []
        for i in range(0, len(data), 4):
            block = data[i:i + 4]
            while len(block) < 4:
                block.append(0)

            b1 = block[0] ^ block[1] ^ block[3]
            b2 = block[0] ^ block[2] ^ block[3]
            b3 = block[1] ^ block[2] ^ block[3]

            encoded_block = [b1, b2, block[0], b3, block[1], block[2], block[3]]
            encoded_data.append(encoded_block)

        return encoded_data

    def add_noise(self, encoded_data, num_errors=10):
        corrupted_data = [block[:] for block in encoded_data]
        total_bits = len(encoded_data) * 7
        num_errors = min(num_errors, total_bits)

        error_positions = random.sample(range(total_bits), num_errors)

        for pos in error_positions:
            block_idx = pos // 7
            bit_idx = pos % 7
            corrupted_data[block_idx][bit_idx] ^= 1

        return corrupted_data

    def decode(self, corrupted_data):
        decoded_data = []
        error_count = 0
        error_counts_per_block = []

        for block in corrupted_data:
            s1 = block[0] ^ block[2] ^ block[4] ^ block[6]
            s2 = block[1] ^ block[2] ^ block[5] ^ block[6]
            s3 = block[3] ^ block[4] ^ block[5] ^ block[6]

            error_position = s1 * 1 + s2 * 2 + s3 * 4

            if error_position > 0:
                block[error_position - 1] ^= 1
                error_count += 1
                error_counts_per_block.append(1)
            else:
                error_counts_per_block.append(0)

            decoded_data.extend(block[2:3] + block[4:7])

        return decoded_data, error_count, error_counts_per_block

text = "Information technologies are rapidly developing, opening up new opportunities for process automation and business improvement."
clean_text = re.sub(r'[^a-zA-Z]', '', text.lower())

coder = HammingCoder()
compressed, huffman_codes = huffman_compress(clean_text)
encoded_bits = [int(bit) for bit in compressed]
encoded_data = coder.encode(encoded_bits)
corrupted_data = coder.add_noise(encoded_data, num_errors=10)

decoded_data, error_count, errors_per_block = coder.decode(corrupted_data)
print("== Error Detection and Correction ==")
print(f"Number of detected and corrected errors: {error_count}")
print(f"Number of errors occurred in each block: {errors_per_block}")
print("Decoded data after error correction:")
print(decoded_data)

print("\n" + "="*50)
print("== Original Message Text ==")
print(text)

print("\n" + "="*50)
print("== Compressed Text using Huffman Coding ==")
print(compressed)

print("\n" + "="*50)
print("== Encoded Data after Hamming Coding ==")
for block in encoded_data:
    print(block)

print("\n" + "="*50)
print("== Data with Random Errors ==")
for block in corrupted_data:
    print(block)
