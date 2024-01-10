from qreader import QReader
from textwrap import wrap
import cv2
import qrcode
import base64
import sys

arguments = sys.argv

def create_qr(data, filename):
    qr_code = qrcode.make(data)
    qr_code.save(filename)

def read_qr(filename):
    qreader = QReader()
    qr_code = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)
    return qreader.detect_and_decode(image=qr_code)[0]

def splice_string(string, amount):
    return wrap(string, amount)

def file_to_base64(filename):
    with open(filename, 'rb') as file:
        return base64.b64encode(file.read()).decode("utf-8")

def file_to_qr(filename):
    print("[#] Starting file-to-qr conversion")
    print("[#] Converting file to base64")
    file = file_to_base64(filename)
    print("[#] Wrapping file in 2300 char chunks")
    contents = wrap(file, 2300)
    print("[#] Adding read info to base64")
    contents[0] = "START" + contents[0]
    contents[len(contents) - 1] = contents[len(contents) - 1] + "END"
    counter = 1
    print(f"[#] Creating QR {len(contents)} codes")
    for i in contents:
        create_qr(i, f'qr-{counter}.png')
        print(f"[#] Created QR {counter}")
        counter += 1
    print("[#] Done converting file-to-qr!")

def qr_to_file(filename):
    print("[#] Starting qr-to-file conversion")
    counter = 1
    contents = []
    file_base64 = ""
    while True:
        print(f"[#] Reading QR {counter}")
        content = read_qr(f'qr-{counter}.png')
        if content is None:
            print(f"[#] Failed to recognize QR {counter}. Retrying...")
            content = read_qr(f'qr-{counter}.png')
            if content is None:
                print(f"[#] Failed to recognize QR {counter}. Retrying...")
                content = read_qr(f'qr-{counter}.png')
                if content is None:
                    print(f"[#] Failed to recognize QR {counter}")
                    return

        if content.startswith("START"):
            content = content[5:]
        if content.endswith("END"):
            content = content[:-3]
            contents.append(content)
            break
        contents.append(content)
        counter += 1

    print("[#] Composing file")
    for i in contents:
        file_base64 = file_base64 + i

    print("[#] Converting file to bytes")
    file_base64 = bytes(file_base64, 'utf-8')

    print(f"[#] Saving file to {filename}")
    with open(filename, "wb") as f:
        f.write(base64.decodebytes(file_base64))
    
    print("[#] Done converting qr-to-file!")

if len(arguments) > 1:
    if arguments[1] == "convert":
        file_to_qr(arguments[2])
    elif arguments[1] == "revert":
        qr_to_file(arguments[2])
    else:
        print("Invalid argument.")
        print("Use 'python3 qr-files convert' to convert a file to qr codes")
        print("Use 'python3 qr-files revert' to convert qr codes to a file")
else:
    print("Invalid argument.")
    print("Use 'python3 qr-files convert' to convert a file to qr codes")
    print("Use 'python3 qr-files revert' to convert qr codes to a file")