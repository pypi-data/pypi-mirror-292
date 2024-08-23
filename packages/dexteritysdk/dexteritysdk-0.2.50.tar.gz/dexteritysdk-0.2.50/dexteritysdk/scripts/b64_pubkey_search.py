import base58
import base64
import sys

# Function to search for bytes
def find_bytes(haystack, needle):
    return haystack.find(needle)

# Base58-decoded bytes
base58_encoded_str = sys.argv[2]
decoded_base58 = base58.b58decode(base58_encoded_str)

# Read and Base64-decode the file
with open(sys.argv[1], 'r') as file:
    base64_encoded_data = file.read()
    decoded_base64 = base64.b64decode(base64_encoded_data)

# Search for Base58-decoded bytes in Base64-decoded file
position = find_bytes(decoded_base64, decoded_base58)

print(position)
