import boto3
from dynamodb_json import json_util as json
from boto3.dynamodb.conditions import Attr

sns = None

topicName = "WegmansMailNotification"
subscribers = ["ar4038@rit.edu","ts8583@rit.edu"]

def createTopic(topicName):
  global sns
  response = sns.create_topic(Name=topicName)
  topicArn = response["TopicArn"]
  return topicArn

def listAllTopics():
  global sns
  response = sns.list_topics()
  topics = response["Topics"]
  return topics

def createAnEmailSubscription(topicArn,emailID):
  global sns
  response = sns.subscribe(TopicArn=topicArn, Protocol="email", Endpoint=emailID)
  subscription_arn = response["SubscriptionArn"]
  return subscription_arn

def getAllSubscriptionsByTopic(topicArn):
  global sns
  response = sns.list_subscriptions_by_topic(TopicArn=topicArn)
  subscriptions = response["Subscriptions"]
  return subscriptions

def publishMessage(topicArn,subject,message):
  global sns
  response = sns.publish(TopicArn=topicArn,Message=message,Subject=subject)
  print(response)

def checkIfTopicAndSubscriptionExists():
  global sns
  topicArn = ""
  sns = boto3.client("sns", region_name="us-east-1")
  topics = listAllTopics()
  for i in range(len(topics)):
    tArn = topics[i]["TopicArn"]
    topicNames = tArn.split(":")[5]
    if topicName == topicNames:
       topicArn = tArn
  if(topicArn == ""):
    topicArn = createTopic(topicName)
  subs = getAllSubscriptionsByTopic(topicArn)
  subscribersRequired = subscribers[:]
  for i in range(len(subs)):
    subEmail = subs[i]["Endpoint"]
    if subEmail in subscribersRequired:
      subscribersRequired.remove(subEmail)
  for i in range(len(subscribersRequired)):
    createAnEmailSubscription(topicArn,subscribersRequired[i])
  return topicArn

def fetchPeopleWithoutMaskDetails():
  dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
  table = dynamodb.Table('NotWornMask')
  response = table.scan(
    FilterExpression=Attr('time').gt(1619240254)
  )
  dynamodb_json = json.dumps(response['Items'])
  json.loads(dynamodb_json)
  return dynamodb_json


def publishAlertForUnsafeEnviornment(topicArn):
  subject = "This is a test to see if you are getting messages"
  message = "Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test Test"
  publishMessage(topicArn,subject,message)

if __name__ == '__main__':
  val = fetchPeopleWithoutMaskDetails()
  print(val)
  #   topicArn = checkIfTopicAndSubscriptionExists()
  #   publishAlertForUnsafeEnviornment(topicArn)
      
