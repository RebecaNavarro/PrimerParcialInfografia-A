import math
import logging
import arcade
import arcade.key
import arcade.key
import pymunk

from game_object import Bird, Column, Pig, YellowBird, BlueBird
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
        self.add_columns()
        self.add_pigs()

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False

        # agregar un collision handler
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler
        
        # que cambie de tipo de pájaro, aquí se guarda
        self.bird_type = Bird
        self.bird_image = "assets/img/red-bird3.png"      

        # para que se pueda hacer click dos veces y no se dibuje, sino se aumente la velocidad del pajaro amarillo o se divida el pajáro azul
        self.bird_flying = False
        self.active_bird = None

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        logger.debug(impulse_norm)
        if impulse_norm > 1200:
            for obj in self.world:
                if obj.shape in arbiter.shapes:
                    obj.remove_from_sprite_lists()
                    self.space.remove(obj.shape, obj.body)
        for bird in self.birds:
            if bird.shape in arbiter.shapes:
                self.bird_flying = False
                self.active_bird = None
                break
        return True

    def add_columns(self):
        for x in range(WIDTH // 2, WIDTH, 400):
            column = Column(x, 50, self.space)
            self.sprites.append(column)
            self.world.append(column)

    def add_pigs(self):
        pig1 = Pig(WIDTH / 2, 100, self.space)
        self.sprites.append(pig1)
        self.world.append(pig1)

    def on_update(self, delta_time: float):
        self.space.step(1 / 60.0)  # actualiza la simulacion de las fisicas
        self.update_collisions()
        self.sprites.update()

    def update_collisions(self):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.bird_flying:
                if isinstance(self.active_bird, YellowBird) and not self.active_bird.has_boosted:
                    self.active_bird.boost()
                if isinstance(self.active_bird, BlueBird) and not self.active_bird.has_split:
                    self.active_bird.split(self)
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
            bird = self.bird_type(self.bird_image, impulse_vector, x, y, self.space)
            self.sprites.append(bird)
            self.birds.append(bird)
            self.bird_flying = True
            self.active_bird = bird

    def check_active_bird(self):
        if self.active_bird:
            if self.active_bird.body.position.y < 0 or self.active_bird.body.velocity.length < 10:
                self.active_bird = None

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
              
        
    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        self.sprites.draw()
        if self.draw_line:
            arcade.draw_line(self.start_point.x, self.start_point.y, self.end_point.x, self.end_point.y,
                             arcade.color.BLACK, 3)


def main():
    app = App()
    arcade.run()


if __name__ == "__main__":
    main()