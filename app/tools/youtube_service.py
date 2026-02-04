# youtube_service.py
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeService:
    def __init__(self, api_key: str):
        self.client = build("youtube", "v3", developerKey=api_key)

    def search_videos(self, query: str, max_results: int = 5):
        response = self.client.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            order="viewCount" 
        ).execute()

        return response.get("items", [])

    def get_video_stats(self, video_id: str):
        response = self.client.videos().list(
            part="statistics",
            id=video_id
        ).execute()

        return response["items"][0]["statistics"]

    def get_transcript_snippet(self, video_id: str, max_chars: int = 280):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join([t["text"] for t in transcript])
            return text[:max_chars]
        except Exception:
            return ""
