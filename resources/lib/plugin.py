# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from codequick import Route, Resolver, Listitem, run
from codequick.utils import urljoin_partial, bold
import urlquick
import xbmcgui
import re
import urllib
import inputstreamhelper

nonDrmBaseUrl = "https://media-content.akamaized.net/"
drmLicence = "https://playlicense.mxplay.com/widevine/proxy?content_id="

languagese = ["ta", "te","ml","kn","en","mr","pa","bn","bho","gu","hi"]
langNames = ["Tamil","Telugu","Malayalam","Kannada","English","Marathi","Punjabi","Bengali","Bhojpuri","Gujarati","Hindi"]
fanArts = ["58/79/Tamil_1580458708325_promo.jpg","89/86/Telugu_1580458096736_promo.jpg",
    "67/0/Malayalam_1580459753008_promo.jpg","37/41/Kannada_1580458557594_promo.jpg",
    "52/8/English_1580458071796_promo.jpg","30/23/Marathi_1580458084801_promo.jpg",
    "79/58/Punjabi_1580458722849_promo.jpg","72/66/Bengali_1580459416363_promo.jpg",
    "87/70/Bhojpuri_1580459428665_promo.jpg","41/66/Gujarati_1580459392856_promo.jpg",
    "98/98/Hindi_1580458058289_promo.jpg"]
@Route.register
def root(plugin, content_type="segment"):
    
    Languagesitem = {"label": "MX Movies", 
    "info":{"plot":"Watch MX Movies"}, 
    "art":{"thumb":"http://www.henry-richard2k.ml/addon_arts/MX_Movies.jpg",
    "fanart":"http://www.henry-richard2k.ml/addon_arts/MX_Movies.jpg"},
    "callback":languagesList}

    TVLanguagesitem = {"label": "MX TV Shows", 
    "info":{"plot":"Watch MX TV Shows"},
    "art":{"thumb":"http://www.henry-richard2k.ml/addon_arts/MX_SHOWS.jpg",
    "fanart":"http://www.henry-richard2k.ml/addon_arts/MX_SHOWS.jpg"}, 
    "callback":TVlanguagesList}

    LiveTVitem = {"label": "MX Live TV", 
    "info":{"plot":"Watch MX TV Shows"}, 
    "art":{"thumb":"http://www.henry-richard2k.ml/addon_arts/MX_TV.jpg",
    "fanart":"http://www.henry-richard2k.ml/addon_arts/MX_TV.jpg"},
    "callback":live_tv}

    

    yield Listitem.from_dict(**Languagesitem)
    yield Listitem.from_dict(**TVLanguagesitem)
    yield Listitem.from_dict(**LiveTVitem)

@Route.register
def languagesList(plugin):
    yield Listitem.search(searchMovies,s_type="movie")
    for lang,name,fanArt in zip(languagese,langNames,fanArts):
        item = Listitem()
        item.label = name
        item.art["thumb"] = "https://jioimages.cdn.jio.com/imagespublic/logos/langGen/"+name+"_1579245819981.jpg"
        item.art["fanart"] = "https://jioimages.cdn.jio.com/imagespublic/"+fanArt
        item.set_callback(movies_list,url="pageNum=1&pageSize=16&isCustomized=true",language=lang)
        yield item

@Route.register
def movies_list(plugin, url,language):
    resp = urlquick.get("https://api.mxplay.com/v1/web/detail/browseItem?&"+url+"&browseLangFilterIds="+language+"&type=1&userid=HOTSTAR%20RANDOM%20ID%20:%201f151757-0147-4261-9cf7-e1abf4cc58cf&platform=com.mxplay.mobile&content-languages=en").json()
    
    for i in resp['items']:
        item = Listitem()
        item.label = i['title']
        item.art["thumb"] = nonDrmBaseUrl + i['imageInfo'][0]['url']
        item.art["fanart"] = nonDrmBaseUrl + i['imageInfo'][0]['url']

        provider = i['stream']['provider']

        if provider != "thirdParty":
            if not i['stream']["drmProtect"]:
                if i['stream'][provider]['dash']['high'] is not None:
                    item.set_callback(playVideo,url=nonDrmBaseUrl + i['stream'][provider]["dash"]['high'],drmKey="")
                else:
                    item.set_callback(playVideo,url=nonDrmBaseUrl + i['stream'][provider]["dash"]['base'],drmKey="")
            else:
                if i['stream'][provider]['dash']['high'] is not None:
                    item.set_callback(playVideo,url=i['stream'][provider]["dash"]['high'],drmKey=drmLicence + i['stream']['videoHash'].replace(":",""))
                    
                else:
                    item.set_callback(playVideo,url=i['stream'][provider]["dash"]['base'],drmKey=drmLicence + i['stream']['videoHash'].replace(":",""))
                    
        else:
            if i['stream'][provider]['webHlsUrl'] is not None:
                item.set_callback(playVideo,url=i['stream'][provider]['webHlsUrl'],drmKey="")
            else:
                item.set_callback(playVideo,url=i['stream'][provider]['hlsUrl'],drmKey="")

        yield item
    yield Listitem.next_page(url=resp['next'],language=language ,callback=movies_list)

@Resolver.register
def playVideo(plugin,url,drmKey):
    if drmKey !="":
        is_helper = inputstreamhelper.Helper("mpd","com.widevine.alpha")
        
        if is_helper.check_inputstream():
            return Listitem().from_dict(**{
            "label": plugin._title,
            "callback": url,
            "properties": {
                
                "inputstream": is_helper.inputstream_addon,
                "inputstream.adaptive.manifest_type": "mpd",
                "inputstream.adaptive.license_type": "com.widevine.alpha",
                "inputstream.adaptive.license_key": drmKey +'||R{SSM}|',
            }
        })

    else:
        if "m3u8" in url:
            return Listitem().from_dict(**{
            "label": "Playing",
            "callback": url,
            "properties": {
                "inputstream.adaptive.manifest_type": "hls",
                "inputstream": "inputstream.adaptive"

            }
        })

        else:
            return Listitem().from_dict(**{
            "label": "Playing",
            "callback": url,
            "properties": {
                "inputstream.adaptive.manifest_type": "mpd",
                "inputstream": "inputstream.adaptive"

            }
        })


@Route.register
def TVlanguagesList(plugin):
    yield Listitem.search(searchTvShows,s_type="shows")

    for lang,name,fanArt in zip(languagese,langNames,fanArts):
        item = Listitem()
        item.label = name
        item.art["thumb"] = "https://jioimages.cdn.jio.com/imagespublic/logos/langGen/"+name+"_1579245819981.jpg"
        item.art["fanart"] = "https://jioimages.cdn.jio.com/imagespublic/"+fanArt
        item.set_callback(tvShows_list,url="pageNum=1&pageSize=16&isCustomized=true",language=lang)
        yield item

@Route.register
def tvShows_list(plugin, url,language):
    resp = urlquick.get("https://api.mxplay.com/v1/web/detail/browseItem?&"+url+"&browseLangFilterIds="+language+"&type=2&userid=HOTSTAR%20RANDOM%20ID%20:%201f151757-0147-4261-9cf7-e1abf4cc58cf&platform=com.mxplay.mobile&content-languages=en").json()
    for i in resp["items"]:
        item = Listitem()
        item.label =i["title"]
        
        item.art["thumb"] = nonDrmBaseUrl + i['imageInfo'][0]['url']
        item.art["fanart"] = nonDrmBaseUrl + i['imageInfo'][0]['url']
        item.set_callback(getSeasons,tvshow_id=i['id'])
        yield item

    yield Listitem.next_page(url=resp['next'],language=language ,callback=tvShows_list)

@Route.register
def getSeasons(plugin,tvshow_id):
    resp = urlquick.get(
        "https://api.mxplay.com/v1/web/detail/collection?type=tvshow&id=" + tvshow_id + "&userid=HOTSTAR%20RANDOM%20ID%20:%201f151757-0147-4261-9cf7-e1abf4cc58cf&platform=com.mxplay.mobile&content-languages=en").json()
    tempImg = nonDrmBaseUrl+resp['imageInfo'][0]['url']
    for seasons in resp["tabs"][0]["containers"]:
            item = Listitem()
            item.label = seasons["title"]
            item.art["thumb"] = nonDrmBaseUrl+resp['imageInfo'][0]['url']
            item.art["fanart"] = nonDrmBaseUrl+resp['imageInfo'][0]['url']
            
            item.set_callback(getEpisodes,next_page="",episodes_id=seasons["id"])
            yield item

@Route.register
def getEpisodes(plugin,next_page, episodes_id):
    resp = urlquick.get(
        "https://api.mxplay.com/v1/web/detail/tab/tvshowepisodes?" + next_page + "&type=season&id=" + episodes_id + "&userid=3369f42b-b2ee-41a2-8cfe-84595a464920&platform=com.mxplay.desktop&content-languages=hi,en,ta,te,kn,mr,pa,ml,bn,bho,gu").json()
    
    for i in resp['items']:
        item = Listitem()
        item.label = i['title']
        item.art["thumb"] = nonDrmBaseUrl + i['imageInfo'][0]['url']
        item.art["fanart"] = nonDrmBaseUrl + i['imageInfo'][0]['url']

        provider = i['stream']['provider']

        if provider != "thirdParty":
            if not i['stream']["drmProtect"]:
                if i['stream'][provider]['dash']['high'] is not None:
                    item.set_callback(playVideo,url=nonDrmBaseUrl + i['stream'][provider]["dash"]['high'],drmKey="")
                else:
                    item.set_callback(playVideo,url=nonDrmBaseUrl + i['stream'][provider]["dash"]['base'],drmKey="")
            else:
                if i['stream'][provider]['dash']['high'] is not None:
                    item.set_callback(playVideo,url=i['stream'][provider]["dash"]['high'],drmKey=drmLicence + i['stream']['videoHash'].replace(":",""))
                    
                else:
                    item.set_callback(playVideo,url=i['stream'][provider]["dash"]['base'],drmKey=drmLicence + i['stream']['videoHash'].replace(":",""))
                    
        else:
            if i['stream'][provider]['webHlsUrl'] is not None:
                item.set_callback(playVideo,url=i['stream'][provider]['webHlsUrl'],drmKey="")
            else:
                item.set_callback(playVideo,url=i['stream'][provider]['hlsUrl'],drmKey="")

        yield item
    yield Listitem.next_page(next_page=resp['next'],episodes_id=episodes_id ,callback=getEpisodes)

@Route.register
def searchMovies(plugin,search_query, s_type):
    resp = urlquick.get(
        "https://api.mxplay.com/v1/web/search/result?query=" + search_query + "&userid=HOTSTAR%20RANDOM%20ID%20:%201f151757-0147-4261-9cf7-e1abf4cc58cf&platform=com.mxplay.mobile&content-languages=en").json()
    
    for i in resp['sections']:
        if i.get('id') in [s_type]:

            for result in i['items']:
                item = Listitem()
                item.label = result['title']
                item.art["thumb"] = nonDrmBaseUrl + result['imageInfo'][0]['url']
                item.art["fanart"] = nonDrmBaseUrl + result['imageInfo'][0]['url']

                provider = result['stream']['provider']

                if provider != "thirdParty":
                    if not result['stream']["drmProtect"]:
                        if result['stream'][provider]['dash']['high'] is not None:
                            item.set_callback(playVideo,url=nonDrmBaseUrl + result['stream'][provider]["dash"]['high'],drmKey="")
                        else:
                            item.set_callback(playVideo,url=nonDrmBaseUrl + result['stream'][provider]["dash"]['base'],drmKey="")
                    else:
                        if result['stream'][provider]['dash']['high'] is not None:
                            item.set_callback(playVideo,url=result['stream'][provider]["dash"]['high'],drmKey=drmLicence + result['stream']['videoHash'].replace(":",""))
                            
                        else:
                            item.set_callback(playVideo,url=result['stream'][provider]["dash"]['base'],drmKey=drmLicence + result['stream']['videoHash'].replace(":",""))
                            
                else:
                    if i['stream'][provider]['webHlsUrl'] is not None:
                        item.set_callback(playVideo,url=result['stream'][provider]['webHlsUrl'],drmKey="")
                    else:
                        item.set_callback(playVideo,url=result['stream'][provider]['hlsUrl'],drmKey="")

                yield item

@Route.register
def searchTvShows(plugin,search_query, s_type):
    resp = urlquick.get(
        "https://api.mxplay.com/v1/web/search/result?query=" + search_query + "&userid=HOTSTAR%20RANDOM%20ID%20:%201f151757-0147-4261-9cf7-e1abf4cc58cf&platform=com.mxplay.mobile&content-languages=en").json()
    for i in resp['sections']:
        if i.get('id') in [s_type]:

            for result in i['items']:
                item = Listitem()
                item.label = result['title']
                item.art["fanart"] = nonDrmBaseUrl + result["imageInfo"][0]["url"]
                item.art["thumb"] = nonDrmBaseUrl + result["imageInfo"][0]["url"]
                item.set_callback(getSeasons,tvshow_id=result["id"])
                yield item

@Route.register
def live_tv(plugin):
    resp = urlquick.get(
    "https://api.mxplay.com/v1/web/live/channels?device-density=2&userid=de6336ad-26f3-40bf-bffe-a2d2386a02b1&platform=com.mxplay.desktop&content-languages=hi,en,ta").json()

    for channel in resp['channels']:
        item = Listitem()
        item.label = channel['title']
        item.art["fanart"] = nonDrmBaseUrl + channel['imageInfo'][0]['url']
        item.art["thumb"] = nonDrmBaseUrl + channel['imageInfo'][0]['url']
        item.set_callback(playVideo,url=channel['stream']['mxplay']['hls']["main"],drmKey="")
        yield item