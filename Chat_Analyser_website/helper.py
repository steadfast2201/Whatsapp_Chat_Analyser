from urlextract import URLExtract
import pandas as pd
from collections import Counter
import emoji
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


extractor = URLExtract()

def fetch_stats(selected_user,df):

    if selected_user !="OverAll":
        df = df[df['user']==selected_user]

    num_messages = df.shape[0]

    words=[]
    for i in df['message']:
        words.extend(i.split())

    media_message = df[df['message'] ==  '<Media omitted>\n'].shape[0]

    # fetch Number of links shared...

    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))    

    return num_messages,len(words),media_message,len(links)
    

def most_active_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'precent'})
    return x,df

    # Most Common Words
def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stopwords = f.read()

    if selected_user !="OverAll":
        df = df[df['user']==selected_user]
    
    temp = df[df['user']=='group_notification']
    temp = temp[temp['message']!='<media_omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stopwords:
                words.extend(message.split())

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_count(selected_user,df):
    if selected_user !="OverAll":
        df = df[df['user']==selected_user]

    emojis = []

    for message in df['message']:
        # Convert emojis to text
        message_with_emojis = emoji.demojize(message)

        # Use regular expressions to find emojis
        emoji_list = re.findall(r':\w+:', message_with_emojis)

        # Add found emojis to the list
        emojis.extend(emoji_list)

    # Convert emoji text back to emoji characters
    emojis_df = [emoji.emojize(emoji_text) for emoji_text in emojis]

    # Create a DataFrame with the emojis with count
    emojis_final = pd.DataFrame(Counter(emojis_df).most_common(len(Counter(emojis_df))))

    return emojis_final

def monthly_timeline(selected_user,df):
    if selected_user !="OverAll":
        df = df[df['user']==selected_user]

    timeline = df.groupby(['year','month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+"-"+str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

def daily_time(selected_user,df):
    if selected_user !="OverAll":
        df = df[df['user']==selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline


def Analysis_Conversation_trends(selected_user,df):
    if selected_user !="OverAll":
        df = df[df['user']==selected_user]

    vec = CountVectorizer()
    dtm = vec.fit_transform(df)
    
    # Apply LDA
    lda = LatentDirichletAllocation(n_components=5,random_state=42)
    lda.fit(dtm)

    from sklearn.feature_extraction.text import TfidfVectorizer

    # Create a TF-IDF matrix
    tfidf_vectorizer = TfidfVectorizer(max_df=0.85, max_features=50)
    tfidf_matrix = tfidf_vectorizer.fit_transform(df)

    # Extract top keywords
    top_keywords = tfidf_vectorizer.get_feature_names_out()

    return top_keywords
