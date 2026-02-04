import os
from youtube_service import YouTubeService
from youtube_tool import YoutubeSearchTool
import json
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def main():

    service = YouTubeService(api_key=YOUTUBE_API_KEY)

    tool = YoutubeSearchTool(youtube_service=service)
    
    query="Shaheer sheik"
    print("QUERY", query)

    result = tool.run(query)

    for item in result:
        print(json.dumps(item, indent=4))
        print("-" * 50)


if __name__ == "__main__":
    main()