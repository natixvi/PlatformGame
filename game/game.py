import pygame, os, random, time
import game_module as gm

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

# Ustawienia ekranu i gry

screen = pygame.display.set_mode(gm.SIZESCREEN)
pygame.display.set_caption('Prosta gra platformowa...')

# Zarządzanie szybkością aktualizacji ekranu

clock = pygame.time.Clock()
font = pygame.font.Font("others/font1.ttf", 24)

# Dodanie muzyki do gry

pygame.mixer.music.load('sounds/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000) #-1 w nieskonczonosc gra muza
coin_fx = pygame.mixer.Sound('sounds/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sounds/jump.wav')
jump_fx.set_volume(0.5)
collision_fx = pygame.mixer.Sound('sounds/collision.wav')
jump_fx.set_volume(0.5)
bullet_fx = pygame.mixer.Sound('sounds/bullet.mp3')
bullet_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound('sounds/hit.mp3')
hit_fx.set_volume(0.5)
pick_item_fx = pygame.mixer.Sound('sounds/pick_item.wav')
pick_item_fx.set_volume(0.5)
complete_level_fx = pygame.mixer.Sound('sounds/complete_level.wav')
complete_level_fx.set_volume(0.5)

# Klasa gracza


class Player(pygame.sprite.Sprite):
    def __init__(self, file_image):
        super().__init__()
        self.image = file_image
        self.rect = self.image.get_rect()
        self.press_left = False
        self.press_right = False

        # Animacje atrybut notuje w ktora strone jest odworocony i jaka grafike wgrać

        self.rotate_left = False

        # Z jaka predkoscią

        self.movement_x = 0
        self.movement_y = 0

        # Pomozcnicza zmienna kiedy zmieniać grafikę

        self._count = 0
        self.level = None
        self.lifes = 3
        self.items = {}
        self.score = 0
        self.boom = False
        self.out_of_screen = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def turn_left(self):
        self.rotate_left = True
        self.movement_x = -6

    def turn_right(self):
        self.rotate_left = False
        self.movement_x = 6

    # Umiejetnosc zatrzymywania się

    def stop(self):
        self.movement_x = 0

    def jump(self):
        self.rect.y += 2
        colliding_platforms = pygame.sprite.spritecollide(self, player.level.set_of_platforms, False)
        self.rect.y -= 2

        if colliding_platforms:
            self.movement_y = -15
        jump_fx.play()

    def shoot(self):
        if self.items.get("shotgun", False):
            bullet = Bullet(gm.BULLET_LIST, self.rotate_left,
                            self.rect.centerx, self.rect.centery + 20)
            self.level.set_of_bullets.add(bullet)
            bullet_fx.play()

    def update(self):

        # Grawitacja

        self._gravitation()

        # ---------ruch w poziome --------------
        self.rect.x += self.movement_x

        # animacje

        if self.movement_x > 0:
            self._move(gm.PLAYER_WALK_LIST_R)
        if self.movement_x < 0:
            self._move(gm.PLAYER_WALK_LIST_L)

        # Kolizje z platformami

        colliding_platforms = pygame.sprite.spritecollide(self, player.level.set_of_platforms, False)

        for p in colliding_platforms:
            if self.movement_x > 0:
                self.rect.right = p.rect.left
            if self.movement_x < 0:
                self.rect.left = p.rect.right


        # ----- ruch w pionie ----------
        self.rect.y += self.movement_y

        # kolizje z platformami

        colliding_platforms = pygame.sprite.spritecollide(self, player.level.set_of_platforms, False)

        for p in colliding_platforms:
            if self.movement_y > 0: # w dol
                self.rect.bottom = p.rect.top  # dolna wsp ramki gracza byla styczna do gornej krawedzi ramki platformy
                if self.rotate_left and self.movement_x == 0:
                    self.image = gm.PLAYER_STAND_L
                if not self.rotate_left and self.movement_x == 0:
                    self.image = gm.PLAYER_STAND_R
            if self.movement_y < 0:
                self.rect.top = p.rect.bottom
            self.movement_y = 0

            if isinstance(p, MovingPlatform):
                self.rect.x += p.mov_x

        # animacja (zmiana grafiki przy skoku i spadaniu)

        self.rect.y += 2
        colliding_platforms = pygame.sprite.spritecollide(self, player.level.set_of_platforms, False)
        self.rect.y -= 2

        if not colliding_platforms:
            if self.movement_y > 0: # spadek
                if self.rotate_left:
                    self.image = gm.PLAYER_FALL_L
                else:
                    self.image = gm.PLAYER_FALL_R

            if self.movement_y < 0: # skok
                if self.rotate_left:
                    self.image = gm.PLAYER_JUMP_L
                else:
                    self.image = gm.PLAYER_JUMP_R

        # wykrywamy kolizje z przedmiotami

        colliding_items = pygame.sprite.spritecollide(self, player.level.set_of_items, False)
        for item in colliding_items:
            if item.name == 'life':
                pick_item_fx.play()
                self.lifes += 1
                item.kill()

            if item.name == 'shotgun':
                pick_item_fx.play()
                self.items[item.name] = 1
                item.kill()

            if item.name == 'coin':
                coin_fx.play()
                self.score += 1
                item.kill()


        # Wykrywamy kolizję z wrogami:

        colliding_enemies = pygame.sprite.spritecollide(player, player.level.set_of_enemies, True)
        if colliding_enemies:
            collision_fx.play()
            player.lifes -= 1
            player.boom = True

        # Sprawdzamy czy gracz nie spadł z planszy

        if self.rect.bottom > gm.HEIGHT:
            collision_fx.play()
            player.lifes -= 1
            player.boom = True
            player.out_of_screen = True


    # Metoda grawitacji - aby gracz spadał jak na niczym nie stoi

    def _gravitation(self):
        if self.movement_y == 0:
            self.movement_y = 2
        else:
            self.movement_y += 0.35

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.press_left = True
                self.turn_left()
            if event.key == pygame.K_RIGHT:
                self.press_right = True
                self.turn_right()
            if event.key == pygame.K_UP:
                self.jump()
            if event.key == pygame.K_SPACE:
                self.shoot()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                if self.press_right:
                    self.turn_right()
                else:
                    self.stop()
                    self.image = gm.PLAYER_STAND_L
                self.press_left = False

            if event.key == pygame.K_RIGHT:
                if self.press_left:
                    self.turn_left()
                else:
                    self.stop()
                    self.image = gm.PLAYER_STAND_R
            self.press_right = False

    def _move(self, image_list):
        if self._count < 3:
            self.image = image_list[0]
        elif self._count < 6:
            self.image = image_list[1]
        elif self._count < 9:
            self.image = image_list[2]
        elif self._count < 12:
            self.image = image_list[3]
        elif self._count < 15:
            self.image = image_list[4]
        elif self._count < 18:
            self.image = image_list[5]
        elif self._count < 21:
            self.image = image_list[6]

        if self._count < 21:
            self._count += 1
        else:
            self._count = 0


# Klasa platformy


class Platform(pygame.sprite.Sprite):
    def __init__(self, image_list, width, height, pos_x, pos_y):
        super().__init__()
        self.image_list = image_list
        self.width = width
        self.height = height
        self.image = pygame.Surface([self.width, self.height]) # obiekt prostokąta
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def draw(self, surface):
        """self.image.fill(gm.DARKGREEN)
        surface.blit(self.image, self.rect)"""
        if self.width == 70:
            surface.blit(self.image_list[0], self.rect)
        else:
            surface.blit(self.image_list[1], self.rect)
            for i in range(70, self.width - 70, 70):
                surface.blit(self.image_list[2], [self.rect.x + i, self.rect.y])

            surface.blit(self.image_list[3], [self.rect.x + self.width - 70, self.rect.y])


# Klasa poruszającej platformy


class MovingPlatform(Platform):
    def __init__(self, image_list, level, mov_x, mov_y, width, height, pos_x, pos_y, bound_left, bound_right, bound_top, bound_bottom):
        super().__init__(image_list, width, height, pos_x, pos_y)
        self.level = level
        self.mov_x = mov_x
        self.mov_y = mov_y
        self.bound_left = bound_left
        self.bound_right = bound_right
        self.bound_top = bound_top
        self.bound_bottom = bound_bottom

    def update(self):

        # Poruszanie w bok
        self.rect.x += self.mov_x

        # Sprawdzamy czy gracz nie udeżył w platformę , jeśli tak to przesuwamy gracza
        collide = pygame.sprite.collide_rect(self, self.level.player)
        if collide:
            if self.mov_x < 0:
                self.level.player.rect.right = self.rect.left
            else:
                self.level.player.rect.left = self.rect.right

        # Poruszanie w górę i dół
        self.rect.y += self.mov_y

        # Sprawdzamy czy gracz nie udeżył w platformę
        collide = pygame.sprite.collide_rect(self, self.level.player)
        if collide:
            if self.mov_y < 0:
                self.level.player.rect.bottom = self.rect.top
            else:
                self.level.player.rect.top = self.rect.bottom

        # Zmiana kierunku ruchu przy granicach
        if self.rect.bottom > self.bound_bottom or self.rect.top < self.bound_top:
            self.mov_y *= -1

        pos_x = self.rect.left - self.level.world_shift
        if pos_x < self.bound_left or pos_x + self.rect.width > self.bound_right:
            self.mov_x *= -1

# Klasa itemów playera


class Item(pygame.sprite.Sprite):
    def __init__(self, image, name, pos_center_x = 0, pos_center_y = 0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.name = name
        self.rect.center = [pos_center_x, pos_center_y]


# Klasa broni


class Bullet(pygame.sprite.Sprite):
    def __init__(self, image_list, rotate_left, pos_center_x, pos_center_y):
        super().__init__()
        self.image = image_list[0] if rotate_left else image_list[1] # jeżeli lewo id 0 w prawo id 1
        self.rect = self.image.get_rect()
        self.movement_x = -15 if rotate_left else 15
        self.rect.center = [pos_center_x, pos_center_y]

    def update(self):
        self.rect.x += self.movement_x

# Ogólna klasa wroga


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_start, image_list_left, image_list_right, image_list_dead_left, image_list_dead_right, movement_x = 0, movement_y = 0):
        super().__init__()
        self.image = image_start
        self.rect = self.image.get_rect()
        self.image_list_left = image_list_left
        self.image_list_right = image_list_right
        self.image_list_dead_left = image_list_dead_left
        self.image_list_dead_right = image_list_dead_right
        self.movement_x = movement_x
        self.movement_y = movement_y
        self.rotate_left = True
        self.count = 0
        self.lifes = 1

    def update(self):
        if not self.lifes and self.count > 7: #count - by bylo widac jak umiera a nie od razu znika
            self.kill()

        self.rect.x += self.movement_x

        if self.movement_x > 0 and self.rotate_left:
            self.rotate_left = False

        if self.movement_x < 0 and not self.rotate_left:
            self.rotate_left = True

        # Animacja - zmiana
        if self.lifes:
            if self.movement_x > 0:
                self._move(self.image_list_right)
            if self.movement_x < 0:
                self._move(self.image_list_left)
        else:
            self.movement_x = 0
            self.movement_y = 0
            if not self.rotate_left:
                self._move(self.image_list_dead_right)
            if self.rotate_left:
                self._move(self.image_list_dead_left)



    def _move(self, image_list):
        if self.count < 4:
            self.image = image_list[0]
        elif self.count < 8:
            self.image = image_list[1]

        if self.count < 8:
            self.count += 1
        else:
            self.count = 0 # aby zapetlic grafiki od poczatku

# Klasa 1 wroga


class PlatformEnemy(Enemy):
    def __init__(self, image_start, image_list_left, image_list_right,
                 image_list_dead_left, image_list_dead_right, platform, movement_x = 0, movement_y = 0):
        super().__init__(image_start, image_list_left, image_list_right,
                         image_list_dead_left, image_list_dead_right, movement_x, movement_y)

        self.platform = platform
        self.rect.bottom = self.platform.rect.top # dolna krawedz wroga ma sie pokrywac z gorna platformy
        self.rect.centerx = random.randint(self.platform.rect.left + self.rect.width//2,
                                           self.platform.rect.right - self.rect.width//2)

    def update(self):
        super().update()
        if self.rect.left < self.platform.rect.left or self.rect.right> self.platform.rect.right:
            self.movement_x *= -1


# # Klasa latającego wroga


class FlayingEnemy(Enemy):
    def __init__(self, image_start, image_list_left, image_list_right,
                 image_list_dead_left, image_list_dead_right, level, movement_x=0, movement_y=0, boundary_left = 0, boundary_right = 0, boundary_top = 0, boundary_bottom = 0):
        super().__init__(image_start, image_list_left, image_list_right,
                         image_list_dead_left, image_list_dead_right, movement_x, movement_y)
        self.boundary_left = boundary_left
        self.boundary_right = boundary_right
        self.boundary_top = boundary_top
        self.boundary_bottom = boundary_bottom
        self.sleep = True
        self.level = level # żeby okreslić granice jako stałe ale trzeba uwzględnić to w przesuwanie planszy

    def update(self):
        if self.sleep:
            if self.rect.left - self.level.player.rect.right < 300:
                self.sleep = False
        else:
            super().update()
            self.rect.y += self.movement_y
            pos_x = self.rect.left - self.level.world_shift
            if pos_x < self.boundary_left or pos_x + self.rect.width > self.boundary_right:
                self.movement_x *= -1
            if self.rect.top < self.boundary_top or self.rect.bottom > self.boundary_bottom:
                self.movement_y *= -1


# Ogólna klasa planszy - kolejne poziomy - rakcja miedzy plansza a obiektem gracza

class Level:
    def __init__(self, player):

        # Obiekty planszy

        self.set_of_platforms = pygame.sprite.Group()
        self.set_of_items = pygame.sprite.Group()
        self.set_of_bullets = pygame.sprite.Group()
        self.set_of_enemies = pygame.sprite.Group()
        self.world_shift = 0
        self.id_level = 0
        # Jak długi ma być poziom left/right:
        self.level_limit = -10000
        self.player = player

    # Metoda pobierająca z pliku najwiekszy zdobyty wynik

    def _get_high_score(self):
        high_score = 0
        # Try to read the high score from a file
        try:
            with open("high_score.txt", "r") as high_score_file:
                high_score = int(high_score_file.read())
        except IOError as ioe:
            print(ioe)
        return high_score

    #Metoda zapisująca do pliku nowy największy wynik

    def _save_high_score(self, new_high_score):
        # Try to write the file to disk
        try:
            with open("high_score.txt", "w") as high_score_file:
                high_score_file.write(str(new_high_score))
        except IOError as ioe:
            print(ioe)

    # Aktualizacja wszystkich obiektów

    def update(self):
        self._delete_bullet()
        self.set_of_bullets.update()
        self.set_of_enemies.update()
        self.set_of_platforms.update()
        self.set_of_items.update()

        # Jeśli gracz zbliży się do prawej strony, przesuń świat w lewo (-x)
        if self.player.rect.right >= 500:
            diff = self.player.rect.right - 500
            self.player.rect.right = 500
            self._shift_world(-diff)

        # Jeśli gracz znajdzie się w pobliżu lewej strony, przesuń świat w prawo (+x)
        if self.player.rect.left <= 150:
            diff = 150 - self.player.rect.left
            self.player.rect.left = 150
            self._shift_world(diff)

        # Sprawdzanie czy punkty gracza nie są większe od największego zdobytego wyniku do tej pory

        high_score = self._get_high_score()
        if self.player.score > high_score:
            self._save_high_score(self.player.score)

        # Sprawdzanie czy gracza żyje czy koniec gry
        if self.player.boom:
            if not self.player.out_of_screen:
                if self.player.lifes <= 0:
                    self.player.boom = False
                    while not pygame.key.get_pressed()[pygame.K_q]:
                        message_to_screen("GAME OVER, press q to exit", (255, 26, 26))
                        pygame.display.flip()
                        pygame.event.get()
                    exit(0)
                elif self.player.lifes > 0:
                    self.player.boom = False
                    message_to_screen("Boom you hit an enemy you lost a life!", (255, 26, 26))
                    pygame.display.flip()
                    time.sleep(1)
            else:
                if self.player.lifes <= 0:
                    self.player.boom = False
                    while not pygame.key.get_pressed()[pygame.K_q]:
                        message_to_screen("GAME OVER, press q to exit", (255, 26, 26))
                        pygame.display.flip()
                        pygame.event.get()
                    exit(1)
                elif self.player.lifes > 0:
                    self.player.boom = False
                    message_to_screen("Boom you lost a life!", (255, 26, 26))
                    pygame.display.flip()
                    if self.player.rotate_left:
                        self.player.rect.y = 0
                        self.player.rect.x += 400
                        time.sleep(1)
                    else:
                        self.player.rect.y = 0
                        self.player.rect.x -= 400
                        time.sleep(1)


    # Metoda rysująca wszytskie obiekty

    def draw(self, surface):

        # Rysowanie platform

        for p in self.set_of_platforms:
            p.draw(surface)

        # Rysowanie przedmiotów, pocisków, wrogów

        self.set_of_items.draw(surface)
        self.set_of_bullets.draw(surface)
        self.set_of_enemies.draw(surface)

        # Rysowanie poziomu levelu

        text_points = font.render("Level: " + str(self.id_level), True, (255, 26, 26))
        text_points_XY = text_points.get_rect()
        text_points_XY.x = 15
        text_points_XY.y = gm.HEIGHT - 30
        surface.blit(text_points, text_points_XY)

        # Rysowanie punktów ile zdobył gracz

        text_points = font.render("High Score: " + str(self._get_high_score()), True, (255, 26, 26))
        text_points_XY = text_points.get_rect()
        text_points_XY.x = 15
        text_points_XY.y = 15
        surface.blit(text_points, text_points_XY)

        text_points = font.render("Your Score: " + str(player.score), True, (255, 26, 26))
        text_points_XY = text_points.get_rect()
        text_points_XY.x = 15
        text_points_XY.y = 50
        surface.blit(text_points, text_points_XY)

        # Rysowanie żyć - gracza ile ma

        for i in range(self.player.lifes - 1):
            surface.blit(gm.HEART, [20 + 40 * i, 100])


    # Przesuwanie planszy

    def _shift_world(self, shift_x):
        self.world_shift += shift_x

        for p in self.set_of_platforms:
            p.rect.x += shift_x

        for item in self.set_of_items:
            item.rect.x += shift_x

        for bullet in self.set_of_bullets:
            bullet.rect.x += shift_x

        for pe in self.set_of_enemies:
            pe.rect.x += shift_x

    # Metoda usuwania pocisków

    def _delete_bullet(self):
        pygame.sprite.groupcollide(self.set_of_bullets, self.set_of_platforms, True, False)

        for b in self.set_of_bullets:
            if b.rect.left > gm.WIDTH or b.rect.right < 0:
                b.kill()

            colliding_enemies = pygame.sprite.spritecollide(b, self.set_of_enemies, False)
            for enemy in colliding_enemies:
                hit_fx.play()
                b.kill()
                if enemy.lifes:
                    enemy.lifes -= 1
                    if enemy.lifes == 0:
                        enemy.count = 0


# Klasa nr 1


class Level_1(Level):
    def __init__(self, player = None):
        super().__init__(player)
        self.level_limit = -1500
        self._create_platforms()
        self._create_items()
        self._create_platform_enemies()
        self._create_bat_enemies()
        self._create_coin_platform()
        self.id_level = 1

    # Metoda tworzenia fizycznych platform

    def _create_platforms(self):
        ws_static_platforms = [[70, 70, 100, 350],[gm.WIDTH *70, 70, -150, gm.HEIGHT - 70],[6*70, 70, 800, 350],
                              ]
        for ws in ws_static_platforms:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)

    # Metoda tworzenia coin na podstawie platformy

    def _create_ws_coins(self, platform):
        for i in range(0, platform.width, 70):
            ws = [platform.rect.x + 35 + i, platform.rect.y - 50]
            coin = Item(gm.COIN, 'coin', *ws)
            self.set_of_items.add(coin)

    # Metoda tworzenia platformy pod coin

    def _create_coin_platform(self):
        ws_static_platforms = [[70, 70, 100, 350]]
        for ws in ws_static_platforms:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)
            self._create_ws_coins(p)

    # Metoda tworzenia platformy z wrogiem

    def _create_platform_enemies(self):
        ws_static_platforms_with_enemy = [[10*70, 70, 1500, 350], [6*70, 70, 2500, 350]]
        for ws in ws_static_platforms_with_enemy:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)
            pe = PlatformEnemy(gm.ZOMBIE_STAND_L, gm.ZOMBIE_WALK_LIST_L, gm.ZOMBIE_WALK_LIST_R,
                               gm.ZOMBIE_DEAD_LIST_L, gm.ZOMBIE_DEAD_LIST_R, p,
                               random.choice([-4, -3, -2, 2, 3, 4]))
            self.set_of_enemies.add(pe)

    # Metoda tworzenia rzeczy

    def _create_items(self):
        ws_life = [[1000, 300]]
        for ws in ws_life:
            life = Item(gm.HEART, 'life', *ws)
            self.set_of_items.add(life)

        ws_shotgun = [[1400, 620]]
        for ws in ws_shotgun:
            shotgun = Item(gm.SHOTGUN, 'shotgun', *ws)
            self.set_of_items.add(shotgun)

    # Metoda tworzenia latających wrogów

    def _create_bat_enemies(self):
        ws_bound_bat_enemies = [[1200, 2400, 0, 300]]

        for id, ws in enumerate(ws_bound_bat_enemies):
            bat = FlayingEnemy(gm.BAT_HANG, gm.BAT_FLY_LIST_L, gm.BAT_FLY_LIST_R, gm.BAT_DEAD_LIST_L,
                           gm.BAT_DEAD_LIST_R, self, random.choice([-5,-4,-3,-2,2,3,4,5]),
                           random.choice([-4, -3, -2, 2, 3, 4]), *ws)

            bat.rect.left = ws_bound_bat_enemies[id][0] + 300
            bat.rect.top = ws_bound_bat_enemies[id][2]
            self.set_of_enemies.add(bat)
            

# Klasa planszy nr 2


class Level_2(Level):
    def __init__(self, player = None):
        super().__init__(player)
        self.level_limit = -3035
        self._create_platforms()
        self._create_moving_x_platforms()
        self._create_moving_y_platforms()
        self._create_items()
        self._create_platform_enemies()
        self._create_bat_enemies()
        self._create_coin_platform()
        self._create_moving_coin_platform()
        self.id_level = 2
        
    # Metoda tworzenia fizycznych platform

    def _create_platforms(self):
        ws_static_platforms = [[15 * 70, 70, -150, gm.HEIGHT - 70]]
        for ws in ws_static_platforms:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)

    # Metoda tworzenia coin na podstawie platformy

    def _create_ws_coins(self, platform):
        for i in range(0, platform.width, 70):
            ws = [platform.rect.x + 35 + i, platform.rect.y - 50]
            coin = Item(gm.COIN, 'coin', *ws)
            self.set_of_items.add(coin)

    # Metoda tworzenia ruchomej platformy

    def _create_moving_x_platforms(self):
        ws_moving_platforms = [[6*70, 40, 900, gm.HEIGHT - 140, 900, 2000, 0, 0]]
        for ws in ws_moving_platforms:
            p = MovingPlatform(gm.METAL_LIST, self, random.choice([-5,-4,-3,-2,2,3,4,5]),0, *ws)
            self.set_of_platforms.add(p)

    def _create_moving_y_platforms(self):
        ws_moving_platforms = [[3 * 70, 40, 2700, 270, 0, 0, 200, gm.HEIGHT - 70]]
        for ws in ws_moving_platforms:
            p = MovingPlatform(gm.METAL_LIST, self, 0, random.choice([-5,-4,-3,-2,2,3,4,5]), *ws)
            self.set_of_platforms.add(p)

    # Metoda tworzenia platformy pod coin

    def _create_coin_platform(self):
        ws_static_platforms = [[70, 70, 100, 350], [16*70, 70, 2950, 200]]
        for ws in ws_static_platforms:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)
            self._create_ws_coins(p)

    # Metoda tworzenia ruchomej platformy pod coin

    def _create_moving_coin_platform(self):
        ws_moving_platforms = [[3*70, 40, 350, 250, 350, 1000, 0 , 0], [6*70, 40, 1000, 110, 980, 1600, 0, 0]]
        for ws in ws_moving_platforms:
            p = MovingPlatform(gm.METAL_LIST, self, random.choice([-5, -4, -3, -2, 2, 3, 4, 5]),0, *ws)
            self.set_of_platforms.add(p)
            self._create_ws_coins(p)

    # Metoda tworzenia platformy z wrogiem

    def _create_platform_enemies(self):
        ws_static_platforms_with_enemy = [[10 * 70, 70, 1500, 350], [10*70, 70, 2000 ,gm.HEIGHT - 70]]
        for ws in ws_static_platforms_with_enemy:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)
            pe = PlatformEnemy(gm.ZOMBIE_STAND_L, gm.ZOMBIE_WALK_LIST_L, gm.ZOMBIE_WALK_LIST_R,
                               gm.ZOMBIE_DEAD_LIST_L, gm.ZOMBIE_DEAD_LIST_R, p,
                               random.choice([-4, -3, -2, 2, 3, 4]))
            self.set_of_enemies.add(pe)

    # Metoda tworzenia rzeczy

    def _create_items(self):
        ws_life = [[1000, 300]]
        for ws in ws_life:
            life = Item(gm.HEART, 'life', *ws)
            self.set_of_items.add(life)

        ws_shotgun = [[1400, 550]]
        for ws in ws_shotgun:
            shotgun = Item(gm.SHOTGUN, 'shotgun', *ws)
            self.set_of_items.add(shotgun)

    # Metoda tworzenia latających wrogów

    def _create_bat_enemies(self):
        ws_bound_bat_enemies = [[1200, 2400, 0, 300]]
        for id, ws in enumerate(ws_bound_bat_enemies):
            bat = FlayingEnemy(gm.BAT_HANG, gm.BAT_FLY_LIST_L, gm.BAT_FLY_LIST_R, gm.BAT_DEAD_LIST_L,
                           gm.BAT_DEAD_LIST_R, self, random.choice([-5,-4,-3,-2,2,3,4,5]),
                           random.choice([-4, -3, -2, 2, 3, 4]), *ws)

            bat.rect.left = ws_bound_bat_enemies[id][0] + 300
            bat.rect.top = ws_bound_bat_enemies[id][2]
            self.set_of_enemies.add(bat)


def message_to_screen(msg, color):
    font2 = pygame.font.Font("font1.ttf", 35)
    screen_text = font2.render(msg, True, color)
    text_rect = screen_text.get_rect()
    text_x = screen.get_width() / 2 - text_rect.width / 2
    text_y = screen.get_height() / 2 - text_rect.height / 2
    screen.blit(screen_text, [text_x, text_y])



# Konkretyzacja obiektów
# Tworzenie playera

player = Player(gm.PLAYER_STAND_R)

# Tworzenie levelów

level_list = []
level_list.append(Level_1(player))
level_list.append(Level_2(player))

# Sprawdzanie obecnego levela:

id_level = 0
current_level = level_list[id_level]
player.level = current_level
player.rect.x = 0
player.rect.y = gm.HEIGHT - player.rect.height

# Głowna pętla gry

window_open = True
while window_open:
    screen.blit(gm.BACKGROUND, (0,-340))

    # Pętla zdarzeń(np ruch myszka itp)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                window_open = False
            if event.key == pygame.K_q:
                window_open = False
        elif event.type == pygame.QUIT:
            window_open = False

        player.get_event(event)

    # Rysowanie i aktualizacja obiektów
    # Aktualizacja playera

    player.update()

    # Aktualzicja levela

    current_level.update()

    # Przechodzenie do następnego poziomu
    current_position = player.rect.x + current_level.world_shift
    if current_position < current_level.level_limit:
        if id_level < len(level_list) - 1:
            message_to_screen("Hurra you won the level! You move to the next level!", (255, 26, 26))
            pygame.display.flip()

            # Ustawienie pozycji gracza, wyzerowanie żyć od nowa i punktów

            player.rect.x = 0
            player.lifes = 3
            player.items['shotgun'] = 0
            id_level += 1
            current_level = level_list[id_level]
            player.level = current_level
            complete_level_fx.play()
            time.sleep(2)
        else:

            # Koniec leveli == koniec gry
            while not pygame.key.get_pressed()[pygame.K_q]:
                message_to_screen("Hurra you won the game! Press Q to Exit",  (255, 26, 26))
                pygame.display.flip()
                pygame.event.get()
            window_open = False

    # Rysowanie obiektów

    current_level.draw(screen)
    player.draw(screen)

    # Aktualizacja okna pygame

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
