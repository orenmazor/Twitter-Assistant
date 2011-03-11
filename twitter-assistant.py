# Copyright (c) 2011, Oren Mazor 
# All rights reserved. 
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met: 
# 
#  * Redistributions of source code must retain the above copyright notice, 
#    this list of conditions and the following disclaimer. 
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution. 
#  * Neither the name of Oren Mazor nor the names of its contributors may be 
#    used to endorse or promote products derived from this software without 
#    specific prior written permission. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

#!/usr/bin/python
from _collections import defaultdict
from time import sleep
import tweepy
import json
import time

class Bot():
    """encapsulate all of the twitter wrangling in one class"""
    
    settings = None
    api = None
    
    keywords = defaultdict(dict)
    
    def __init__(self,user_settings = None):
        self.settings = user_settings
        
    def FollowUser(self,username,message = None):
        user = self.api.get_user(username)
        user.follow()
        
        if not message is None:
            self.MentionUser(username,message)
        
    def MentionUser(self,username,message = None):
        self.api.update_status("@"+username + " " + message)
        
    def HandleDirectMessage(self):
        pass
    
    def HandleMentionAtMe(self):
        pass
    
    def SendDirectMessage(self):
        pass
        
    def BackupAccount(self):
        account_backup = {}
        #todo: this wont work.
        account_backup["username"] = self.api.me
        account_backup["friends"] = self.api.friends
        account_backup["lists"] = self.api.lists
        
        backupfile = open(account_backup["username"] + "_" + str(time.time())+ "_backup.json","w")
        json.dump(account_backup,backupfile)
        
    def RestoreAccount(self, old_account):
        pass
        
    def AddAction(self,keyword=None,action=None,parameters=None):
        if action is None:
            raise Exception("doing nothing on no action seems redundant")
            
        if keyword is None:
            raise Exception("you want me to watch nothing?")
            
        self.keywords[keyword][action] = parameters
            
    def Run(self,frequency):
        print "starting run with a "+str(frequency) + " second pause in between"
        
        print "important keywords are: " + str(self.keywords.keys())
        
        for keyword in self.keywords.keys():
            results = self.api.search(keyword)
            
            for match in results:
                for action in self.keywords[keyword]:
                    action(match.from_user,self.keywords[keyword][action])
                    #pause for some random amount of time.
                    sleep(random.randint(1, 100))
        #sleep for whatever the frequency is
        print "sleeping for "+str(frequency) + " seconds"
        sleep(frequency)
        
    def Login(self):
        if self.settings["twitter_request_token"] is u"" or self.settings["twitter_request_secret"] is u"":
            print "need to get your key and secret. this will turn assistant_settings.json into a file that contains secure info. dont share it"
            auth = tweepy.OAuthHandler(self.settings["twitter_consumer_key"], self.settings["twitter_consumer_secret"])
        
            try:
                redirect_url = auth.get_authorization_url()
                print "go to this url, and give permission to this app to access your account."+ redirect_url
                print "you'll only need to do this once."
                verifier = raw_input("what's the code?:")
                auth.get_access_token(verifier)
                
                self.settings["twitter_request_token"] = auth.access_token.key
                self.settings["twitter_request_secret"] = auth.access_token.secret
                
                settings_file = open("assistant_settings.json","w")
                json.dump(self.settings,settings_file)
                settings_file.close()
                
            except tweepy.TweepError as e:
                return False,e.message
        else:    
            auth = tweepy.OAuthHandler(self.settings["twitter_consumer_key"], self.settings["twitter_consumer_secret"])
            auth.set_access_token(self.settings["twitter_request_token"], self.settings["twitter_request_secret"])
        self.api = tweepy.API(auth)
        return True,"no error"
        
        
def main():
    """configure the access to your twitter handle in the settings file that came with this. you'll need to create a new application (client, not browser), and grab the oauth data they give you"""
     
    settings_file = open("./assistant_settings.json","r")
    settings = json.load(settings_file)
    settings_file.close()
    
    bot = Bot(settings)
    
    success, error = bot.Login()
    
    if not success:
        raise Exception("config failed with error: " + error)
        
    #pick an action, either follow or mention and add them. order doesnt matter as its not guaranteed.
    #the third parameter is a dictionary. right now it's used to pass the message to the user. this
    #is only required in the case of MentionUser (i.e. what message do you want to send to the user?)
    #in the case of followuser, you can ignore message if you only want to follow the user, and not mention them
    bot.AddAction("winning",bot.FollowUser,None)
    bot.AddAction("#tigerblood",bot.MentionUser,'like tiger blood? try panda blood for more win!')
    bot.AddAction("#tigerblood",bot.FollowUser,None)
    
    #in seconds, how often do you want to run these checks?
    bot.Run(60)
    
if __name__ == '__main__':
    main()