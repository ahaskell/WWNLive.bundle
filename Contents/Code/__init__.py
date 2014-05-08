

NAME = 'WWNLive'
BASE_URL = 'http://wwnlive.com'
promotions = []
####################################################################################################

#TODO Clean up the authenticate to recognize failure on login.
def authenticate():
    Log(Prefs['wwwnlive_user'])
    Log(Prefs['wwnlive_pwd'])
    credentials = {"email":  Prefs['wwwnlive_user'], "password": Prefs['wwnlive_pwd'], "Login": "go"}
    login = HTTP.Request(BASE_URL + "/signin.php", values=credentials)
    account_home = HTML.ElementFromString(login.content)
    Log(login.content)
    for link in account_home.iter('a'):
        if link.get('href') is not None and Regex("account.php\?gid=[0-9]").search(link.get("href")) is not None:
            promotions.append((link.getchildren()[0].get('alt'), link.getchildren()[0].get('src'), link.get('href')))
    promotions.reverse()


def ValidatePrefs():
    authenticate()
  
  
####################################################################################################
def Start():
    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0'


###################################################################################################


@handler('/video/wwnlive', NAME)
def MainMenu():
    #TODO when not authenticated need to show Ondemand conent instead of account content
    authenticate()
    oc = ObjectContainer(no_cache=True)
    oc.add(MovieObject(
        title="Intro",
        url="wwnlive://wwn-HLR_360p.mp4"
    ))
    for promotion in promotions:
        oc.add(DirectoryObject(
            key=Callback(Promotion, root=promotion[2], title=promotion[0], logo=promotion[1]),
            thumb=BASE_URL + "/" + promotion[1],
            title=promotion[0]
        ))
    return oc


@route('/video/wwnlive/promotion')
def Promotion(root=None, title=None, logo=None):
    oc = ObjectContainer(title2=title, no_cache=True)
    promotion = HTTP.Request(BASE_URL + root, immediate=True)
    promotion = HTML.ElementFromString(promotion.content)
    #Log("Events")
    for event in promotion.find_class("EventBox"):
        event_logo = event.find_class('eBoxRight')[0].getchildren()[0].get('src')
        #Since WWN lists upcoming events all the time we need to check if it is applicable to the current Promotion
        if event_logo == logo:
            Log(event.find_class('eName')[0].text_content().strip())
            Log(event.find_class('eBoxAccess')[0].find("a").get("href"))
    return oc

