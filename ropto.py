# written by Jeemin Kim
# Jan 16, 2022
# github.com/mrharrykim

from logging import error
from os import system
from lib.utils import RoptoError, Time, get_equivalences, remove_duplicates, get_coordinate, get_duration
from argparse import ArgumentParser
from getpass import getpass
from lib.security import decrypt, encrypt
from lib.naverAPI import NaverOpenAPI
from lib.solveTSP import TSPSolver
from config import API_ID, DEFAULT_START_ADDRESS

def get_namespace(args: list[str] =None):
    parser = ArgumentParser(description="ROPTO: Route optimizer", add_help=False)
    group1 = parser.add_argument_group("control options")
    group1.add_argument("-f", "--file", default="addr.txt", help="use addresses from this file (default: addr.txt)")
    group1.add_argument("-n", "--no-return", action="store_true", help="don't consider trip from the last point to the initial point")
    group1.add_argument("-s", "--set-start", action="store_true", help="start from the first address in the file")
    group2 = parser.add_argument_group("information options")
    group2.add_argument("-h", "--help", action="help", help="show this help message and exit")
    group2.add_argument("-v", "--verbose", metavar="N", choices=range(1, 4), type=int, default=1, help="set how much output is produced (least: 1 - most: 3, default: 1)")
    group3 = parser.add_argument_group("account options")
    group3.add_argument("-c", "--chpasswd", action="store_true", help="prompt for new password")
    group3.add_argument("-r", "--reset", action="store_true", help="reset api key (retoration purpose only)")
    return parser.parse_args(args)

def main(namespace, secret):

    api = NaverOpenAPI(API_ID, secret, verbose=namespace.verbose)

    start_address = DEFAULT_START_ADDRESS

    with open(namespace.file, "r", encoding="UTF-8") as file:
        if namespace.set_start:
            start_address = file.readline()
        addresses = [start_address]
        addresses_dump = file.read()
        addresses = addresses + addresses_dump.split("\n")

    geocodes = api.get_geocodes(*addresses)
    coordinates = [get_coordinate(geocode) for geocode in geocodes]

    equivalences = get_equivalences(coordinates)
    unique_geocodes = remove_duplicates(geocodes, equivalences)
    unique_coordinates = remove_duplicates(coordinates, equivalences) 

    direction_matrix = api.get_directions(*unique_coordinates)
    duration_matrix = [[get_duration(direction) for direction in directions] for directions in direction_matrix]
    solver = TSPSolver(verbose=namespace.verbose)
    solution = solver.solve(duration_matrix, namespace.no_return)
    
    if namespace.verbose == 1 or namespace.verbose == 2 or namespace.verbose == 3:
        output = "계산결과\n\n"
        output += unique_geocodes[0]["roadAddress"] + "\n"
        previous_point = 0
        for point in solution.points[1:]:
            duration = duration_matrix[previous_point][point]
            direction_time = Time(duration)
            output += "v\t" + format(direction_time, "%h[ 시간 ]%m[ 분]") + "\n"
            output += unique_geocodes[point]["roadAddress"] + "\n"
            previous_point = point
        total_time = Time(solution.duration)
        output +="\n총 이동 시간:\t" + format(total_time, "%h[ 시간 ]%m[ 분]") + "\n"
    
    return output
        
if __name__ == "__main__":
    namespace = get_namespace()
    if namespace.chpasswd:
        passwd = getpass("비밀번호: ")
        secret = decrypt(passwd)
        if not secret:
            exit()
        new_passwd = getpass("새 비밀번호: ")
        new_passwd_copy = getpass("새 비밀번호 (다시 한 번 입력해 주세요.): ")
        if new_passwd != new_passwd_copy:
            print("새 비밀번호가 일치하지 않습니다.")
            exit()
        encrypt(secret, new_passwd)
        print("비밀번호 변경에 성공하였습니다.")
        exit()

    if namespace.reset:
        system("cls")
        key = input("API_KEY: ")
        system("cls")
        new_passwd = getpass("\r새 비밀번호: ")
        new_passwd_copy = getpass("새 비밀번호 (다시 한 번 입력해 주세요.): ")
        if new_passwd != new_passwd_copy:
            print("새 비밀번호가 일치하지 않습니다.")
            exit()
        encrypt(key, new_passwd)
        print("초기화에 성공하였습니다.")
        exit()

    for i in range(3):
        passwd = getpass("비밀번호: ")
        secret = decrypt(passwd)
        if secret:
            break
    else:
        exit()
    
    try:
        print("\n" + main(namespace, secret))
    except RoptoError as err:
        # print(error.__class__.__name__ + ":", *error.args)
        print("\n")
        error("\t"+ err.__class__.__name__ + ":\t" + err.args[0])
        exit()



