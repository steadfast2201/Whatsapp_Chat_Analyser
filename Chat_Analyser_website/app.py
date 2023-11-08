import pandas as pd
import re
import streamlit as st
import helper
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    
    # Ensure that 'messages' and 'dates' have the same length
    max_length = min(len(messages), len(dates))
    messages = messages[:max_length]
    dates = dates[:max_length]
    
    # Create the DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert 'message_date' type to datetime
    # Modify the date format to accommodate two-digit years
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()

    # Extract the 'hour' from the 'date' column
    df['hour'] = df['date'].dt.hour

    def create_period(hour):
        if hour == 23:
            return str(hour) + "-" + '00'
        elif hour == 0:
            return '00' + "-" + str(hour + 1)
        else:
            return str(hour) + "-" + str(hour + 1)

    # Check the column name to ensure it matches your DataFrame.
    if 'hour' in df.columns:
        df['period'] = df['hour'].apply(create_period)

    return df

st.sidebar.title("WhatsApp Chat Analyzer")

# File Upload
uploaded_file = st.file_uploader("Choose a WhatsApp chat text file", type=['txt'])

if uploaded_file is not None:
    # Read and preprocess the chat data
    data = uploaded_file.read().decode("utf-8")
    df = preprocess(data)


    # fetch unique user
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"OverAll")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if (st.sidebar.button("Show Analysis")):
        num_message, words, Media_message, links_number = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("<h3>Total Message</h3>", unsafe_allow_html=True)
            st.title(num_message)

        with col2:
            st.markdown("<h3>Total Words</h3>", unsafe_allow_html=True)
            st.title(words)  # Decrease font size (adjust the size as needed)

        with col3:
            st.markdown("<h3>Total Media</h3>", unsafe_allow_html=True)
            st.title(Media_message)  # Decrease font size (adjust the size as needed)

        with col4:
            st.markdown("<h3>Total Links</h3>", unsafe_allow_html=True)
            st.title(links_number)  # Decrease font size (adjust the size as needed)


        # Timeline
        st.title("Monthly_Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'],timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig) 

        # Daily Timeline
        st.title("Daily_Timeline")
        daily_timeline = helper.daily_time(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(daily_timeline['only_date'],daily_timeline['message'],color='red')
        plt.xticks(rotation='vertical')
        st.pyplot(fig) 

        # finding busiest user in the group (OverAll)
        if selected_user == 'OverAll':
            st.title("Most Busy Users")
            x,new_df = helper.most_active_users(df)
            fig,ax = plt.subplots()
            col1,col2 = st.columns(2)

            with col1:
                ax.bar(x.index,x.values,color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)


            most_common_df = helper.most_common_words(selected_user,df)

            fig,ax = plt.subplots()
            ax.barh(most_common_df[0],most_common_df[1])
            plt.xticks(rotation='vertical')
            st.title("Most Common Words")
            st.pyplot(fig)

        # emoji_Analysis
        emoji_df = helper.emoji_count(selected_user,df)
        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()
            ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f")
            st.pyplot(fig)

