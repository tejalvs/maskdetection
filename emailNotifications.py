import boto3

def createSNS(topicName):
  sns = boto3.client("sns", 
                     region_name="us-east-1")
  response = sns.create_topic(Name=topicName)
  topicArn = response["TopicArn"]
  return 

def listAllTopics():
  response = sns.list_topics()
  topics = response["Topics"]
  print(topics)

def createAnEmailSubscription():
  response = sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint="ar4038@rit.edu")
  subscription_arn = response["SubscriptionArn"]

def listAllSubscriptions():
  response = sns.list_subscriptions()
  subscriptions = response["Subscriptions"]
  print(subscriptions)

def getAllSubscriptionsByTopic(topicArn):
  response = sns.list_subscriptions_by_topic(TopicArn=topicArn)
  subscriptions = response["Subscriptions"]
  print(subscriptions)

def publishMessage(topicArn):
  sns.publish(TopicArn=topicArn, 
              Message="message text", 
              Subject="subject used in emails only")

topicArn = createSNS("topicTest")
listAllSubscriptions()
getAllSubscriptionsByTopic(topicArn)
publishMessage(topicArn)
