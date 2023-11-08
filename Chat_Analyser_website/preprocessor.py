import pandas as pd
import re

def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    
    messages = re.split(pattern, data)[2:]

    dates = re.findall(pattern, data)
    
    # Find the minimum length between 'messages' and 'dates'
    max_length = min(len(messages), len(dates))

    # Trim both lists to the same length
    messages = messages[:max_length]
    dates = dates[:max_length]

    # Now, 'messages' and 'dates' have the same length, and you can proceed to create the DataFrame.

    # Check if 'messages' and 'dates' have the same length
    if len(messages) != len(dates):
        raise ValueError("messages and dates lists must have the same length")

    # Ensure that 'messages' and 'dates' have the same length
    max_length = min(len(messages), len(dates))
    messages = messages[:max_length]
    dates = dates[:max_length]

    # Create the DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert 'message_date' type to datetime
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
