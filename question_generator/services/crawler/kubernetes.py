import requests
from bs4 import BeautifulSoup

def get_kubernetes_release():
    url = "https://kubernetes.io/releases/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        release_details = soup.find_all("div", class_="release-details")

        if release_details:
            first_release = release_details[0].get_text(strip=True)
            latest_release = None
            released_date = None

            if "Latest Release:" in first_release:
                latest_release_start = first_release.find("Latest Release:") + len("Latest Release:")
                latest_release_end = first_release.find("(released:")
                latest_release = first_release[latest_release_start:latest_release_end].strip()

            if "(released:" in first_release:
                released_start = first_release.find("(released:") + len("(released:")
                released_end = first_release.find(")", released_start)
                released_date = first_release[released_start:released_end].strip()

            return latest_release, released_date
    return None, None