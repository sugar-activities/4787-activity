#-------------------------------------------
# TestGame.py - basic code for an OLPC game
# mhoel - original code
# mhoel - April 8, 2016 - lewa image - http://www.didgigo.com
#-------------------------------------------

#!/usr/bin/python
import pygame
import sys
import random
import json
from gi.repository import Gtk

# class for covering rectangles
class MyRect:

    def __init__(self,x,y,w,h,color):

      self.xcoord = x
      self.ycoord = y
      self.width = w
      self.height = h
      self.color = color

# class for each question / guess round
class MyRound:

    def __init__(self,img,pts,hint,answer,rating):

      self.roundimg = img
      self.roundpts = int(pts)
      self.roundhint = hint
      self.roundanswer = answer
      self.rating = rating
      self.numtimes = 0

# class for each piece of text
class MyText:

    def __init__(self,name,font,text,color,pos):

      self.name = name
      self.font = font
      self.text = text
      self.color = color
      self.pos = pos

# main game class
class TestGame:

    # runs when class instantiates
    def __init__(self):

        # instance variable defaults
        self.x = 100
        self.y = 100
        self.score = 0

    # Called to save the state of the game to the Journal.
    def write_file(self, file_path):
        pass

    # Called to load the state of the game from the Journal.
    def read_file(self, file_path):
        pass

    # create text that doesn't change
    def createText(self,title,onlyRound):
        textList = []

        font = pygame.font.Font(None, 36) 
        color = (255,255,255)

        # must be index 0 and 1 - referenced later as such
        hint = MyText("hint",font,"Hint", (200,0,0),(210,70))
        hinttext = MyText("hinttext",font,"", (200,0,0),(650,750))

        guess = MyText("guess",font,"Guess",color,(1010,50))
        guesspts = MyText("guesspts",font,onlyRound.roundpts,color,(1010,75))
        scorepts = MyText("scorepts",font,"0",color,(1010,150))
        answer = MyText("answer",font,"",color,(375,750))
        score = MyText("score",font,"Score", color,(1010,125))
        rating = MyText("rating",font,"Rating", color,(100,50))
        ratingpts = MyText("ratingpts",font,onlyRound.rating, color,(100,75))
        typeit = MyText("typeit",font,"Type a guess:", color,(200,750))
        skip = MyText("skip",font,"Skip",color,(110,165))

        font = pygame.font.Font(None,100)
        title = MyText("title",font,title, color,(200,650))

        # add text to this list so it will draw
        textList = [hint,hinttext,guess,score,guesspts,scorepts,answer,rating,ratingpts,typeit,skip,title] 
        return textList

    # creates all the rectangles to cover the image
    def make_rects(self,screen):
        myrects = []
        xspot = 202 
        yspot = 52
        for i in range(10):
           for j in range(10):
              x = xspot
              y = yspot 
              w = 75
              h = 55
              color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
              r = MyRect(x,y,w,h,color)
              myrects.append(r)
              xspot = xspot + w + 5

           yspot = yspot + h + 5
           xspot = 202

        # make first rectangle black so we can write HINT on it
        myrects[0].color = (0,0,0)

        return myrects

    # read through game.json and create a list of all the rounds
    def makeRound(self,data):
        roundList = []
        for r in data['Game']['GameList']:
           round = MyRound(r['image'],r['points'],r['hint'],r['answer'],r['rating'])
           roundList.append(round)
        return roundList 
        
    # The main game loop.
    def run(self):
        self.running = True

        # get the surface to draw on
        screen = pygame.display.get_surface()

		  # create rectangles
        myrects = self.make_rects(screen)

        # skip button
        skip = MyRect(100,150,80,50,(0,150,0))

        # create all the rounds and set current guessing round data
        data = json.loads(open('game.json').read()) # read in game.json data
        title = data["Game"]["title"]
        roundList = self.makeRound(data)
        onlyRound = roundList[random.randint(0,len(roundList))-1]
        onlyRound.numtimes = 1 # set numtimes to 1 - only should appear 2x, otherwise boring game

        # create the sounds
        try:
            sound = pygame.mixer.Sound("sounds/click_x.wav")
            soundwin = pygame.mixer.Sound("sounds/chime.wav")
            soundloss = pygame.mixer.Sound("sounds/buzzer_x.wav")
        except pygame.error:
            print ('Cannot load sound')
            raise SystemExit

        # set all the static text
        mytext = ""
        roundpts = onlyRound.roundpts
        textList = self.createText(title,onlyRound) 

        # -------------------------------
        # this is the main game loop, all events dealt with here
        # -------------------------------
        while self.running:
            # Pump GTK messages.
            while Gtk.events_pending():
                Gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                   sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif (event.type == pygame.MOUSEBUTTONDOWN):
                    self.x = pygame.mouse.get_pos()[0]
                    self.y = pygame.mouse.get_pos()[1]

                    # collision detection for SKIP button, if clicked reset everything 
                    r = pygame.Rect(skip.xcoord,skip.ycoord,skip.width,skip.height)
                    if (r.collidepoint(self.x,self.y)):
                        onlyRound.numtimes = onlyRound.numtimes + 1 # keep track of number of times
                        onlyRound = roundList[random.randint(0,len(roundList)-1)]
                        roundpts = onlyRound.roundpts
                        textList[0].text = "Hint"
                        textList[1].text = ""
                        myrects = self.make_rects(screen)
                        break

                    # check for collisions and remove rects
                    for i in myrects:
                        r = pygame.Rect(i.xcoord,i.ycoord,i.width,i.height)
                        if (r.collidepoint(self.x,self.y)):
                             pts_to_remove = 1
                             if (i.xcoord == 202 and i.ycoord == 52):
                                textList[0].text = ""
                                pts_to_remove = int(roundpts / 2)
                             myrects.remove(i)
                             roundpts = roundpts - pts_to_remove
                             sound.play()
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: # legacy from inherited code
                        self.x -= 5
                    elif event.key == pygame.K_RIGHT: # legacy
                        self.x += 5
                    else:
                        if (event.key == pygame.K_BACKSPACE): # deal with backspaces
                           mytext = mytext[:-1]
                        elif (event.key == pygame.K_RETURN):  # check to see if entered guess is correct
                           if (mytext == onlyRound.roundanswer):
                              soundwin.play()
                              self.score = int(self.score) + roundpts
                              onlyRound.numtimes = onlyRound.numtimes + 1 # keep track of number of times
                              onlyRound = roundList[random.randint(0,len(roundList)-1)] # new current round
                              while onlyRound.numtimes > 2:
                                 onlyRound = roundList[random.randint(0,len(roundList)-1)]
                              roundpts = onlyRound.roundpts
                              textList[0].text = "Hint"
                              textList[1].text = ""
                              myrects = self.make_rects(screen)
                           else:
                              soundloss.play()
                              roundpts = roundpts - 5 
                           mytext = ""
                        else:
                           if (len(mytext) < 10): # all guesses have to be 10 characters or less
                              mytext = mytext + str(pygame.key.name(event.key)).lower()

            # Clear Display
            screen.fill((0, 0, 0))
            screen.blit(pygame.image.load("images/" + onlyRound.roundimg),(200,50))

            # draw the rectangles
            for i in myrects:
                pygame.draw.rect(screen,i.color,(i.xcoord,i.ycoord,i.width,i.height))

            # draw skip button
            pygame.draw.rect(screen,skip.color,(skip.xcoord,skip.ycoord,skip.width,skip.height))

            # draw the text
            for i in textList:
                if (i.name == "guesspts"): i.text = str(roundpts)
                if (i.name == "scorepts"): i.text = str(self.score)
                if (i.name == "answer"): i.text = mytext
                if (i.name == "ratingpts"): i.text = str(onlyRound.rating)
                if (i.name == "hinttext" and textList[0].text == ""): 
                   i.text = onlyRound.roundhint
               
                font = i.font
                text = font.render(i.text,1,i.color) 
                screen.blit(text,i.pos)

            # Flip Display
            pygame.display.update()


# This function is called when the game is run directly from the command line:
# ./TestGame.py
def main():
    pygame.init()
    pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    #pygame.display.set_mode((1200,900))
    game = TestGame()
    game.run()

if __name__ == '__main__':
    main()
