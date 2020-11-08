import tkinter as tk #Importing moduels
import sys
from tkinter import * #for canvas
import winsound #for playing sound
import time #for time
from time import sleep


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master) #Setting variables
        self.lives = 3
        self.points = 0
        self.width = 900
        self.height = 600
        self.paddle_collisions = 0
        self.background = None
        self.logo = tk.PhotoImage(file='pic.png') #Defining the background picture
        self.canvas = tk.Canvas(self, bg='#ffffff', width=self.width, height=self.height) #Setting the main game canvas
        self.canvas.create_image(0, 0, image=self.logo, anchor='nw') #Laying the background image ontop
        self.canvas.pack()
        self.pack()


        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 420) #Defining where to start the paddle of from
        self.items[self.paddle.item] = self.paddle

        self.hud = None #Lives HUD
        self.hud2 = None #Points HUD
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-20)) #Settings the arrows to move the paddle canvas
        self.canvas.bind('<Right>', lambda _: self.paddle.move(20))

    def setup_game(self):
        winsound.PlaySound("playball.wav", winsound.SND_ASYNC)
        self.add_ball()
        self.update_lives_text() #Updating the points and lives scoreboard after every reset
        self.update_points_text()
        self.text = self.draw_text(450, 250, 'Press Space to start, Q to exit') #Displaying starting text
        self.canvas.bind('<space>', lambda _: self.start_game()) #Binding keys to actions
        self.canvas.bind('<q>', lambda _: sys.exit())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position() #Settings the paddle coordinates
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5 #Finding the middle of the paddle coord x axis
        self.ball = Ball(self.canvas, x, 405) #Defining where to place the ball at the start
        self.paddle.set_ball(self.ball) #Telling code to place the ball at the start

    def draw_text(self, x, y, text, size='40'): #setting the scoreboard text and font to use for both scoreboards
        font = ('Arial', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self): #Block of code to work the lives score board
        text = 'Lives: %s' % self.lives #Defining the  text
        if self.hud is None:
            self.hud = self.draw_text(375, 20, text, 15) #Defining where to place the text
        else:
            self.canvas.itemconfig(self.hud, text=text) #Referring back to the draw_text block

    def update_points_text(self): #Block of code to work the points score board
        text = 'Points: %s' % self.points #Defining the text
        if self.hud2 is None:
            self.hud2 = self.draw_text(475, 20, text, 15) #Defining where to place the text
        else:
            self.canvas.itemconfig(self.hud2, text=text) #Referring back to the draw_text block

    def start_game(self): #Starts the main game loop. Unbinds the binded keys so if they are
        self.canvas.unbind('<space>') #pressed during the game nothing happens
        self.canvas.unbind('<q>')
        self.canvas.delete(self.text) #Deleting the text off the canvas
        self.paddle.ball = None #setting variables
        self.game_loop() #Moving onto the main game loop block

    def game_loop(self):
        self.check_collisions()
        if self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            self.update_lives_text()
            winsound.PlaySound("aww.wav", winsound.SND_ASYNC) #To play the sound when you miss the ball
            if self.lives < 1:
                winsound.PlaySound("your_out.wav", winsound.SND_ASYNC) #To play the sound when youve lost
                self.ball.delete()
                self.paddle.delete()
                self.draw_text(450, 200, 'Game over') #Code to display the final text displaying your points
                self.draw_text(450, 300, 'You Scored: %s' % self.points)
                self.text = self.draw_text(450, 400, 'Press Q to Exit')  # Displaying ending text
                self.canvas.bind('<q>', lambda _: sys.exit())  # Binding keys to actions

            else:
                self.paddle_collisions = 0 #Setting the paddle collisions to 0
                self.after(1000, self.setup_game)
        else:
            self.ball.update() #Updating ball position
            self.after(50, self.game_loop) #Wait 50milliseconds then go to game_loop block

    def check_collisions(self):
        ball_coords = self.ball.get_position() #defining ball_coords with where the ball currently is on the game
        items = self.canvas.find_overlapping(*ball_coords) #Seeing if the ball overlaps with anything on the canvas...
        if len(items) > 2: #if the ball collides with more than 2 items then its a collision 1: background 2: image background 3: paddle !collision
            if self.paddle_collisions > 0:
                self.ball.direction[1] *= -1 #sets the ball in a different direction
                x = self.ball.direction[0] * self.ball.speed
                y = self.ball.direction[1] * self.ball.speed
                self.ball.move(x, y)
                winsound.PlaySound("hit.wav",winsound.SND_ASYNC) #plays the pathed sound whenever the code detects a collision
                self.points += 1 #adds a point on whenever the code detects a collision
                self.update_points_text() #updates the points text
            self.paddle_collisions += 1

class GameObject(object): #Simplyfying the self.() terms
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self): #Defining the commands for the game objects
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject): #Creating the Ball
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10 #Can increase or decrease speed of ball by changing this variable
        item = canvas.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, fill='#FFA500') #Create the ball on the canvas
        super(Ball, self).__init__(canvas, item)

    def update(self): #This section updates the balls movement if it hits a side or top
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

class Paddle(GameObject): #Creating the Paddle
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2, x + self.width / 2, y + self.height / 2, fill='#000000')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball): #Simplyfying the self.ball variable
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('BaseBall Bash by Louise Symons') #setting the title
    game = Game(root)
    game.mainloop() #calling the main loop
