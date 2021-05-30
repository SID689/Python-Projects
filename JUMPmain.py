# Jungle Jump ( a platform game)
# ART FROM INTERNET
#"Jungle Jumpin'" by Scott Elliott
# Sound effects from https://freesound.org/people/LloydEvans09/sounds/187024/, https://freesound.org/people/swordmaster767/sounds/397819/,https://freesound.org/people/qubodup/sounds/60013/
# Tausdei

import pygame as pg
import random
from JUMPsettings import *
from JUMPsprites import *
from os import path
import os

class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'Images')
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # load sprite sheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        #load sounds
        self.snd_dir = path.join(self.dir, 'Sound')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jump.wav'))
        self.speed_sound = pg.mixer.Sound(path.join(self.snd_dir, 'powerup.wav'))
        self.woosh_sound = pg.mixer.Sound(path.join(self.snd_dir, 'woosh.flac'))

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'Jungle.ogg'))
        self.run()
        pg.mixer.music.fadeout(500)

    def run(self):
        # Game Loop
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # spawn a mob
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        # hit a mob
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
        if mob_hits:
            self.playing = False
        # check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False

        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 15

        # if player hits powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.woosh_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
        # Die!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # spawn new platforms to keep same average number
        while len(self.platforms) < 7:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - width),
                    random.randrange(-75, -30))

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(green)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, black, WIDTH / 2, 15)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        pg.mixer.music.load(path.join(self.snd_dir, 'chill_jungle_ambient.ogg'))
        pg.mixer.music.play(loops=-1)
        self.jngbkgnd = pg.image.load("JNGBKGND.jpg").convert()
        self.screen.blit(self.jngbkgnd, (0, 0))
        self.draw_text(TITLE, 48, black, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move", 22, black, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, black, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("High Score: " + str(self.highscore), 22, black, WIDTH / 2, 15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        pg.mixer.music.load(path.join(self.snd_dir, 'chill_jungle_ambient.ogg'))
        pg.mixer.music.play(loops=-1)
        self.screen.blit(self.jngbkgnd, (0,0))
        self.draw_text("GAME OVER", 48, black, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, black, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, black, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, black, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, black, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()

