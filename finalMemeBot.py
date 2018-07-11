import time, datetime, argparse, sys
from pathlib import Path
from package.config import *

my_file = Path("log.txt")
if my_file.is_file():
    print('Log.txt was already found')
else:
    file = open('log.txt', 'w')
    print('Created log file')

def log(input):
    message = str(input) + ' ' + str(datetime.datetime.now().strftime('%m-%d %H:%M:%S'))
    print(message)

    with open('log.txt', 'a') as l:
        l.write(message + '\n')

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--used_bot', help='Pick the bot that you would like to use')
args = parser.parse_args()

if len(sys.argv) < 3:
    log('Need an argument for bot to use')
    exit()

if args.used_bot == 'MEB':
    bot = MEB
    log("I'm using " + MEBusername)
elif args.used_bot == 'S':
    bot = S
    log("I'm using " + Susername)
elif args.used_bot == 'STIB':
    bot = STIB
    log("I'm using " + STIBusername)
else:
    log('Incorrect arg')

version = 'v4.0'
ME = 'MemeEconomy'

def twilio_message(message):
    client.messages.create(
        to=my_cell,
        from_=my_twilio,
        body=message
    )

successfully_invested = []
subreddit = bot.subreddit(ME)
x = 0
while x < 5:
    investment_boolean = False
    global balance
    log('Running loop')
    # Finding Balance #
    for item in bot.inbox.comment_replies(limit=1):
        if item.author == "MemeInvestor_bot":
            comment_body = item.body
            message_breakdown = comment_body.split(" ")
            length_of_message = len(message_breakdown)
            def breakdown_message(location, message):
                global balance
                balance = int(message_breakdown[location])
                log(message + str(balance) + ' memecoins')
            # ! balance message #
            if length_of_message == 7:
                breakdown_message(5, 'Found a !balance inbox message. Says we have ')
            # ! initial investment message #
            elif length_of_message == 30:
                breakdown_message(13, 'Found the initial update message. Says we have ')
            # Good ! after investment message #
            elif length_of_message == 53:
                breakdown_message(-5, 'Good news. Found the updated message. Says we have ')
                twilio_message(comment_body)
            # Bad ! after investment message #
            elif length_of_message == 50:
                breakdown_message(-5, 'Bad news. Found the updated message. Says we have ')
                twilio_message(comment_body)
    log('Starting to look through the 50 newest posts')
    for submission in subreddit.new(limit=50):
        post_id = submission.id
        if post_id not in successfully_invested and investment_boolean == False:
            def invest(post_id):
                investment_submission = bot.submission(post_id)
                for comment in investment_submission.comments:
                    if comment.author == 'MemeInvestor_bot':
                        amount = round(balance*.75)
                        comment.reply('!invest ' + str(amount))
                        successfully_invested.append(post_id)
                        log('Successfully invested in "' + str(investment_submission.title) + '"')
                        global investment_boolean
                        investment_boolean = True

            upvotes_on_post = submission.ups
            comments = submission.comments.list()
            number_of_comments = len(comments)
            submission_title = submission.title

            submission_time = datetime.datetime.fromtimestamp(submission.created_utc)
            age = (datetime.datetime.now() - submission_time)
            time_boolean_twenty_five = age > datetime.timedelta(minutes=25)
            time_boolean_sixty = age < datetime.timedelta(minutes=60)

            log_investment_message = ('Added the "' + str(submission_title) + '" post to the investment queue. Data: \n' +
                    'Upvotes: ' + str(upvotes_on_post) + '\n' + 'Comments: ' + str(number_of_comments) + '\n' +
                    'Age: ' + str(age))

            if time_boolean_twenty_five == True and upvotes_on_post > 25:
                log(log_investment_message)
                invest(post_id)
            elif time_boolean_sixty == True and 180 > upvotes_on_post > 60:
                log(log_investment_message)
                invest(post_id)
            else:
                continue
    if investment_boolean == False:
        log('Could not find any posts to invest in\n Sleeping for 5 minutes.')
        time.sleep(300)
    else:
        # Sleep for 4 hours #
        log('Sleeping for 4 hours due to the investment\n\n')
        time.sleep(14440)
    x += 1