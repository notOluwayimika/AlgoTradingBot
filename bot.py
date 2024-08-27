import praw
import config
from textblob import TextBlob

reddit = praw.Reddit(
    client_id=config.REDDIT_ID,
    client_secret=config.REDDIT_SECRET,
    password=config.REDDIT_PASS,
    user_agent="USERAGENT",
    username=config.REDDIT_USER,
)

sentimentList = []
neededSentiments = 300

def Average(lst):
    if len(lst)== 0:
        return len(lst)
    else:
        return sum(lst[-neededSentiments:]/neededSentiments)

for comment in reddit.subreddit("eurusd").stream.comments():
    print(comment.body)
    
    redditComment = comment.body
    blob = TextBlob(redditComment)
    
    # print(blob.sentiment)
    
    sent = blob.sentiment
    print(f"******** Sentiment is : {sent.polarity} ********")
    if sent.polarity != 0.0:
        sentimentList.append(sent)
    
        if round(Average(sentimentList) > 0.5 and len(sentimentList)>neededSentiments):
            print("Buy")
        elif round(Averafe(sentimentList)<0.5 and len(sentimentList)>neededSentiments):
            print("Sell")
            