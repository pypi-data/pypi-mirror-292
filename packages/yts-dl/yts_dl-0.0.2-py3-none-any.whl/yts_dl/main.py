import os
import logging
import colorlog
import subprocess
import multiprocessing
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


logger = colorlog.getLogger()


class Downloader:
    desktop_path = Path(os.path.expanduser("~")) / "Desktop"
    downloads_path = desktop_path / "downloads"

    def __init__(self):
        self.setup_logger()

        urls = self.extract_urls_from_txt_files()
        if not len(urls):
            return

        commands = self.prepare_commands(urls)
        results = self.run_commands_in_parallel(commands, self.downloads_path)

        for command, output, error in results:
            logger.info(command)
            if output:
                logger.info(output)
            if error:
                logger.error(error)

    def setup_logger(self):
        bold_seq = "\033[1m"

        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                f"{bold_seq}%(log_color)s[%(asctime)s] %(levelname)s\n%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "white",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.WARN)

    def extract_urls_from_txt_files(self):
        urls_file = os.path.join(self.desktop_path, "urls.txt")

        urls = set()
        if os.path.exists(urls_file):
            with open(urls_file, "r") as file:
                lines = file.readlines()
                for line in lines:
                    url = line.strip()
                    if url:
                        urls.add(url)

            if not len(urls):
                logger.warning(
                    "No URLs found inside the 'urls.txt' file on your Desktop.\nPlease add the URLs you want to download and re-run the script."
                )
        else:
            with open(urls_file, "w+") as file:
                pass

            logger.warning(
                "No 'urls.txt' file found on your Desktop. A new file is created for you.\nPlease add the URLs you want to download and re-run the script."
            )

        return list(urls)

    def process_urls(self, urls):
        urls_youtube = []
        urls_spotify = []

        for url in urls:
            parsed_url = urlparse(url)
            is_youtube = (
                "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc
            )
            is_spotify = not is_youtube and "spotify.com" in parsed_url.netloc

            if not is_youtube and not is_spotify:
                logger.warning(f"Unsupported URL format: {url}")
                break

            cleaned_query = ""
            query_params = parse_qs(parsed_url.query)
            if query_params:
                if is_youtube:
                    first_param_key = next(iter(query_params.keys()))
                    if first_param_key == "v":
                        cleaned_query = urlencode(
                            {first_param_key: query_params[first_param_key][0]}
                        )
            clean_url = urlunparse(parsed_url._replace(query=cleaned_query))

            if is_youtube:
                urls_youtube.append(clean_url)

            elif is_spotify:
                urls_spotify.append(clean_url)

        return urls_youtube, urls_spotify

    def prepare_commands(self, urls):
        commands = []
        urls_youtube, urls_spotify = self.process_urls(urls)

        for url in urls_youtube:
            commands.append(f'yt-dlp {url} -o "%(title)s.%(ext)s"')

        output_spotify = self.downloads_path / f'"{{list-name}}/{{artists}} - {{title}}.{{output-ext}}"'
        if len(urls_spotify):
            commands.append(f"spotdl download {" ".join(urls_spotify)} --output {output_spotify} --threads {multiprocessing.cpu_count()}")

        return commands

    def run_command(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return (command, result.stdout.decode("utf-8"), None)
        except subprocess.CalledProcessError as e:
            return (command, None, e.stderr.decode("utf-8"))

    def run_commands_in_parallel(self, commands, out_dir):
        results = []
        pwd = os.getcwd()
        os.makedirs(out_dir, exist_ok=True)
        os.chdir(out_dir)

        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = {executor.submit(self.run_command, cmd): cmd for cmd in commands}
            for future in as_completed(futures):
                cmd = futures[future]
                try:
                    output, error = future.result()[1:]
                    results.append((cmd, output, error))
                except Exception as exc:
                    results.append((cmd, None, str(exc)))

        os.chdir(pwd)
        return results


def downloader():
    s = Downloader()


if __name__ == "__main__":
    downloader()
