from marshmallow import Schema, fields, INCLUDE, EXCLUDE, ValidationError
import requests
from pprint import pprint
import base64
import json
from afroquotes import config






class YoutubeThumbnail(Schema):
	standard = fields.Dict(required=True, data_key="standard")

	class Meta:
		unknown = INCLUDE

class YoutubeVideoSnippet(Schema):
    publishedAt = fields.Str(required=True, data_key="publishedAt")
    channel_id = fields.Str(required=True, data_key="channelId")
    title = fields.Str(required=True, data_key="title")
    description = fields.Str(required=True)
    thumbnail = fields.Nested(YoutubeThumbnail)
    category_id= fields.Str(required=False, data_key="categoryId")
    channel_title = fields.Str(required=True, data_key="channelTitle")
    tags = fields.List(fields.Str())

    class Meta:
    	unknown=EXCLUDE
    

class YoutubeVideoSchema(Schema):
    kind = fields.Str(required=True)
    etag = fields.Str(required=True)
    youtube_id = fields.Str(required=True, data_key="id")
    snippet = fields.Nested(YoutubeVideoSnippet)
    statistics = fields.Dict(keys=fields.Str(), values=fields.Str(), required=True)
    class Meta:
    	unknown=INCLUDE



class YoutubeChartPage(Schema):
	items = fields.List(fields.Nested(YoutubeVideoSchema), data_key="items")
	next_page = fields.Str(required=False, data_key="nextPageToken")
	page_info = fields.Dict(required=True, key=fields.Str(), value=fields.Int(), data_key="pageInfo")
	class Meta:
		unknown=EXCLUDE

class YoutubeSearchResult(Schema):
	video_id_dict = fields.Dict(keys=fields.Str(), values=fields.Str(), required=True, data_key="id")
	snippet = fields.Nested(YoutubeVideoSnippet)
	class Meta:
		unknown=EXCLUDE

class YoutubeSearchResultPage(Schema):
	items = fields.List(fields.Nested(YoutubeSearchResult))
	next_page = fields.Str(required=False, data_key="nextPageToken")
	page_info = fields.Dict(required=True, key=fields.Str(), value=fields.Int(), data_key="pageInfo")
	class Meta:
		unknown=EXCLUDE

def get_resource(params):
	try:
		response = requests.get("https://www.googleapis.com/youtube/v3/videos", params=params)
		# pprint(json.loads(response.text))

		# with open("yt_chart_response_page.json") as response:
		#     data = json.load(response)
		    # print (data)
		schema = YoutubeChartPage()
		response_data = schema.load(json.loads(response.text))
		# response_data = youtube_chart_schema.load(data)

		return response_data

	except ValidationError as ex:
		pprint(ex.messages)
	


def youtube_call():

	params = {
		"part":"statistics,snippet", 
		"chart":"mostPopular", 
		"key":"AIzaSyA4Ot-KTuTBBTsaJbosvwCMqmPFdeM2eFM",
		"regionCode":"NG",
		"videoCategoryId":"10",
		"pageToken": None,
		"maxResults":50,
	}
	pages = []

	page = get_resource(params)

def search_youtube(q):
	params = {

		"part":"snippet", 
		"q":q,
		"order":"relevance",
		"type":"video", 
		"key":"AIzaSyA4Ot-KTuTBBTsaJbosvwCMqmPFdeM2eFM",
		"regionCode":"NG",
		"videoCategoryId":"10",
		"pageToken": None,
		"maxResults":5,
	}
	try:
		response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
		
		youtube_chart_schema = YoutubeSearchResultPage()
		response_data = youtube_chart_schema.load(json.loads(response.text))


		video_id=response_data["items"][0].get("video_id_dict")
		# data = yt_resource_by_id(video_id.get("videoId"))

		return video_id.get("videoId")

	except ValidationError as ex:
		pprint(ex.messages)

def yt_resource_by_id(resource_id):
	params = {
	"part":"statistics,snippet",
	"key": config.YOUTUBE_KEY,
	"id": resource_id,

	}
	data = get_resource(params)
	return data


def sportify_resource():
	spotify_client = {
	"client_id":SPOTIFY_CLIENT_ID,
	"client_secret":SPOTIFY_SECERET,
	}
	params = {
	"grant_type":"client_credentials",
	}
	tricket = f"{spotify_client.get('client_id')}:{spotify_client.get('client_secret')}"
	# base64_client_id = base64.b64encode(spotify_client.get("client_id").encode('utf8')).decode('utf8')
	# base64_client_secret = base64.b64encode(spotify_client.get("client_secret").encode('utf8')).decode('utf8')
	encoded_key = base64.b64encode(tricket.encode('utf8')).decode('utf8')
	req_token = f"Basic {encoded_key}"
	print(req_token)
	headers = {"Authorization": req_token, "Content-Type":"application/x-www-form-urlencoded"}
	response = requests.post('https://accounts.spotify.com/api/token', headers=headers, params=params)
	print(response.text)



# if __name__ == '__main__':
# 	# yt_resource_by_id("DxV4Yt1vmg0")
# 	# sportify_resource()
# 	search_youtube('Ku lo sa')

# 	# youtube_call()