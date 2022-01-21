# written by Jeemin Kim
# Jan 15, 2022
# github.com/mrharrykim

from hashlib import sha256
from json import dump, load

def cipher(crypt: str, passwd: str) -> str:
    padded_passwd = passwd*(len(crypt)//len(passwd))+"0"*(len(crypt)%len(passwd))
    return "".join([chr(ord(s)^ord(p)) for s, p in zip(crypt, padded_passwd)])

def encrypt(secret: str, passwd: str) -> str:
    with open(r"lib\shadow.json", "w") as file:
        crypt = cipher(secret, passwd)
        hash = sha256(secret.encode()).hexdigest()
        dump({"crypt": crypt, "hash": hash}, file)

def decrypt(passwd: str) -> str:
    with open(r"lib\shadow.json", "r") as file:
        pair = load(file)
    secret = cipher(pair["crypt"], passwd)
    if sha256(secret.encode()).hexdigest() != pair["hash"]:
        print("비밀번호가 잘못되었습니다. 다시 시도해 주세요")
        return None
    print("인증에 성공하였습니다.")
    return secret

if __name__ == "__main__":
    pass
