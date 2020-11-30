########################### LIBRARIES #########################################

from pymongo import MongoClient
import pandas as pd
import re
from textblob import TextBlob
import matplotlib.pyplot as plt

########################### Connect to DB #####################################

client = MongoClient("mongodb://localhost:27017")
db = client["dbFifa"] #database name
collection = db["tweets"] #collection name

########################### tweets cleaning ##############################

list_tweets = []
for data1 in  collection.aggregate([ { "$project" : { "_id" : 0 , "Orig_Tweet" : 1 } }, {"$limit" : 100 } ]):
    list_tweets.append(data1)

df1 = pd.DataFrame(list_tweets)
clean_tweets = df1['Orig_Tweet']
long = clean_tweets.size
for i in range(long):
    clean_tweets[i]= re.sub("(RT @[a-zA-Z0-9_:]+)|(@[a-zA-Z0-9_]+)|(http[a-zA-Z0-9./:]+)|([?]+)","",clean_tweets[i])
    
########################### Most used hashtages ##################

hashs = dict()
for data2 in clean_tweets:
    words = re.findall("#[a-zA-Z_]*",data2)
    for word in words:
        if word in hashs:
            hashs[word] += 1
        else:
            hashs[word] = 1
            
########################### Most used words #######################

coll_word = db["word_count"]
most_word_freq = []
for data3 in coll_word.aggregate([ 
							{ "$sort" : {"value":-1} },
                            { "$limit" : 15 } 
						  	]):
    most_word_freq.append(data3)

df2 = pd.DataFrame(most_word_freq)

########################### The worst and best tweets(based on likes) #######################

top_likes = []
for data3 in collection.aggregate([ 
                            { "$project" : { "_id" : 0 ,  "Likes" : 1 , "Tweet" : 1 , "Name" : 1 } },
							{ "$sort" : { "Likes" : -1 } },
                            { "$limit" : 100 } 
						  	]):
    top_likes.append(data3)
        
df3 = pd.DataFrame(top_likes)

less_likes = [] 
for data3 in collection.aggregate([ 
                            { "$project" : { "_id" : 0 ,  "Likes" : 1 , "Tweet" : 1 , "Name" : 1 } },
							{ "$sort" : { "Likes" : 1 } },
                            { "$limit" : 100 } 
						  	]):
    less_likes.append(data3)
        
df3 = pd.DataFrame(less_likes)


########################### Sentiment analysis with TextBlob lib ############################
pos,neg,neu = 0,0,0

for tweet in clean_tweets:
    tweet_analysis = TextBlob(tweet)
    tweet = re.sub("#[a-zA-Z0-9_]+","",tweet)
    print(tweet)
    if tweet_analysis.polarity > 0:
        print('positive')
        pos += 1
    elif tweet_analysis.polarity == 0:
        print('neutral')
        neu+= 1
    else:
        print('negative')
        neg += 1
    print("---------------")

########################### visualization ########################
    
#Show most used words with bars
df2.plot(kind='bar',x="_id" ,y="value")

#Display the sentiment analysis result with pie chart
labels = 'tweet Positive', 'tweet negative', 'tweet neutres'
val = [ pos , neg , neu]
explode = (0, 0, 0.1) 

fig1, ax1 = plt.subplots()
ax1.pie(val, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.show()
