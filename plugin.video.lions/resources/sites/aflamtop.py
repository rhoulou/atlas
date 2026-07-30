# -*- coding: utf-8 -*-
# zombi https://github.com/zombiB/zombi-addons/

import re
	
from resources.lib.util import Quote
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.comaddon import VSlog, siteManager, addon
from resources.lib.parser import cParser
from resources.lib.Styling import getGenreIcon, getThumb, getFunc
from bs4 import BeautifulSoup

ADDON = addon()
icons = ADDON.getSetting('defaultIcons')
LOGO = 'special://home/addons/plugin.video.lions/resources/sites/logos/aflamtop.png'

SITE_IDENTIFIER = 'aflamtop'
SITE_NAME = 'Aflamtop'
SITE_DESC = 'arabic vod'
 
URL_MAIN = siteManager().getUrlMain(SITE_IDENTIFIER)

MOVIE_EN = (URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%a7%d8%ac%d9%86%d8%a8%d9%8a%d8%a9/', 'showMovies')
MOVIE_AR = (URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%b9%d8%b1%d8%a8%d9%8a%d8%a9/', 'showMovies')
MOVIE_HI = (URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d9%87%d9%86%d8%af%d9%8a%d8%a9/', 'showMovies')
MOVIE_ASIAN = (URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%a7%d8%b3%d9%8a%d9%88%d9%8a%d8%a9/', 'showMovies')
MOVIE_DUBBED = (URL_MAIN + '/category/%d9%85%d9%84%d8%aa%d9%8a%d9%85%d9%8a%d8%af%d9%8a%d8%a7-%d9%85%d8%af%d8%a8%d9%84%d8%ac%d8%a9/', 'showMovies')
MOVIE_CLASSIC = (URL_MAIN + '/tag/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d8%a7%d8%a8%d9%8a%d8%b6-%d9%88%d8%a7%d8%b3%d9%88%d8%af/', 'showMovies')
MOVIE_ADULT = (URL_MAIN + '/tag/%d9%84%d9%84%d9%83%d8%a8%d8%a7%d8%b1-%d9%81%d9%82%d8%b7/', 'showMovies')
MOVIE_RECENT = (URL_MAIN + '/recent', 'showMovies')
KID_MOVIES = (URL_MAIN + '/category/%d8%a7%d9%84%d8%a7%d9%86%d9%8a%d9%85%d9%8a%d8%b4%d9%86/', 'showMovies')
MOVIE_GENRES = (True, 'showGenres')
MOVIE_YEARS = (True, 'showYears')
MOVIE_QUALITY = (True, 'showQuality')

DOC_NEWS = (URL_MAIN + '/category/%d8%a7%d9%81%d9%84%d8%a7%d9%85/%d8%a7%d9%81%d9%84%d8%a7%d9%85-%d9%88%d8%ab%d8%a7%d8%a6%d9%82%d9%8a%d8%a9/', 'showMovies')


URL_SEARCH = (URL_MAIN + '/?s=', 'showMovies')
URL_SEARCH_MOVIES = (URL_MAIN + '/?s=', 'showMovies')
FUNCTION_SEARCH = 'showMovies'
 
def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'SEARCH_MOVIES', icons + '/Search.png', oOutputParameterHandler)
    
    showSiteCats()
 
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1] , "Movies by Genres", icons + "/Genres.png", oOutputParameterHandler)  

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_YEARS[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_YEARS[1] , "Movies by Year", icons + "/Calendar.png", oOutputParameterHandler) 

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_QUALITY[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_QUALITY[1] , "Movies by Quality", icons + "/HD.png", oOutputParameterHandler) 
    # #oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    # #oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1], 'أقسام الموقع', icons + '/Icon.png', oOutputParameterHandler)
   
# #    oOutputParameterHandler.addParameter('siteUrl', SERIE_GENRES[0])
# #    oGui.addDir(SITE_IDENTIFIER, SERIE_GENRES[1], 'مسلسلات', icons + '/TVShows.png', oOutputParameterHandler) 
 
    # oOutputParameterHandler = cOutputParameterHandler()
    # oOutputParameterHandler.addParameter('siteUrl', MOVIE_EN[0])
    # oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام أجنبية', icons + '/MoviesEnglish.png', oOutputParameterHandler)
   
    # oOutputParameterHandler = cOutputParameterHandler()
    # oOutputParameterHandler.addParameter('siteUrl', MOVIE_AR[0])
    # oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام عربية', icons + '/Arabic.png', oOutputParameterHandler)
 
    # oOutputParameterHandler = cOutputParameterHandler()
    # oOutputParameterHandler.addParameter('siteUrl', MOVIE_ASIAN[0])
    # oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام أسيوية', icons + '/Asian.png', oOutputParameterHandler)
   
    # oOutputParameterHandler = cOutputParameterHandler()
    # oOutputParameterHandler.addParameter('siteUrl', MOVIE_HI[0])
    # oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام هندية', icons + '/Hindi.png', oOutputParameterHandler)
    
    # oOutputParameterHandler = cOutputParameterHandler()
    # oOutputParameterHandler.addParameter('siteUrl', MOVIE_CLASSIC[0])
    # oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام كلاسيكية', LOGO, oOutputParameterHandler)

    # oOutputParameterHandler = cOutputParameterHandler()
    # oOutputParameterHandler.addParameter('siteUrl', MOVIE_DUBBED[0])
    # oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام مدبلجة', icons + '/Dubbed.png', oOutputParameterHandler) 
 
    # oOutputParameterHandler = cOutputParameterHandler()
    # oOutputParameterHandler.addParameter('siteUrl', KID_MOVIES[0])
    # oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'أفلام كرتون', icons + '/Cartoon.png', oOutputParameterHandler)   
    
# #   oOutputParameterHandler = cOutputParameterHandler()
# #   oOutputParameterHandler.addParameter('siteUrl', DOC_NEWS[0])
# #   oGui.addDir(SITE_IDENTIFIER, 'showMovies', 'برامج وثائقية', icons + '/Documentary.png', oOutputParameterHandler 
 
    oGui.setEndOfDirectory() 
    
def showSearch():
    oGui = cGui()
 
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/?s='+sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return

def showSiteCats():
    oGui = cGui()

    cats = [
        ("افلام اجنبية", MOVIE_EN[0]),
        ("افلام عربية", MOVIE_AR[0]),
        ("افلام هندية", MOVIE_HI[0]),
        ("افلام اسيوية", MOVIE_ASIAN[0]),
        ("الانيميشن", KID_MOVIES[0]),
        ("افلام وثائقية", DOC_NEWS[0]),
        ("افلام كلاسيكية", MOVIE_CLASSIC[0]),
        ("افلام مدبلجة", MOVIE_DUBBED[0]),
        ("افلام للكبار فقط", MOVIE_ADULT[0]),
        ("المضاف حديثا", MOVIE_RECENT[0]),
    ]
 
    for sTitle,sUrl in cats:
        
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, getFunc(sTitle), sTitle, getThumb(sTitle), oOutputParameterHandler)       

    #oGui.setEndOfDirectory()    

def showGenres():
    oGui = cGui()

    genres = [
        ("افلام الاكشن", URL_MAIN + '/genre/%d8%a7%d9%83%d8%b4%d9%86/'),
        ("افلام الرعب", URL_MAIN + '/genre/%d8%b1%d8%b9%d8%a8/'),
        ("افلام الخيال العلمي", URL_MAIN + '/genre/%d8%ae%d9%8a%d8%a7%d9%84-%d8%b9%d9%84%d9%85%d9%8a/'),
        ("افلام الرومانسية", URL_MAIN + '/genre/%d8%b1%d9%88%d9%85%d8%a7%d9%86%d8%b3%d9%8a/'),
        ("افلام الفانتازيا", URL_MAIN + '/genre/%d9%81%d8%a7%d9%86%d8%aa%d8%a7%d8%b2%d9%8a%d8%a7/'),
        ("افلام الكوميديا", URL_MAIN + '/genre/%d9%83%d9%88%d9%85%d9%8a%d8%af%d9%8a/'),
        ("افلام الجريمة", URL_MAIN + '/genre/%d8%ac%d8%b1%d9%8a%d9%85%d8%a9/'),
        ("افلام الغموض", URL_MAIN + '/genre/%d8%ba%d9%85%d9%88%d8%b6/'),
        ("افلام حربية", URL_MAIN + '/genre/%d8%ad%d8%b1%d8%a8%d9%8a/'),
        ("افلام الدراما", URL_MAIN + '/genre/%d8%af%d8%b1%d8%a7%d9%85%d8%a7/'),
        ("افلام الويسترن", URL_MAIN + '/genre/%d9%88%d9%8a%d8%b3%d8%aa%d8%b1%d9%86/'),
    ]
 
    for sTitle,sUrl in genres:
        
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, getFunc(sTitle), sTitle, getGenreIcon(sTitle), oOutputParameterHandler)       

    oGui.setEndOfDirectory()  

def showQuality():
    oGui = cGui()

    qualities = [
        ("Bluray", URL_MAIN + '/?cat=&genre=&Quality=[bluray]&year='),
        ("1080p", URL_MAIN + '/?cat=&genre=&Quality=[1080p]&year='),
        ("720p", URL_MAIN + '/?cat=&genre=&Quality=[720p]&year='),
        ("480p", URL_MAIN + '/?cat=&genre=&Quality=[480p]&year='),
        ("WEB-DL", URL_MAIN + '/?cat=&genre=&Quality=[web-dl]&year='),
        ("HDRip", URL_MAIN + '/?cat=&genre=&Quality=[hdrip]&year='),
    ]
 
    for sTitle,sUrl in qualities:
        
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, getFunc(sTitle), sTitle, icons + "/HD.png", oOutputParameterHandler)       

    oGui.setEndOfDirectory() 

def showYears():
    oGui = cGui()

    years = []
    for y in range(2026, 1990, -1):
        years.append((str(y), URL_MAIN + '/?cat=&genre=&Quality=&year=[%d]' % y))
 
    for sTitle,sUrl in years:
        
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, getFunc(sTitle), sTitle, icons + "/Calendar.png", oOutputParameterHandler)       

    oGui.setEndOfDirectory()
    

def showSearchSeries(sSearch = ''):
    oGui = cGui()
    if sSearch:
      sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')
 
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
     # (.+?) ([^<]+) .+?

    sPattern = '<article aria-label="post"><a href="(.+?)">.+?<li aria-label="episode"><em>.+?</em>(.+?)</li><li aria-label="year">(.+?)</li>.+?<li>الموسم(.+?)</li>.+?</em>(.+?)<em>.+?data-src="(.+?)" width'
		
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
	
    itemList = []
    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()    
        for aEntry in aResult[1]:
 
            sTitle = aEntry[4]+'S'+aEntry[3]+' E'+aEntry[1]
            sTitle = sTitle.replace("S ","S")
            siteUrl = aEntry[0] + "watching/"
            sThumb = aEntry[5]
            sYear = ""
            sDesc = ""

            if sTitle not in itemList:
                itemList.append(sTitle)


                oOutputParameterHandler.addParameter('siteUrl',siteUrl)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('sYear', sYear)
                oOutputParameterHandler.addParameter('sDesc', sDesc)
                
                oGui.addTV(SITE_IDENTIFIER, 'showServer', sTitle, '', sThumb, sDesc, oOutputParameterHandler)


 
    if not sSearch:
          # ([^<]+) .+?
        sStart = '</section>'
        sEnd = '</ul>'
        sHtmlContent = oParser.abParse(sHtmlContent, sStart, sEnd)

        sPattern = '<li><a href="([^<]+)">([^<]+)</a>'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        
        
        if aResult[0]:
            oOutputParameterHandler = cOutputParameterHandler()    
            for aEntry in aResult[1]:
     
                sTitle = aEntry[1]
                
                sTitle =  "PAGE " + sTitle
                sTitle =   '[COLOR red]'+sTitle+'[/COLOR]'
                siteUrl = aEntry[0]
                sThumb = ""


                oOutputParameterHandler.addParameter('siteUrl',siteUrl)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                
                oGui.addDir(SITE_IDENTIFIER, 'showSearchSeries', sTitle, '', oOutputParameterHandler)

        oGui.setEndOfDirectory() 
def showSeriesSearch():
    oGui = cGui()
 
    sSearchText = oGui.showKeyBoard()
    if sSearchText:
        sUrl = URL_MAIN + '/?s='+sSearchText
        showSeries(sUrl)
        oGui.setEndOfDirectory()
        return

 
def showMovies(sSearch = ''):
    oGui = cGui()
    if sSearch:
      sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')



    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = '<a href="([^"]+)"[^>]*title="([^"]+)"[^>]*class="recent--block"'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
	
	
    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()    
        for aEntry in aResult[1]:
            if 'مسلسل' in aEntry[1] or 'موسم' in aEntry[1] or 'الحلقة' in aEntry[1]:
               continue
 
            sTitle = aEntry[1].replace("مشاهدة","").replace("مسلسل","").replace("انمي","").replace("مترجمة","").replace("مترجم","").replace("برنامج","").replace("فيلم","").replace("والأخيرة","").replace("مدبلج للعربية","مدبلج").replace("مدبلج","[arabic]").replace("والاخيرة","").replace("كاملة","").replace("حلقات كاملة","").replace("اونلاين","").replace("مباشرة","").replace("انتاج ","").replace("جودة عالية","").replace("كامل","").replace("HD","").replace("السلسلة الوثائقية","").replace("الفيلم الوثائقي","").replace("اون لاين","")
            siteUrl = aEntry[0]
            sThumb = ''
            sDesc = ''
            sYear = ''
            m = re.search('([0-9]{4})', sTitle)
            if m:
                sYear = str(m.group(0))
                sTitle = sTitle.replace(sYear,'')

            oOutputParameterHandler.addParameter('siteUrl',siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sYear', sYear)
            oOutputParameterHandler.addParameter('sDesc', sDesc)
			
            oGui.addMovie(SITE_IDENTIFIER, 'showServer', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

        
 
    if not sSearch:
        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)
        oGui.setEndOfDirectory()

 
def showSeries(sSearch = ''):
    import requests
    oGui = cGui()
    if sSearch:
      sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')



    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
 # ([^<]+) .+?
    sPattern = '<a href="([^"]+)"[^>]*title="([^"]+)"[^>]*class="recent--block"'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
	
    itemList = []
    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()    
        for aEntry in aResult[1]:
 
            sTitle = aEntry[1].replace("مشاهدة","").replace("مسلسل","").replace("انمي","").replace("مترجمة","").replace("مترجم","").replace("برنامج","").replace("فيلم","").replace("والأخيرة","").replace("مدبلج للعربية","مدبلج").replace("والاخيرة","").replace("كاملة","").replace("حلقات كاملة","").replace("اونلاين","").replace("مباشرة","").replace("انتاج ","").replace("جودة عالية","").replace("كامل","").replace("HD","").replace("السلسلة الوثائقية","").replace("الفيلم الوثائقي","").replace("اون لاين","")
            
            sDisplayTitle = sTitle.replace("الموسم العاشر","S10").replace("الموسم الحادي عشر","S11").replace("الموسم الثاني عشر","S12").replace("الموسم الثالث عشر","S13").replace("الموسم الرابع عشر","S14").replace("الموسم الخامس عشر","S15").replace("الموسم السادس عشر","S16").replace("الموسم السابع عشر","S17").replace("الموسم الثامن عشر","S18").replace("الموسم التاسع عشر","S19").replace("الموسم العشرون","S20").replace("الموسم الحادي و العشرون","S21").replace("الموسم الثاني و العشرون","S22").replace("الموسم الثالث و العشرون","S23").replace("الموسم الرابع والعشرون","S24").replace("الموسم الخامس و العشرون","S25").replace("الموسم السادس والعشرون","S26").replace("الموسم السابع والعشرون","S27").replace("الموسم الثامن والعشرون","S28").replace("الموسم التاسع والعشرون","S29").replace("الموسم الثلاثون","S30").replace("الموسم الحادي و الثلاثون","S31").replace("الموسم الثاني والثلاثون","S32").replace("الموسم الاول","S1").replace(" الثانى","2").replace("الموسم الثاني","S2").replace("الموسم الثالث","S3").replace("الموسم الثالث","S3").replace("الموسم الرابع","S4").replace("الموسم الخامس","S5").replace("الموسم السادس","S6").replace("الموسم السابع","S7").replace("الموسم الثامن","S8").replace("الموسم التاسع","S9").split('الموسم')[0].split('الحلقة')[0].strip()
            
            siteUrl = URL_MAIN+aEntry[0].replace("/film/","/watch/").replace("/episode/","/watch/")
            sThumb = ''
            sDesc = ''
            sYear = ''

            if sDisplayTitle not in itemList:
                itemList.append(sDisplayTitle)
                oOutputParameterHandler.addParameter('siteUrl',siteUrl)
                oOutputParameterHandler.addParameter('sMovieTitle', sDisplayTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)
                oOutputParameterHandler.addParameter('sYear', sYear)
                oOutputParameterHandler.addParameter('sDesc', sDesc)

                oGui.addTV(SITE_IDENTIFIER, 'showSeasons', sDisplayTitle, '', sThumb, sDesc, oOutputParameterHandler)

 
        
 
    if not sSearch:
        sNextPage = __checkForNextPage(sHtmlContent)
        if sNextPage:
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addDir(SITE_IDENTIFIER, 'showSeries', '[COLOR teal]Next >>>[/COLOR]', icons + '/Next.png', oOutputParameterHandler)
        oGui.setEndOfDirectory()  
def showSeasons():
    oGui = cGui()
   
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')



    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    oParser = cParser()
    sSeason = ''
    
    #Recuperation infos

    sPattern = '<h1 class="section-title">(.+?)</h1>'
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if (aResult[0]):
        sSeason = aResult[1][0].replace("مشاهدة","").replace("مترجمة","").replace("مسلسل","").replace("انمي","").replace("كاملة","").replace("برنامج","").replace("كامل","").replace("مترجم","").replace("الموسم العاشر","S10").replace("الموسم الحادي عشر","S11").replace("الموسم الثاني عشر","S12").replace("الموسم الثالث عشر","S13").replace("الموسم الرابع عشر","S14").replace("الموسم الخامس عشر","S15").replace("الموسم السادس عشر","S16").replace("الموسم السابع عشر","S17").replace("الموسم الثامن عشر","S18").replace("الموسم التاسع عشر","S19").replace("الموسم العشرون","S20").replace("الموسم الحادي و العشرون","S21").replace("الموسم الثاني و العشرون","S22").replace("الموسم الثالث و العشرون","S23").replace("الموسم الرابع والعشرون","S24").replace("الموسم الخامس و العشرون","S25").replace("الموسم السادس والعشرون","S26").replace("الموسم السابع والعشرون","S27").replace("الموسم الثامن والعشرون","S28").replace("الموسم التاسع والعشرون","S29").replace("الموسم الثلاثون","S30").replace("الموسم الحادي و الثلاثون","S31").replace("الموسم الثاني والثلاثون","S32").replace("الموسم الاول","S1").replace("الموسم الأول","S1").replace("الموسم الثاني","S2").replace("الموسم الثالث","S3").replace("الموسم الثالث","S3").replace("الموسم الرابع","S4").replace("الموسم الخامس","S5").replace("الموسم السادس","S6").replace("الموسم السابع","S7").replace("الموسم الثامن","S8").replace("الموسم التاسع","S9").replace("الموسم","S").replace("S ","S")

    #print sHtmlContent
   
    oParser = cParser()
     # (.+?) ([^<]+) .+?
    sPattern = '<h2 class="entry-title">([^<]+)</h2.+?src="([^<]+)" class=.+?<a href="([^<]+)" class="lnk-blk">'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
	
    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()    
        for aEntry in aResult[1]:
 


            sTitle = aEntry[0].replace("مشاهدة","").replace("مسلسل","").replace("انمي","").replace("مترجمة","").replace("مترجم","").replace("برنامج","").replace("فيلم","").replace("الموسم العاشر","S10").replace("الموسم الحادي عشر","S11").replace("الموسم الثاني عشر","S12").replace("الموسم الثالث عشر","S13").replace("الموسم الرابع عشر","S14").replace("الموسم الخامس عشر","S15").replace("الموسم السادس عشر","S16").replace("الموسم السابع عشر","S17").replace("الموسم الثامن عشر","S18").replace("الموسم التاسع عشر","S19").replace("الموسم العشرون","S20").replace("الموسم الحادي و العشرون","S21").replace("الموسم الثاني و العشرون","S22").replace("الموسم الثالث و العشرون","S23").replace("الموسم الرابع والعشرون","S24").replace("الموسم الخامس و العشرون","S25").replace("الموسم السادس والعشرون","S26").replace("الموسم السابع والعشرون","S27").replace("الموسم الثامن والعشرون","S28").replace("الموسم التاسع والعشرون","S29").replace("الموسم الثلاثون","S30").replace("الموسم الحادي و الثلاثون","S31").replace("الموسم الثاني والثلاثون","S32").replace("الموسم الاول","S1").replace("الموسم الأول","S1").replace("الموسم الثاني","S2").replace("الموسم الثالث","S3").replace("الموسم الثالث","S3").replace("الموسم الرابع","S4").replace("الموسم الخامس","S5").replace("الموسم السادس","S6").replace("الموسم السابع","S7").replace("الموسم الثامن","S8").replace("الموسم التاسع","S9").replace("الموسم","S").replace("S ","S")
            siteUrl = URL_MAIN+aEntry[2]
            sThumb = URL_MAIN+aEntry[1]
            sDesc = ""
            sYear = ""
            if '/episode/' in aEntry[2]:
                sTitle = sSeason+' E'+aEntry[2].split('/episode/')[1]

            oOutputParameterHandler.addParameter('siteUrl',siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oOutputParameterHandler.addParameter('sYear', sYear)
            oOutputParameterHandler.addParameter('sDesc', sDesc)
            if '/episode/'  in aEntry[2] :
                oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler) 
            else: 
	            oGui.addSeason(SITE_IDENTIFIER, 'showEps', sTitle, '', sThumb, sDesc, oOutputParameterHandler)
       
       
    oGui.setEndOfDirectory() 
def showEps():
    import requests
    oGui = cGui()
   
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')



    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    #print sHtmlContent
   
    oParser = cParser()
     # (.+?) ([^<]+) .+?
    sPattern = '<h2 class="entry-title">([^<]+)</h2.+?src="([^<]+)" class=.+?<a href="([^<]+)" class="lnk-blk">'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
	
    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()    
        for aEntry in aResult[1]:
 

            sTitle = sMovieTitle
            siteUrl = URL_MAIN+aEntry[2]
            sThumb = URL_MAIN+aEntry[1]
            sDesc = ""
            if '/episode/' in aEntry[2]:
                sTitle = sMovieTitle+'E'+aEntry[2].split('/episode/')[1]
			


            oOutputParameterHandler.addParameter('siteUrl',siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGui.addEpisode(SITE_IDENTIFIER, 'showHosters', sTitle, sThumb, sThumb, sDesc, oOutputParameterHandler)
               
       
    oGui.setEndOfDirectory() 
 
def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    if '?watch=1' not in sUrl:
        sUrl = sUrl + '?watch=1'

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = r'data-watch="([^"]+)"[^>]*>.*?<span id="serverName">([^<]+)</span>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            sHosterUrl = aEntry[0]
            sServerName = aEntry[1]
            if sHosterUrl.startswith('//'):
                sHosterUrl = 'https:' + sHosterUrl

            oHoster = None

            try:
                import resolveurl
                hmf = resolveurl.HostedMediaFile(url=sHosterUrl)
                if hmf.valid_url():
                    oHoster = cHosterGui().getHoster('resolver')
                    RH = sHosterUrl.split('/')[2].replace('www.', '').split('.')[0].upper()
                    oHoster.setRealHost(RH)
            except Exception:
                pass

            if not oHoster:
                oHoster = cHosterGui().checkHoster(sHosterUrl)

            if oHoster:
                sTitle = '%s [COLOR coral](%s)[/COLOR]' % (sMovieTitle, sServerName)
                oHoster.setDisplayName(sTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl + "|verifypeer=false&Referer=" + URL_MAIN + "/", sThumb)

    oGui.setEndOfDirectory() 
			
def showServer():
    oGui = cGui()
   
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    if '?watch=1' not in sUrl:
        sUrl = sUrl + '?watch=1'

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = r'data-watch="([^"]+)"[^>]*>.*?<span id="serverName">([^<]+)</span>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            sHosterUrl = aEntry[0]
            sServerName = aEntry[1]
            if sHosterUrl.startswith('//'):
                sHosterUrl = 'https:' + sHosterUrl

            oHoster = None

            try:
                import resolveurl
                hmf = resolveurl.HostedMediaFile(url=sHosterUrl)
                if hmf.valid_url():
                    oHoster = cHosterGui().getHoster('resolver')
                    RH = sHosterUrl.split('/')[2].replace('www.', '').split('.')[0].upper()
                    oHoster.setRealHost(RH)
            except Exception:
                pass

            if not oHoster:
                oHoster = cHosterGui().checkHoster(sHosterUrl)

            if oHoster:
                sTitle = '%s [COLOR coral](%s)[/COLOR]' % (sMovieTitle, sServerName)
                oHoster.setDisplayName(sTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl + "|verifypeer=false&Referer=" + URL_MAIN + "/", sThumb)

       
    oGui.setEndOfDirectory()  
def showServers():
    oGui = cGui()
   
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')
 
    oRequestHandler = cRequestHandler(sUrl + '?watch=1')
    sHtmlContent = oRequestHandler.request()

    sPattern = r'data-watch="([^"]+)"[^>]*>.*?<span id="serverName">([^<]+)</span>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if aResult[0]:
        for aEntry in aResult[1]:
            sHosterUrl = aEntry[0]
            sServerName = aEntry[1]
            if sHosterUrl.startswith('//'):
                sHosterUrl = 'https:' + sHosterUrl

            oHoster = None

            try:
                import resolveurl
                hmf = resolveurl.HostedMediaFile(url=sHosterUrl)
                if hmf.valid_url():
                    oHoster = cHosterGui().getHoster('resolver')
                    RH = sHosterUrl.split('/')[2].replace('www.', '').split('.')[0].upper()
                    oHoster.setRealHost(RH)
            except Exception:
                pass

            if not oHoster:
                oHoster = cHosterGui().checkHoster(sHosterUrl)

            if oHoster:
                sTitle = '%s [COLOR coral](%s)[/COLOR]' % (sMovieTitle, sServerName)
                oHoster.setDisplayName(sTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl + "|verifypeer=false&Referer=" + URL_MAIN + "/", sThumb)
       	
    sPattern = 'rel="nofollow" href="(.+?)" class'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

	
    if aResult[0]:
        for aEntry in aResult[1]:
            
            url = aEntry
            sTitle = sMovieTitle
            if url.startswith('//'):
               url = 'http:' + url
				
					
            
            sHosterUrl = url 
            if 'userload' in sHosterUrl:
                sHosterUrl = sHosterUrl + "|Referer=" + URL_MAIN
            if 'moshahda' in sHosterUrl:
                sHosterUrl = sHosterUrl + "|Referer=" + URL_MAIN
            if 'mystream' in sHosterUrl:
                sHosterUrl = sHosterUrl + "|Referer=" + URL_MAIN   
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if oHoster:
               sDisplayTitle = sTitle
               oHoster.setDisplayName(sDisplayTitle)
               oHoster.setFileName(sMovieTitle)
               cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)
	    #Affichage du menu  
    oGui.addText(SITE_IDENTIFIER,'[COLOR olive]----------------------------[/COLOR]')
 
     # (.+?) ([^<]+) .+?
    sPattern = '<li><a class="Hoverable" href="([^<]+)" title="([^<]+)"><em>(.+?)</em>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
	
	
    if aResult[0]:
        oOutputParameterHandler = cOutputParameterHandler()    
        for aEntry in aResult[1]:
 
            sTitle = aEntry[1].replace("مسلسل","").replace("مشاهده","").replace("الموسم العاشر","S10").replace("الموسم الحادي عشر","S11").replace("الموسم الثاني عشر","S12").replace("الموسم الثالث عشر","S13").replace("الموسم الرابع عشر","S14").replace("الموسم الخامس عشر","S15").replace("الموسم السادس عشر","S16").replace("الموسم السابع عشر","S17").replace("الموسم الثامن عشر","S18").replace("الموسم التاسع عشر","S19").replace("الموسم العشرون","S20").replace("الموسم الحادي و العشرون","S21").replace("الموسم الثاني و العشرون","S22").replace("الموسم الثالث و العشرون","S23").replace("الموسم الرابع والعشرون","S24").replace("الموسم الخامس و العشرون","S25").replace("الموسم السادس والعشرون","S26").replace("الموسم السابع والعشرون","S27").replace("الموسم الثامن والعشرون","S28").replace("الموسم التاسع والعشرون","S29").replace("الموسم الثلاثون","S30").replace("الموسم الحادي و الثلاثون","S31").replace("الموسم الثاني والثلاثون","S32").replace("الموسم الاول","S1").replace("الموسم الثاني","S2").replace("الموسم الثالث","S3").replace("الموسم الثالث","S3").replace("الموسم الرابع","S4").replace("الموسم الخامس","S5").replace("الموسم السادس","S6").replace("الموسم السابع","S7").replace("الموسم الثامن","S8").replace("الموسم التاسع","S9").replace("الموسم","S").replace("S ","S").split('الحلقة')[0]  
            if "E" not in sTitle:
                sTitle=sTitle+" E"+aEntry[2]
            siteUrl = aEntry[0].replace("/episode/","/watch/").replace("/post/","/watch/")
            sThumb = ""
            sDesc = ""


            oOutputParameterHandler.addParameter('siteUrl',siteUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
			
            oGui.addEpisode(SITE_IDENTIFIER, 'showServers', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

     
    oGui.setEndOfDirectory()	
 
# (.+?) .+? 
def __checkForNextPage(sHtmlContent):
    sPattern = '<a class="page-numbers" href="([^"]+)">'
	
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
 
    if aResult[0]:
        return aResult[1][0]

    return False