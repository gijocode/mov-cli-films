from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Dict

    from mov_cli import Config
    from mov_cli.http_client import HTTPClient

import re

from mov_cli import utils
from mov_cli.scraper import Scraper
from mov_cli import Series, Movie, Metadata, MetadataType
from bs4 import BeautifulSoup

__all__ = ("VadapavScraper",)

class VadapavSerial:
    def __init__(self, data):
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.dir: bool = data["dir"]
        self.parent: str = data["parent"]
        self.mtime: str = data["mtime"]

class VadapavScraper(Scraper):
    def __init__(self, config: Config, http_client: HTTPClient) -> None:
        self.base_url = "https://vadapav.mov"
        super().__init__(config, http_client)

    def search(self, query: str, limit: int = 10) -> Iterable[Metadata]:
        search_url = f"{self.base_url}/s/{query}"
        doc = self.http_client.get(search_url)
        soup = BeautifulSoup(doc, 'html.parser')
        # In this site, all movies are appended with its release year.
        # So it can be used as an inexpensive way to determine the type of media
        movie_pattern = r'.*\(\d{4}\)$'
        results=[]
        for movie in soup.find_all('a',{"class":"directory-entry"}):
            if re.match(movie_pattern,movie.string):
                item_type = MetadataType.MOVIE
                item_year = movie.string[-5:-1]
                item_name = movie.string[:-6]
            else:
                item_type = MetadataType.SERIES
                item_year = "Series" # better than an ugly empty ()
                item_name = movie.string
            results.append(Metadata(id=movie.get('href').strip('/'),title=item_name,type=item_type,year=item_year))
        return results

    def scrape_episodes(self,metadata: Metadata):
        seasons_html = self.http_client.get(f"{self.base_url}/{metadata.id}")
        soup = BeautifulSoup(seasons_html,'html.parser')
        seasons_entries = soup.find_all('a',{'class':'directory-entry'})[1:]
        result = {}
        for i,season in enumerate(seasons_entries):
            season_html = self.http_client.get(self.base_url+season.get('href'))
            soup = BeautifulSoup(season_html,'html.parser')
            episodes_entries = [item for item in soup.find_all('a',{'class':'file-entry'}) if item.string[-4:] != '.srt']
            result[i+1]=len(episodes_entries)

        return result

    def extract_resolution(self,filename):
        # Regular expression to extract resolution information
        match = re.search(r'(\d+)p|4K', filename)
        if match:
            if match.group(1):  # If a numeric resolution is found (e.g., "720p")
                return int(match.group(1))
            else:  # If "4K" is found
                return 2160  # Assumed resolution for 4K
        else:
            return 0  # Default to 0 if resolution is not found

    def scrape(self, metadata: Metadata, episode: Optional[utils.EpisodeSelector] = None) -> Series | Movie:
        if episode is None:
            episode = utils.EpisodeSelector()

        if metadata.type == MetadataType.MOVIE:
            files = self.http_client.get(f"{self.base_url}/{metadata.id}")
            soup = BeautifulSoup(files,'html.parser')
            resources = [x for x in soup.find_all('a',{"class":"file-entry"}) if x.string[-4:]!='.srt']
            subtitles = [x for x in soup.find_all('a',{'class':'file-entry'}) if x.string[-4:]=='.srt']
            subtitle_url = {"en":self.base_url+subtitles[0].get('data-href')} if subtitles else None
            resource_url = ""

            # Always select greatest resolution when there are multiple files
            max_resolution = -1  # Starting with a resolution that's lower than any possible resolution
            for resource in resources:
                resolution = self.extract_resolution(resource.string)
                if resolution > max_resolution:
                    max_resolution = resolution
                    resource_url = resource.get('data-href')

            url = self.base_url+resource_url

            return Movie(
                url,
                title = metadata.title,
                referrer = self.base_url,
                year = metadata.year if metadata.year else "",
                subtitles = subtitle_url
            )

        season = int(episode.season)
        episode_no = int(episode.episode)
        url=None

        season_str = "S"+str(season) if season>9 else "S0"+str(season)
        season_global_str = "Season "+str(season) if season>9 else "Season 0"+str(season)
        episode_str = "E"+str(episode_no) if episode_no>9 else "E0"+str(episode_no)

        files = self.http_client.get(f"{self.base_url}/{metadata.id}")
        soup = BeautifulSoup(files,'html.parser')
        resources = soup.find_all('a',{"class":"directory-entry"})[1:]

        for season_dir in resources:
            if season_dir.string==season_global_str:
                files = self.http_client.get(self.base_url+season_dir.get('href'))
                soup = BeautifulSoup(files,'html.parser')
                resources = [x for x in soup.find_all('a',{"class":"file-entry"}) if x.string[-4:]!='.srt']
                break
        for resource in resources:
            if season_str+episode_str in resource.string:
                url = self.base_url+resource.get('data-href')
                break

        return Series(
            url,
            title = metadata.title,
            referrer = self.base_url,
            episode = episode,
            subtitles = None
        )
