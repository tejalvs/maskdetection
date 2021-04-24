import boto3

sns = boto3.client("sns", 
                   region_name="us-east-1")
response = sns.create_topic(Name="topic_name")
topic_arn = response["TopicArn"]

response = sns.list_topics()
topics = response["Topics"]

response = sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint="ar4038@rit.edu")
subscription_arn = response["SubscriptionArn"]

response = sns.list_subscriptions()
subscriptions = response["Subscriptions"]

response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
subscriptions = response["Subscriptions"]

sns.publish(TopicArn=topic_arn, 
            Message="message text", 
            Subject="subject used in emails only")
