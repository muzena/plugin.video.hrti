# Module: main
# Author: Nirvana
# Created on: 20.12.2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Example video plugin that is compatible with Kodi 19.x "Matrix" and above
"""
import sys
from urllib.parse import urlencode, urlparse, parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon
import posixpath
from lib.hrti_api2 import HRTiAPI
from lib.common import Common

_HANDLE = int(sys.argv[1])
_URL = sys.argv[0]

plugin = Common(
    addon=xbmcaddon.Addon(),
    addon_handle=_HANDLE,
    addon_url=_URL
)

api = HRTiAPI(plugin)
channels = api.get_channels()
catalog_structure = api.get_catalog_structure()

CATEGORIES = ['TV Channels', 'Radio Channels']


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(_URL, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.
    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.
    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.
    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    return CATEGORIES


def path_parse(path_string, *, normalize=True, module=posixpath):
    result = []
    if normalize:
        tmp = module.normpath(path_string)
    else:
        tmp = path_string
    while tmp != "/":
        (tmp, item) = module.split(tmp)
        result.insert(0, item)
    return result


def get_children(node, wanted_subcategory):
    children = None
    for child in node:
        if child['ReferenceId'] == wanted_subcategory:
            children = child['Children']
    return children


def list_subcategories(path):
    current_node = catalog_structure
    parent_category = ""
    if path is not None:
        sections = path_parse("/"+path)
        i = 0
        while i < len(sections):
            current_node = get_children(current_node, sections[i])
            parent_category = sections[i]
            i += 1
    count = 0
    for child in current_node:
        if child['ParentReferenceId'] == parent_category:
            list_item = xbmcgui.ListItem(label=child['Name'])
            list_item.setArt({'thumb': child['PosterLandscape'],
                              'fanart': child['PosterLandscape']})
            list_item.setInfo('video', {'title': child['Name'],
                                        'genre': child['Name'],
                                        'mediatype': 'video'})
            if path is None:
                url = get_url(action='listing', category=child['ReferenceId'])
            else:
                url = get_url(action='listing', category=path+"/"+child['ReferenceId'])
            is_folder = True
            xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
            count += 1
    if count == 0:
        catalog = api.get_catalog(parent_category, 250, 1)
        # number = catalog['NumberOfItems']
        # print(catalog)
        for catalog_entry in catalog['Items']:
            list_item = xbmcgui.ListItem(label=catalog_entry['Title'])
            # catalog_entry['VodData'] AvailableFrom, Duration, ProductionYear
            # catalog_entry['SeriesData'] {'LastEpisodeNumber': 1,
            # 'LastSeasonNumber': 1, 'SeriesName': '',
            # 'SeriesReferenceId': '44425aa1-0a72-7f51-9371-046be46ed537'}
            # catalog_entry['Type']
            # catalog_entry['VodCategoryNames']
            # catalog_entry['AvailableFrom']
            list_item.setArt({'thumb': catalog_entry['PosterLandscape'],
                              'icon': catalog_entry['PosterLandscape'],
                              'fanart': catalog_entry['PosterPortrait']})
            list_item.setProperty('IsPlayable', 'true')
            metadata = {'mediatype': 'video'}
            list_item.setInfo('video', metadata)
            url = get_url(action='play', video=catalog_entry['ReferenceId'])
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)

    if path is not None:
        xbmcplugin.endOfDirectory(_HANDLE)


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, 'My Video Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.

        # list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
        #                'icon': VIDEOS[category][0]['thumb'],
        #               'fanart': VIDEOS[category][0]['thumb']})

        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
    list_subcategories(None)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.
    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_HANDLE, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_HANDLE, 'videos')
    # Get the list of videos in the category.
    # Iterate through videos.
    for channel in channels:
        if (channel['Radio'] and category == 'Radio Channels') or (not channel['Radio'] and category == 'TV Channels'):
            list_item = xbmcgui.ListItem(label=channel['Name'])
            list_item.setArt({'thumb': channel['Icon'], 'icon': channel['Icon'], 'fanart': channel['Icon']})
            list_item.setProperty('IsPlayable', 'true')

            # for video in videos:
            # Create a list item with a text label and a thumbnail image.
            # list_item = xbmcgui.ListItem(label=video['name']
            # Set additional info for the list item.
            # 'mediatype' is needed for skin to display info for this ListItem correctly.
            if channel['Radio']:
                metadata = {'mediatype': 'audio'}
                list_item.setInfo('music', metadata)
            else:
                metadata = {'mediatype': 'video'}
                list_item.setInfo('video', metadata)

            url = get_url(action='play', video=channel['StreamingURL'])
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)
            # Add a sort method for the virtual folder items (alphabetically, ignore articles)
            # xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_HANDLE)


def authorize_and_play(filename, contenttype, content_ref_id):
    parts = urlparse(filename)
    directories = parts.path.strip('/').split('/')
    contentdrmid = directories[0] + "_" + directories[1]
    print(contentdrmid)
    result = api.authorize_session(contenttype, content_ref_id, contentdrmid, None, None)
    print(result)


def play_video(path):
    """
    Play a video by the provided path.
    :param path: Fully-qualified video URL
    :type path: str
    """
    print("play " + path)
    parts = urlparse(path)
    if parts.scheme == "":
        voddetails = api.get_vod_details(path)
        print(voddetails)
        filename = voddetails['FileName']
        # result = api.authorize_session("svod", path, None, "hrtvodorigin_"+path+".smil", None)
        authorize_and_play(filename, "svod", path)
        print(result)
    else:
        # Create a playable item with a path to play.
        for channel in channels:
            if path == channel['StreamingURL']:
                refid = channel['ReferenceID']
                print(refid)
                parts = urlparse(path)
                directories = parts.path.strip('/').split('/')
                contentid = directories[0] + "_" + directories[1]
                print(contentid)
                result = api.authorize_session("tlive", refid, contentid, None, refid)
                print(result)
                result2 = api.report_session_event(result['SessionId'], refid)
                drmid = result['DrmId']
                print(result2)
                print(drmid)

                user_agent = "kodi plugin for hrti.hrt.hr (python)"

                license_str = api.get_license()
                list_item = xbmcgui.ListItem(path=path)

                list_item.setMimeType('application/xml+dash')
                list_item.setContentLookup(False)

                list_item.setProperty('inputstream', 'inputstream.adaptive')
                list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
                list_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
                list_item.setProperty('inputstream.adaptive.license_key',
                                      "https://lic.drmtoday.com/license-proxy-widevine/cenc/" +
                                      "|User-Agent=" + user_agent +
                                      "&Content-Type=text%2Fplain" +
                                      "&origin=https://hrti.hrt.hr" +
                                      "&referer=https://hrti.hrt.hr" +
                                      "&dt-custom-data=" + license_str + "|R{SSM}|JBlicense")

                list_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')

                xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=list_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    deviceid = plugin.uniq_id()
    api.DEVICE_ID = deviceid
    xbmc.log("DeviceID: "+str(deviceid),  level=xbmc.LOGDEBUG)

    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    print("Params" + str(params))
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            if params['category'] == 'TV Channels' or params['category'] == 'Radio Channels':
                list_videos(params['category'])
            else:
                list_subcategories(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        elif params['action'] == 'logout':
            api.logout()
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
