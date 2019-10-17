#                             YouTubeMDBot
#                  Copyright (C) 2019 - Javinator9889
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#                   (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#               GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
from isodate import parse_duration

from ..constants import YOUTUBE
from ..errors import EmptyBodyError


class YouTubeVideoData:
    """
    Obtains YouTube video data and wraps it inside this class. All fields are direct
    access available, so it is possible to access them directly:
     - title
     - id
     - thumbnail
     - artist
     - duration
     - views
     - likes
     - dislikes
    """

    def __init__(self, data: dict, ignore_errors: bool = False):
        """
        By passing a dict with the YouTube data (YouTube API v3), generate and obtain
        the information available from the result.
        :param data: a dictionary with the information obtained from YouTube API.
        :param ignore_errors: whether to ignore or not errors (do not raise exceptions).
        :raises EmptyBodyError when there is no information available and ignored
        errors is False.
        """
        if not data.get("items"):
            raise EmptyBodyError("The data object has no items")
        self.id: str = ""
        self.title: str = ""
        self.thumbnail: str = ""
        self.artist: str = ""
        self.duration: float = 0.0
        self.views: int = 0
        self.likes: int = 0
        self.dislikes: int = 0
        if len(data.get("items")) >= 1:
            content = data.get("items")[0]
            snippet = content.get("snippet")
            details = content.get("contentDetails")
            statistics = content.get("statistics")
            if not snippet and not ignore_errors:
                raise EmptyBodyError("No information available to requested video")
            elif not snippet and ignore_errors:
                snippet_available = False
            else:
                snippet_available = True
            if not details and not ignore_errors:
                raise EmptyBodyError("No video details available")
            elif not details and ignore_errors:
                details_available = False
            else:
                details_available = True
            if not statistics and not ignore_errors:
                raise EmptyBodyError("No statistics available")
            elif not statistics and ignore_errors:
                statistics_available = False
            else:
                statistics_available = True
            c_id = content.get("id", "")
            self.id = c_id.get("videoId", "") if isinstance(c_id, dict) else c_id
            if snippet_available:
                self.title = snippet["title"]
                try:
                    self.thumbnail = snippet["thumbnails"]["maxres"]["url"]
                except KeyError:
                    try:
                        self.thumbnail = snippet["thumbnails"]["high"]["url"]
                    except KeyError:
                        try:
                            self.thumbnail = snippet["thumbnails"]["medium"]["url"]
                        except KeyError:
                            self.thumbnail = snippet["thumbnails"]["default"]["url"]
                self.artist = snippet["channelTitle"]
            if details_available:
                self.duration = parse_duration(details["duration"]).total_seconds()
            if statistics_available:
                self.views = int(statistics["viewCount"])
                self.likes = int(statistics["likeCount"])
                self.dislikes = int(statistics["dislikeCount"])


class YouTubeAPI:
    """
    Wrapper for the YouTube API data. Allows the developer searching for videos and,
    with a given video ID, obtain its data.
    """

    def __init__(self):
        from googleapiclient.discovery import build

        self.__youtube = build(serviceName=YOUTUBE["api"]["name"],
                               version=YOUTUBE["api"]["version"],
                               developerKey=YOUTUBE["key"])

    def search(self, term: str) -> dict:
        """
        Searchs for a video with the specified term.
        :param term: the search term.
        :return: dict with YouTube data - can be wrapped inside "YouTubeVideoData" class.
        """
        return self.__youtube.search().list(
            q=term,
            type="video",
            part="id,snippet",
            maxResults=1
        ).execute()

    @staticmethod
    def video_details(video_id: str) -> YouTubeVideoData:
        """
        Generates a "YouTubeVideoData" object wrapper with the video ID information.
        :param video_id: YouTube video ID.
        :return: YouTubeVideoData object with the available metadata.
        """
        try:
            import ujson as json
        except ImportError:
            import json
        from urllib.request import urlopen

        youtube_information = YOUTUBE.copy()
        api_url = youtube_information["endpoint"].format(video_id, YOUTUBE["key"])
        data = urlopen(url=api_url)
        return YouTubeVideoData(data=json.loads(data.read()), ignore_errors=True)
