import re
import time
import numpy as np
import json
import cssutils
from constants import (W3_BASE_URL,
                       MBASIC_URL)
import logging

cssutils.log.setLevel(logging.CRITICAL)

CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

def delay():
    """delay for 5-15 seconds"""
    time.sleep(np.random.randint(5, 15))

def getLinks(soup, filter=None):
    """routine to extract all hyperlinks from the given soup element with filtering"""
    linkElements = soup.findAll("a")
    rawLinks = list()
    for i in range(len(linkElements)):
        try:
            link = linkElements[i]["href"]
            rawLinks.append(link)
        except:
            pass
    if filter is None:
        return rawLinks
    filteredLinks = list()
    for link in rawLinks:
        if link.startswith(filter):
            filteredLinks.append(link)
    return filteredLinks

def getMoreCommentsLink(soup, postID):
    """routine to extract the 'more comments' link in the page
    returns None if it doesn't exists"""
    element = soup.find("div", id=f"see_next_{postID.split(';')[1]}")
    nextLink = None
    if element is not None:
        nextLink = f"{MBASIC_URL}{element.a['href']}"
    return nextLink

def getMoreRepliesLink(soup, commentID):
    """routine to extract the 'more replies' link in the page
    return None if it doesn't exists"""
    element = soup.find("div", id=f"comment_replies_more_1:{commentID}")
    nextLink = None
    if element is not None:
        nextLink = f"{MBASIC_URL}{element.a['href']}"
    return nextLink

def getReplyClass(soup):
    """routine to find the div class for replies"""
    css = soup.find('style').text[32:-22]
    dct = parseCSS(css)
    candidates = list()
    for k, v in dct.items():
        if v == "padding: 4px":
            candidates.append(k)
    return candidates[-1][-2:]

def getReplyDivs(divs):
    """routine to filter elements corresponding to a reply"""
    filtered = list()
    for div in divs:
        if len(div.get("class")) == 1:
            filtered.append(div)
    return filtered

def parsePageScript(soup):
    """routine to parse content of <script> tag"""
    metadata = str(soup.find("script"))
    idx = 0
    while metadata[idx] != "{":
        idx += 1
    metadata = metadata[idx:-9]
    return json.loads(metadata)

def parsePostMetadata(metadata):
    """routine to parse the metadata of the post"""
    return dict(
        time=metadata["dateCreated"],
        text=metadata["articleBody"],
        url=metadata["url"],
        likeCount=metadata["interactionStatistic"][1]["userInteractionCount"],
        commentCount=metadata["commentCount"],
        sharCount=metadata["interactionStatistic"][2]["userInteractionCount"],
        author=metadata["author"],
        identifier=metadata["identifier"],
        comments=[]
    )

def parseCSS(css):
    """routine to convert a CSS script to a dictionary"""
    dct = {}
    sheet = cssutils.parseString(css)
    for rule in sheet:
        try:
            selector = rule.selectorText
            styles = rule.style.cssText
            dct[selector] = styles
        except:
            pass
    return dct

def parseReply(div):
    return dict(
        author=dict(
            name=re.sub(CLEANR, "", div.div.h3.text),
            url=f"{W3_BASE_URL}{div.div.h3.a['href']}"
        ),
        text=div.div.div.text
    )
