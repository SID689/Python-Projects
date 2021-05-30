# Sprite classes for platform game
import pygame as pg
from JUMPsettings import *
from random import choice, randrange
vec = pg.math.Vector2


class Spritesheet:
    # utiility class for loading and parsing sprite sheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger sprite sheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        monkey = self.image
        pg.transform.scale(monkey, (100 // 2, 180 // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(720, 391, 87, 99),
                                self.game.spritesheet.get_image(938, 391, 63, 98)]
        for frame in self.standing_frames:
            frame.set_colorkey(black)
        self.walking_frames_r = [self.game.spritesheet.get_image(875, 391, 61, 99),
                                 self.game.spritesheet.get_image(457, 391, 63, 104),
                                 self.game.spritesheet.get_image(588, 391, 68, 101),
                                 self.game.spritesheet.get_image(391, 391, 64, 104)]
        self.walking_frames_l = []
        for frame in self.walking_frames_r:
            frame.set_colorkey(black)
            self.walking_frames_l.append(pg.transform.flip(frame, True, False))

        self.jumping_frames_r = [self.game.spritesheet.get_image(658, 391, 60, 101),
                                 self.game.spritesheet.get_image(809, 391, 64, 99),
                                 self.game.spritesheet.get_image(522, 391, 64, 102),
                                 self.game.spritesheet.get_image(1372, 1, 66, 95)]
        self.jumping_frames_l = []
        for frame in self.jumping_frames_r:
            frame.set_colorkey(black)
            self.jumping_frames_l.append(pg.transform.flip(frame, True, False))

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def jump(self):
        # jump only if standing on a platform
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.3:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        #show walk animation
        if self.walking:
            if now - self.last_update > 150:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walking_frames_r[self.current_frame]
                else:
                    self.image = self.walking_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # show idle animation
        if not self.jumping and not self.walking:
            if now - self.last_update > 500:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pg.mask.from_surface(self.image)


class Platform(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        platform_1 = self.game.spritesheet.get_image(391, 261, 128, 128)
        platform_1 = pg.transform.scale(platform_1, (128 // 2, 128 // 2))
        platform_2 = self.game.spritesheet.get_image(1069, 68, 253, 67)
        platform_2 = pg.transform.scale(platform_2, (253 // 2, 67 // 2))
        platform_3 = self.game.spritesheet.get_image(983, 1, 387, 65)
        platform_3 = pg.transform.scale(platform_3, (387 // 2, 65 // 2))
        platforms = [platform_1, platform_2, platform_3]
        self.image = choice(platforms)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < POW_SPAWN_RATE:
            Pow(self.game, self)


class Pow(pg.sprite.Sprite):

    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost'])
        self.image = self.game.spritesheet.get_image(333, 1, 128, 128)
        self.image = pg.transform.scale(self.image, (128 // 2, 128 // 2))
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top

    def update(self):
        self.rect.bottom = self.plat.rect.top
        if not self.game.platforms.has(self.plat):
            self.kill()


class Mob(pg.sprite.Sprite):

    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.eagle_1 = self.game.spritesheet.get_image(1166, 137, 128, 74)
        self.eagle_1 = pg.transform.scale(self.eagle_1, (128 // 6 * 5, 74 // 6 * 5))
        self.eagle_1.set_colorkey(black)
        self.eagle_2 = self.game.spritesheet.get_image(1041, 137, 123, 76)
        self.eagle_2 = pg.transform.scale(self.eagle_2, (123 // 6 * 5, 76 // 6 * 5))
        self.eagle_2.set_colorkey(black)
        self.eagle_3 = self.game.spritesheet.get_image(1329, 424, 118, 67)
        self.eagle_3 = pg.transform.scale(self.eagle_3, (118 // 6 * 5, 67 // 6 * 5))
        self.eagle_3.set_colorkey(black)
        self.eagle_4 = self.game.spritesheet.get_image(1329, 358, 119, 64)
        self.eagle_4 = pg.transform.scale(self.eagle_4, (119 // 6 * 5, 64 // 6 * 5))
        self.eagle_4.set_colorkey(black)
        self.image = self.eagle_1
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.dx = 0
        self.vx = randrange(1, 4)
        if self.rect.centerx > WIDTH:
            self.vx *= -1
        self.rect.y = randrange(HEIGHT // 2)
        self.last_update = 0
        self.current_frame = 0
        self.eagle_fly_r = [self.eagle_1, self.eagle_2, self.eagle_3, self.eagle_4]
        self.eagle_fly_l = []
        for frame in self.eagle_fly_r:
            self.eagle_fly_l.append(pg.transform.flip(frame, True, False))

    def update(self):
        self.rect.x += self.vx
        center = self.rect.center
        now = pg.time.get_ticks()
        if now - self.last_update > 150:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.eagle_fly_l)
            if self.vx > 0:
                self.image = self.eagle_fly_r[self.current_frame]
            else:
                self.image = self.eagle_fly_l[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = center
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.kill()



































