import math
import logging
import arcade
import arcade.key
import arcade.key
import pymunk

from game_object import Bird, Column, LevelManager, Pig, YellowBird, BlueBird, ExplosiveBird, GrowingBird
from game_logic import get_impulse_vector, Point2D, get_distance

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("arcade").setLevel(logging.WARNING)
logging.getLogger("pymunk").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("main")

WIDTH = 1800
HEIGHT = 600
TITLE = "Angry birds"
GRAVITY = -900
MAX_BIRDS = 3


class App(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        self.background = arcade.load_texture("assets/img/background3.png")
        # crear espacio de pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # agregar piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 15], [WIDTH, 15], 0.0)
        floor_shape.friction = 10
        self.space.add(floor_body, floor_shape)

        self.sprites = arcade.SpriteList()
        self.birds = arcade.SpriteList()
        self.world = arcade.SpriteList()
        # self.add_columns()
        # self.add_pigs()
        self.level_manager = LevelManager(self.space)
        self.level_manager.load_level(self.sprites, self.world, self.birds)
        self.mouse_press = None

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False
        self.bird_count = 0 

        # agregar un collision handler
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler
        
        # que cambie de tipo de pájaro, aquí se guarda
        self.bird_type = Bird
        self.bird_image = "assets/img/red-bird3.png"      

        # para que se pueda hacer click dos veces y no se dibuje, sino se aumente la velocidad del pajaro amarillo o se divida el pajáro azul
        self.bird_flying = False
        self.active_bird = None
        self.game_over = False
        
        # Niveles y puntaje
        self.score = 0
        self.total_score = 0
        self.remaining_pigs = len([obj for obj in self.world if isinstance(obj, Pig)])


    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        logger.debug(impulse_norm)
        if impulse_norm > 1200:
            for obj in self.world:
                if obj.shape in arbiter.shapes:
                    if isinstance(obj, Pig):
                        self.score += 100
                        self.remaining_pigs -= 1
                    elif isinstance(obj, Column):
                        self.score += 35
                    obj.remove_from_sprite_lists()
                    self.space.remove(obj.shape, obj.body)
        for bird in self.birds:
            if bird.shape in arbiter.shapes:
                self.bird_flying = False
                self.active_bird = None
                break
        
        return True
            
    def setup_level(self):
        for obj in self.world:
            self.space.remove(obj.shape, obj.body)
        self.level_manager.load_level(self.sprites, self.world, self.birds)
        self.bird_count = 0
        self.score = 0
        self.remaining_pigs = len([obj for obj in self.world if isinstance(obj, Pig)])

        
    # def add_columns(self, num_columns):
    #     for i in range(num_columns):
    #         x = WIDTH // 2 + (i * 400)
    #         column = Column(x, 50, self.space)
    #         self.sprites.append(column)
    #         self.world.append(column)

    # def add_pigs(self, num_pigs):
    #     for i in range(num_pigs):
    #         x = WIDTH / 2 + (i * 100)
    #         pig = Pig(x, 100, self.space)
    #         self.sprites.append(pig)
    #         self.world.append(pig)

    def on_update(self, delta_time: float):
        if self.game_over:
            return

        self.space.step(1 / 60.0)
        self.update_collisions()
        self.sprites.update()
        self.check_active_bird()
        if self.bird_count >= MAX_BIRDS and self.remaining_pigs > 0 and not self.bird_flying:
            self.game_over = True
            self.total_score += self.score
            logger.debug(f"¡Perdiste! Puntaje acumulado: {self.total_score}")
            self.setup_level()
        if self.remaining_pigs == 0 and self.bird_count >= MAX_BIRDS:
            if self.level_manager.next_level():
                self.total_score += self.score
                self.setup_level()
            else:
                logger.debug("¡Juego completado!")
                logger.debug(f"Puntaje acumulado: {self.total_score}")
                self.close()
                return

        # if all(isinstance(sprite, Pig) and sprite.is_destroyed for sprite in self.world):
        #     if self.level_manager.next_level():
        #         self.setup_level()
        #     else:
        #         logger.debug("¡Juego completado!")
        #         self.close()
        #         return
        # if self.bird_count > MAX_BIRDS:
        #     if any(isinstance(sprite, Pig) and not sprite.is_destroyed for sprite in self.world):
        #         self.game_over = True
        #         logger.debug("¡Perdiste!")
        #         self.setup_level()

    def update_collisions(self):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.bird_flying:
                if isinstance(self.active_bird, YellowBird) and not self.active_bird.has_boosted:
                    self.active_bird.boost()
                if isinstance(self.active_bird, BlueBird) and not self.active_bird.has_split:
                    self.active_bird.split(self)
                if isinstance(self.active_bird, ExplosiveBird) and not self.active_bird.has_exploded:
                    self.active_bird.explode(self)
                if isinstance(self.active_bird, GrowingBird) and not self.active_bird.has_growth:
                    self.active_bird.growth()
            else:
                self.start_point = Point2D(x, y)
                self.end_point = Point2D(x, y)
                self.draw_line = True
                logger.debug(f"Start Point: {self.start_point}")
           
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons == arcade.MOUSE_BUTTON_LEFT:
            self.end_point = Point2D(x, y)
            logger.debug(f"Dragging to: {self.end_point}") 
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT and not self.bird_flying:
            logger.debug(f"Releasing from: {self.end_point}")
            self.draw_line = False
            impulse_vector = get_impulse_vector(self.start_point, self.end_point)
            self.bird_count += 1 
            bird = self.bird_type(self.bird_image, impulse_vector, x, y, self.space)
            self.sprites.append(bird)
            self.birds.append(bird)
            self.bird_flying = True
            self.active_bird = bird
        else:
                logger.debug("¡No puedes lanzar más pájaros!")

    def check_active_bird(self):
        if self.active_bird:
            if self.active_bird.body.position.y < 0 or \
            self.active_bird.body.position.x < 0 or \
            self.active_bird.body.position.x > WIDTH or \
            self.active_bird.body.position.y > HEIGHT or \
            self.active_bird.body.velocity.length < 10:
                self.active_bird = None
                self.bird_flying = False                
    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.R: 
            self.bird_type = Bird
            self.bird_image = "assets/img/red-bird3.png"
        elif symbol == arcade.key.B: 
            self.bird_type = BlueBird
            self.bird_image = "assets/img/blue.png"       
        elif symbol == arcade.key.Y:
            self.bird_type = YellowBird
            self.bird_image = "assets/img/chuck.png"
        elif symbol == arcade.key.E:
            self.bird_type = ExplosiveBird
            self.bird_image = "assets/img/explosive.png"
        elif symbol == arcade.key.G:
            self.bird_type = GrowingBird
            self.bird_image = "assets/img/growing.png"
              
        
    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        self.sprites.draw()
        if self.draw_line:
            arcade.draw_line(self.start_point.x, self.start_point.y, self.end_point.x, self.end_point.y,
                             arcade.color.BLACK, 3)
        arcade.draw_text(f"Puntaje: {self.score}", 10, HEIGHT - 30, arcade.color.WHITE, font_size=20)
        if self.game_over:
            arcade.draw_text("¡Perdiste!", WIDTH // 2, HEIGHT // 2, arcade.color.RED, font_size=50, anchor_x="center")


def main():
    app = App()
    arcade.run()


if __name__ == "__main__":
    main()