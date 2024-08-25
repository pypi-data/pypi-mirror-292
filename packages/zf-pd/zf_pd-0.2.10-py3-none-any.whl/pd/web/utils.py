from urllib.parse import urlparse
from re import sub as re_sub


def get_host(link: str) -> str:
    host = urlparse(link).netloc
    host = re_sub(r"^www\.", "", host)
    host = host.replace("/", "")
    host = re_sub(r"\.co.*", "", host)
    return host


if __name__ == "__main__":
    print(get_host("https://www.google.com/api/v1/search?q=test"))
    print(get_host("https://zeffmuks.com/projects/project.json"))
