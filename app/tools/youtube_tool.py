# youtube_tool.py
from langchain_core.tools import BaseTool
from typing import List, Dict
from pydantic import Field
from youtube_service import YouTubeService
import html


class YoutubeSearchTool(BaseTool):
    name: str = "youtube_search"
    description: str = "Search YouTube videos and return metadata"

    youtube_service: YouTubeService = Field(...)

    def _run(self, query: str) -> List[Dict]:
        videos = self.youtube_service.search_videos(query)

        results = []



        for video in videos:

            video_id = video.get("id", {}).get("videoId")
            
            if not video_id:
                continue

            snippet = video.get("snippet", {})
            

            title = html.unescape(snippet.get("title", ""))
            channel_title = snippet.get("channelTitle")
            published_at = snippet.get("publishedAt")
            description = snippet.get("description", "")

            stats = self.youtube_service.get_video_stats(video_id)
            views = int(stats.get("viewCount", 0))

            transcript = self.youtube_service.get_transcript_snippet(video_id)

            results.append({
                "title": title,
                "video_id": video_id,
                "channel": channel_title,
                "published_at": published_at,
                "views": views,
                "description": description,
                "url": f"https://youtube.com/watch?v={video_id}",
                "transcript_snippet": transcript
            })
        return results


    async def _arun(self, query: str):
        raise NotImplementedError()
