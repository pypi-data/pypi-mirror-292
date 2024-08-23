import argparse
import json

from base58 import b58encode as b58e
from base58 import b58decode as b58d
from solders.keypair import Keypair

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("f")
    args = ap.parse_args()

    try:
        # try to open as file
        with open(args.f, "r") as f:
            kp = json.load(f)
        print(b58e(bytes(kp)).decode('ascii'))
        print(Keypair(kp[:32]).pubkey())
    except:
        try: 
            # try to interpret as b58
            kp = [byte for byte in b58d(args.f)]
            print(kp)
            print(kp[32:])
            print(b58e(bytes(kp[32:])).decode('ascii'))
        except:
            # try to interpret as list of bytes
            kp = [int(byte) for byte in args.f[1:-1].split(',')]
            print(kp)
            print(kp[32:])
            print(b58e(bytes(kp[32:])).decode('ascii'))
            print(b58e(bytes(kp)).decode('ascii'))

if __name__ == '__main__':
    main()
