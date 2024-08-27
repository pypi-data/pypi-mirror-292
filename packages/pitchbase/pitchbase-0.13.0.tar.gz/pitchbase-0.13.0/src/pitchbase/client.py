import os
from pathlib import Path
from typing import Tuple

import m3u8

from .auth import Auth
from .logger import get_logger


class Client:
    def __init__(self, auth: Auth, debug: bool = False):
        self.auth = auth
        self.headers = self.auth.get_header()
        self.logger = get_logger(debug=debug)

    def get_request(self, path: str, params: dict) -> dict:
        rs = self.auth.get_session().get(
            f"{self.auth.get_api_url_base()}{path}", headers=self.headers, params=params
        )
        return rs.json()

    def get_game_schedule(self, filter: str) -> dict:
        return self.get_request(
            "/data/record/game_schedule",
            {
                "filter": filter,
            },
        )

    def get_pitch_data(self, filter: str, limit=300) -> dict:
        return self.get_request(
            "/data/mashup/pitch_data",
            {
                "filter": filter,
                "limit": limit,
            },
        )

    def get_player_master(self, filter: str) -> dict:
        return self.get_request(
            "/data/master/player_master",
            {
                "filter": filter,
            },
        )

    def get_umpire_master(self, filter: str, limit=1000) -> dict:
        return self.get_request(
            "/data/master/umpire_master",
            {
                "filter": filter,
                "limit": limit,
            },
        )

    def get_team_master(self, filter: str) -> dict:
        return self.get_request(
            "/data/master/team_master",
            {
                "filter": filter,
            },
        )

    def get_stadium_master(self, filter: str) -> dict:
        return self.get_request(
            "/data/master/stadium_master",
            {
                "filter": filter,
            },
        )

    def get_movie_angle_upload(self, filter: str, limit: int = 5) -> dict:
        return self.get_request(
            "/movie/angle/upload",
            {
                "filter": filter,
                "limit": limit,
            },
        )

    def get_movie_angle(self, filter: str) -> dict:
        return self.get_request(
            "/movie/angle",
            {
                "filter": filter,
            },
        )

    def get_trackman_record(self, filter: str, limit: int = 300) -> dict:
        return self.get_request(
            "/data/mashup/trackman_record",
            {
                "filter": filter,
                "limit": limit,
            },
        )

    def get_charlyze_record(self, resource_name: str, filter: str) -> dict:
        return self.get_request(
            f"/data/charlyze/record/{resource_name}",
            {
                "filter": filter,
            },
        )

    def get_event_info(self, filter: str, limit: int = 300) -> dict:
        return self.get_request(
            "/data/record/event_info",
            {
                "filter": filter,
                "limit": limit,
            },
        )

    def get_batter_record(self, filter: str, limit: int = 300) -> dict:
        return self.get_request(
            "/data/record/batter_record",
            {
                "filter": filter,
                "limit": limit,
            },
        )

    def download_movie_angle_upload_movie_file_path(
        self, filter: str, download_dir: str
    ) -> Tuple[dict, list]:
        rs = self.get_movie_angle_upload(filter)
        files = self._download_files(rs.get("results"), "movie_file_path", download_dir)
        return rs, files

    def download_ts_from_m3u8(self, m3u8_url: str, download_dir: str) -> list:
        base_uri, m3u8_basename = os.path.split(m3u8_url)
        local_path = f"{download_dir}/{m3u8_basename}"
        self.download(local_path=local_path, url=m3u8_url)
        playlist = m3u8.load(local_path)
        segments = playlist.segments.by_key(None)
        files = []
        for segment in segments:
            ts_basename = segment.uri
            ts_local_path = f"{download_dir}/{ts_basename}"
            if os.path.exists(ts_local_path):
                self.logger.debug(f"already exists => {ts_local_path}")
            else:
                segment_uri = f"{base_uri}/{ts_basename}"
                self.download(local_path=ts_local_path, url=segment_uri)
            files.append(ts_local_path)
        return files

    def download_pitch_data_playlist_file_path(self, filter: str, download_dir: str):
        rs = self.get_pitch_data(filter)
        files = self._download_files(
            rs.get("results"), "playlist_file_path", download_dir
        )
        return rs, files

    def _download_files(self, results, key: str, download_dir: str):
        files = []
        os.makedirs(download_dir, exist_ok=True)
        for result in results:
            url = result.get(key)
            local_path = f"{download_dir}/{os.path.basename(url)}"
            if os.path.exists(local_path):
                self.logger.debug(f"already exists => {local_path}")
            else:
                self.download(local_path, url)
            files.append(local_path)
        return files

    def download(self, local_path: str, url: str):
        self.logger.debug(f"stream downloading... => {local_path}")
        response = self.auth.get_session().get(
            url,
            stream=True,
        )
        path = Path(local_path)
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=512 * 1024):
                f.write(chunk)
        size_gb = os.path.getsize(path) / 1024 / 1024 / 1024
        self.logger.debug(f"download done. => {local_path} ({size_gb} GB)")
