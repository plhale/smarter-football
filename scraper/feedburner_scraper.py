import newspaper
from newspaper import Article

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


def newspaper_parser(url):
    article = Article(url)

    return article

def feedburner_scraper(url_list):
    feed_articles = []
    for url in url_list:     
        row = {}
        post = newspaper_parser(url)
        post.download()
        post.parse()
        post.nlp()

        row['url'] = post.url
        row['date'] = post.publish_date
        row['title'] = post.title
        row['keywords'] = post.keywords
        row['text'] = post.text
        feed_articles.append(row)
    
    
    
    return feed_articles
    
def sbnation_scraper(url):
    newys = newspaper.build(url, memoize_articles=False)
    newsy_urls = []
    for article in newys.articles:
        if '2018' in article.url:
            newsy_urls.append(article.url)
    
    print("# of articles found: ", len(newsy_urls))
    
    news = feedburner_scraper(newsy_urls)
    print("# of articles: ", len(news))
    print("List keys: ",news[0].keys())
    print("List keywords", news[0]['keywords'])
    return news
    
# hawks = sbnation_scraper('https://www.fieldgulls.com')

"""
-------------------------------------------------------------------------------
# of articles found:  151
# of articles:  151
List keys:  dict_keys(['url', 'date', 'title', 'keywords', 'text'])
List keywords ['thing', 'mock', 'hit', 'midpreseason', 'followed', 'watch', 'seahawks', 'vs', 'draft', '3000', 'thats', 'rob', 'weeks', 'nfl', 'vikings', 'twitter']
-------------------------------------------------------------------------------
"""

# Get Transcripts from youtube videos
from youtube_transcript_api import YouTubeTranscriptApi
def youtube_scraper(url_string):
    urls = feedparser.parse(url_string)
    pat_urls = []
    for url in urls['entries']:
        x = url['links'][0]['href']
        pat_urls.append(x)
    
    
    newsy_urls = []
    for youtube_url in pat_urls:
        youtube = YouTubeTranscriptApi.get_transcript(youtube_url[32:])
        transcripts = []
        [transcripts.append(vid['text']) for vid in youtube if vid['text'] != '[Music]' and vid['text'] != '[Applause]']
        newsy_urls.append(transcripts)
    

    return newsy_urls

# nfl_youtube = youtube_scraper('https://www.youtube.com/feeds/videos.xml?user=NFL')


# Save to json
import json
def save_to_json(doc, label):
    doc = json.dumps(doc, indent=4, sort_keys=True, default=str)
    with open(label+'_news.json', 'w') as outfile:
        json.dump(doc, outfile)

#doc = {'hawks':hawks }

#[save_to_json(doc[y], y) for x,y in enumerate(doc)]
        
# Open json
import pandas as pd
import json
from pprint import pprint
def open_new_json(doc):
    with open(doc+'_news.json', encoding='utf-8') as f:
        dat = json.load(f)
    dat = json.loads(dat)
    df = pd.DataFrame(dat)
    df['team'] = doc
    
    return df


document =[
    'hawks',
    'patriots',
    'steelers',
    'cheese',
    'panthers',
    'cardinals',
    'cowboys'
]

def open_json():
    df = {}
    for doc in document:
        df[doc] = open_json(doc)
    nfl = pd.concat(df.values())
    
    nfl = nfl.drop_duplicates(subset='text').reset_index(drop=True)
    nfl['date'] = pd.to_datetime(nfl['date'], format="%Y%m%d %H:%M:%S").dt.date
    nfl['day'] =  pd.to_datetime(nfl['date']).dt.day
    
    return nfl
