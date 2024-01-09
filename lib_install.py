from os import path
import requests


if __name__ == "__main__":

    dir_path = path.dirname(path.abspath(__file__))
    lib_path = path.join(dir_path, "src/web/GuiPages/lib")

    with open(f"{lib_path}/lib-requirements.txt") as requirements_file:

        for line in requirements_file:

            url = line.strip()

            print(f"Downloading {url}")

            filename = path.basename(url)

            response = requests.get(url)

            with open(path.join(lib_path, filename), "wb") as output_file:
                output_file.write(response.content)
