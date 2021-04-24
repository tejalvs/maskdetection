import boto3

sns = None

def createSNS(topicName):
  global sns
  sns = boto3.client("sns", 
                     region_name="us-east-1")
  response = sns.create_topic(Name=topicName)
  topicArn = response["TopicArn"]
  return sns,topicArn

def listAllTopics():
  global sns
  response = sns.list_topics()
  topics = response["Topics"]
  print(topics)

def createAnEmailSubscription(topicArn):
  global sns
  response = sns.subscribe(TopicArn=topicArn, Protocol="email", Endpoint="ar4038@rit.edu")
  subscription_arn = response["SubscriptionArn"]

def listAllSubscriptions():
  global sns
  response = sns.list_subscriptions()
  subscriptions = response["Subscriptions"]
  print(subscriptions)

def getAllSubscriptionsByTopic(topicArn):
  global sns
  response = sns.list_subscriptions_by_topic(TopicArn=topicArn)
  subscriptions = response["Subscriptions"]
  print(subscriptions)

def publishMessage(topicArn):
  global sns
  sns.publish(TopicArn=topicArn, 
              Message="message text", 
              Subject="subject used in emails only")

topicArn = createSNS("topicTest")
listAllSubscriptions()
createAnEmailSubscription(topicArn)
getAllSubscriptionsByTopic(topicArn)
publishMessage(topicArn)
