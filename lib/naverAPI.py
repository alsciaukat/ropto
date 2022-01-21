# written by Jeemin Kim
# Jan 14, 2022
# github.com/mrharrykim

from http.client import HTTPSConnection
from urllib.parse import quote
from json import loads
from config import TOTAL_OUTPUT_LENGTH_VERBOSE_2, OUTPUT_COMPLETE_INDICATOR
from lib.utils import RoptoError

class InvalidAddressError(RoptoError):
    pass

class RequestFailedError(RoptoError):
    pass

class NaverOpenAPI:
    """
    Context manager for Naver API connection.

    Please Refer to https://api.ncloud-docs.com/docs/en/home
    for more information about Naver Open API.
    """
    def __init__(self, id: str, key: str, verbose: int =1):
        self.id = id
        self.key = key
        self.verbose = verbose
    def __enter__(self) -> HTTPSConnection:
        self.conn = HTTPSConnection("naveropenapi.apigw.ntruss.com")
        return self.conn
    def __exit__(self, type, value, traceback) -> None:
        self.conn.close()

    def get_keypair(self):
        return {"X-NCP-APIGW-API-KEY-ID": self.id, "X-NCP-APIGW-API-KEY": self.key}
    
    def get_geocodes(self, *addresses: str, coordinate_only=False):
        """
        Get detailed information about given addresses
        
        It takes human readable addresses and gives full addresses
        and coordinates in longitude & latitude.
        """
        geocoded_addresses: list[dict] = []
        output_prefix = "Requesting geocodes using Naver API"
        
        # create context with https connection which is 'api'
        with self as conn:
            for address in addresses:
                encoded_address = quote(address)
                conn.request("GET", f"/map-geocode/v2/geocode?query={encoded_address}", headers=self.get_keypair())
                geocoding_response = conn.getresponse()
                geocoding_json = geocoding_response.read()
                geocoding_body = loads(geocoding_json)
                
                if geocoding_response.status != 200:
                    raise RequestFailedError(f"{geocoding_response.status}, {geocoding_body}\n지민이에게 도움 요청!")
                if geocoding_body["meta"]["totalCount"] == 0:
                    raise InvalidAddressError(f"주어진 주소를 찾을 수 없습니다. 주어진 주소: '{address}'. 다른 방식으로 입력해 주세요. 예) 원주시 지니기길 11-20")
                if geocoding_body["meta"]["totalCount"] > 1:
                    raise InvalidAddressError(f"주어진 주소가 유일한 주소가 아닙니다. 주어진 주소: '{address}'. 더 상세한 주소로 변경해야 될 수 있습니다. 예) 원주시 지니기길 11-20")
                if coordinate_only:
                    geocoded_addresses.append(geocoding_body["addresses"][0]["x"] + "," + geocoding_body["addresses"][0]["y"])
                else:
                    geocoded_addresses.append(geocoding_body["addresses"][0])
                
                if self.verbose == 2:
                    output_progress = f"{len(geocoded_addresses)}/{len(addresses)}"
                    print(output_prefix + "."*(TOTAL_OUTPUT_LENGTH_VERBOSE_2 - len(output_prefix) - len(output_progress)) + output_progress, end="\r")
        if self.verbose == 2:
            print(output_prefix + "."*(TOTAL_OUTPUT_LENGTH_VERBOSE_2 - len(output_prefix) - len(OUTPUT_COMPLETE_INDICATOR)) + OUTPUT_COMPLETE_INDICATOR)
        return geocoded_addresses
    def get_directions(self, *coordinates: str, duration_only=False):
        """
        Get overall directions from each coordinates to other coordinates.

        coordinate is of a form "<longitude>,<latitude>".
        It returns matrix of route between each of coordinates
        except the diagonal ones which is None.
        """
        direction_matrix = []
        # to prevent lists that have the same memory address
        for i in range(len(coordinates)):
            direction_matrix.append([None]*len(coordinates))

        output_prefix = "Requesting directions using Naver API"

        with self as conn:
            for i, start in enumerate(coordinates):
                for j, goal in enumerate(coordinates):
                    if start == goal:
                        continue
                    conn.request("GET", f"/map-direction/v1/driving?start={start}&goal={goal}", headers=self.get_keypair())
                    direction_response = conn.getresponse()
                    direction_json = direction_response.read()
                    direction_body = loads(direction_json)
                    if direction_response.status != 200:
                        raise RequestFailedError(f"{direction_response.status}\n{direction_body}\n지민이에게 도움 요청!")
                    if direction_body["code"] != 0:
                        raise RequestFailedError(f"{direction_body}\n지민이에게 도움 요청!")
                    
                    if duration_only:
                        direction_matrix[i][j] = direction_body["route"]["traoptimal"][0]["summary"]["duration"]
                    else:
                        direction_matrix[i][j] = direction_body["route"]["traoptimal"][0]
                    if self.verbose == 2:
                        output_progress = f"{i*(len(coordinates)-1)+(j if j>i else j+1)}/{len(coordinates)*(len(coordinates)-1)}"
                        print(output_prefix + "."*(TOTAL_OUTPUT_LENGTH_VERBOSE_2 - len(output_prefix) - len(output_progress)) + output_progress, end="\r")
        if self.verbose == 2:
            print(output_prefix + "."*(TOTAL_OUTPUT_LENGTH_VERBOSE_2 - len(output_prefix) - len(OUTPUT_COMPLETE_INDICATOR)) + OUTPUT_COMPLETE_INDICATOR)
        return direction_matrix


if __name__ == "__main__":
    # def coordinate_of(geocode: dict) -> str:
    #     return geocode["x"] + "," + geocode["y"]
    # geocodes = get_geocodes("북원로 1996", "원주시 세동길 13")
    # coordinates = map(coordinate_of, geocodes)
    # result = get_directions(*coordinates)
    # print(result)
    pass
