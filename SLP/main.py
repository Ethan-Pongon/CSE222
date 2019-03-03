import collections
from imgurpython import ImgurClient
import tweepy
import json
import matplotlib
from tweepy import OAuthHandler
from wordcloud import WordCloud

consumer_key = '9UpeRwwdjaLbA7QFKhX8XhQgt'
consumer_secret = 'jT6vlKNJ3DCVnSqbeQu1qvKBHuAZvy8tadFRWMNrLqWQUNCB1v'
access_token = '1087124205198499840-nQmjQIWPJ4215eHkfFOUzwxLLRqe1U'
access_secret = 'MRChu5UgAmCTJLNZLUJgfRK3oomBlRDZ2NV1TsFTLI1Q3'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth) #twitter api

client = ImgurClient('1631ebda1e42fa1', 'ed3c068eca8ee531da305d9fb06d1ccca23e21b8') #imgur api


NUMBER_TWEETS = 50
hashtag = input()
tweet_counter = 0
words = collections.Counter()
filtered_words = {"a", "A", "I", "the", "The", "and", "that", "in", "on", "to", "but", "at", "an", "for", "of", "&amp", hashtag}

# this for loop gathers a number of tweets specified by 'NUMBER_TWEETS' and adds each one to a json file
for tweet in tweepy.Cursor(api.search, q=hashtag + '-filter:retweets', tweet_mode='extended').items(NUMBER_TWEETS):
    tweet_text = str(tweet.full_text)
    namingfile = "text" + str(tweet_counter) + ".json" #create a new json file to store text for every new tweet coming
    with open(namingfile, 'w') as outfile:
      json.dump(tweet_text, outfile)
    outfile.close()
    tweet_counter = tweet_counter + 1


tweet_counter = 0
while(tweet_counter < NUMBER_TWEETS):
    scanningfile = "text" + str(tweet_counter) + ".json"
    with open(scanningfile, 'r') as readfile:
        scanned_text = json.load(readfile)
    #print(scanned_text)
    #print("")
    scanningfile = scanned_text.split()
    full = map(lambda s: s.strip(' -').lower(), scanningfile)  # remove starting and ending whitespace and dashes from list of text in 'scanningfile'
    full = filter(lambda s: s and s not in filtered_words, scanningfile) #remove words that I've dictated to be filtered out by the list 'filtered_words'
    #print(collections.Counter(scanningfile))
    add = collections.Counter(full)
    words = words + add
    readfile.close()
    tweet_counter = tweet_counter + 1

wordcloud = WordCloud(width=800, height=600, relative_scaling=0.7).generate_from_frequencies(words)
wordcloud.to_file("wordcloud.png")

image_path = '/Users/Ethan/PycharmProjects/SLP Twitter Gun/wordcloud.png' # this gives the location of the generated file containing the word cloud to 'image_path'
image = client.upload_from_path(image_path) # this will upload the wordcloud anonymously to imgur
print(image['link'])

api.update_status('wordcloud generated for' + ' ' + hashtag + ' ' + image['link'] + ' ' + 'with 0.7 relative_scaling') # have the twitter account for this project tweet out a link to where the wordcloud is hosted on imgur
