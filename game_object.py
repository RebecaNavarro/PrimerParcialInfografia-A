import math
import arcade
import arcade.key
import pymunk
from game_logic import ImpulseVector

class Bird(arcade.Sprite):
    """
    Bird class. This represents an angry bird. All the physics is handled by Pymunk,
    the init method only set some initial properties
    """
    def __init__(
        self,
        image_path: str,
        impulse_vector: ImpulseVector,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 5,
        radius: float = 12,
        max_impulse: float = 100,
        power_multiplier: float = 50,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)
        # body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        impulse = min(max_impulse, impulse_vector.impulse) * power_multiplier
        impulse_pymunk = impulse * pymunk.Vec2d(1, 0)
        # apply impulse
        body.apply_impulse_at_local_point(impulse_pymunk.rotated(impulse_vector.angle))
        # shape
        shape = pymunk.Circle(body, radius)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer

        space.add(body, shape)

        self.body = body
        self.shape = shape

    def update(self):
        """
        Update the position of the bird sprite based on the physics body position
        """
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class Pig(arcade.Sprite):
    def __init__(
        self,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 0.4,
        collision_layer: int = 0,
    ):
        super().__init__("assets/img/pig_failed.png", 0.1)
        moment = pymunk.moment_for_circle(mass, 0, self.width / 2 - 3)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Circle(body, self.width / 2 - 3)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape
        self.is_destroyed = False

    def update(self):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class PassiveObject(arcade.Sprite):
    """
    Passive object that can interact with other objects.
    """
    def __init__(
        self,
        image_path: str,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)

        moment = pymunk.moment_for_box(mass, (self.width, self.height))
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Poly.create_box(body, (self.width, self.height))
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class Column(PassiveObject):
    def __init__(self, x, y, space):
        super().__init__("assets/img/column.png", x, y, space)


class StaticObject(arcade.Sprite):
    def __init__(
            self,
            image_path: str,
            x: float,
            y: float,
            space: pymunk.Space,
            mass: float = 2,
            elasticity: float = 0.8,
            friction: float = 1,
            collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)

class YellowBird(Bird):
    def __init__(
        self, 
        image_path: str, 
        impulse_vector: ImpulseVector, 
        x: float, 
        y: float, 
        space: pymunk.Space, 
        mass: float = 5, 
        radius: float = 12, 
        max_impulse: float = 100, 
        power_multiplier: float = 50,
        elasticity: float = 0.8, 
        friction: float = 1, 
        collision_layer: int = 0, 
        boost_multiplier: float = 2
    ):
        super().__init__(image_path, impulse_vector, x, y, space, mass, radius, max_impulse, power_multiplier, elasticity, friction, collision_layer)
        self.initial_impulse = impulse_vector
        self.boost_multiplier = boost_multiplier
        self.has_boosted = False


    def boost(self):
        if not self.has_boosted:
            impulse_vector = pymunk.Vec2d(1, 0).rotated(self.body.angle) * self.boost_multiplier * self.body.mass * 500
            self.body.apply_impulse_at_local_point(impulse_vector)
            self.has_boosted = True
       
class BlueBird(Bird):
    def __init__(
        self, 
        image_path: str, 
        impulse_vector: ImpulseVector, 
        x: float, 
        y: float, 
        space: pymunk.Space, 
        mass: float = 5, 
        radius: float = 12, 
        max_impulse: float = 100, 
        power_multiplier: float = 50,
        elasticity: float = 0.8, 
        friction: float = 1, 
        collision_layer: int = 0
    ):
        super().__init__(image_path, impulse_vector, x, y, space, mass, radius, max_impulse, power_multiplier, elasticity, friction, collision_layer)
        self.has_split = False
        self.space = space

    def split(self, app):
        if not self.has_split:
            angles = [-30, 30]

            for angle in angles:
                new_angle = self.body.velocity.angle + math.radians(angle)
                new_velocity_vector = pymunk.Vec2d(self.body.velocity.length, 0).rotated(new_angle)

                new_body = pymunk.Body(self.body.mass, self.body.moment)
                new_body.position = self.body.position 
                new_body.velocity = new_velocity_vector  

                new_shape = pymunk.Circle(new_body, self.shape.radius)
                new_shape.elasticity = self.shape.elasticity
                new_shape.friction = self.shape.friction

                new_bird = BlueBird(
                    self.texture.name,
                    ImpulseVector(new_velocity_vector.angle, new_velocity_vector.length),
                    new_body.position.x,
                    new_body.position.y,
                    self.space
                )
                new_bird.body = new_body 
                new_bird.shape = new_shape 
                self.space.add(new_bird.body, new_bird.shape)
                app.sprites.append(new_bird)  
                app.birds.append(new_bird)  

        self.has_split = True  

class ExplosiveBird(Bird):
    def __init__(
        self, 
        image_path: str, 
        impulse_vector: ImpulseVector, 
        x: float, 
        y: float, 
        space: pymunk.Space, 
        mass: float = 5, 
        radius: float = 12, 
        max_impulse: float = 100, 
        power_multiplier: float = 50,
        elasticity: float = 0.8, 
        friction: float = 1, 
        collision_layer: int = 0
    ):
        super().__init__(image_path, impulse_vector, x, y, space, mass, radius, max_impulse, power_multiplier, elasticity, friction, collision_layer)
        self.has_exploded = False  
        self.space = space

    def explode(self, app):
        if not self.has_exploded:
            self.has_exploded = True
            angles =[-90, -60, -30, 30, 60, 90,180]
            for angle in angles:  
                new_angle = self.body.velocity.angle + math.radians(angle)
                new_velocity_vector = pymunk.Vec2d(self.body.velocity.length, 0).rotated(new_angle)

                new_body = pymunk.Body(self.body.mass, self.body.moment)
                new_body.position = self.body.position 
                new_body.velocity = new_velocity_vector  

                new_shape = pymunk.Circle(new_body, self.shape.radius)
                new_shape.elasticity = self.shape.elasticity
                new_shape.friction = self.shape.friction

                new_bird = ExplosiveBird(
                    self.texture.name,
                    ImpulseVector(new_velocity_vector.angle, new_velocity_vector.length),
                    new_body.position.x,
                    new_body.position.y,
                    self.space
                )
                new_bird.body = new_body 
                new_bird.shape = new_shape 
                self.space.add(new_bird.body, new_bird.shape)
                app.sprites.append(new_bird)  
                app.birds.append(new_bird)  

        self.has_exploded = True

class GrowingBird(Bird):
    def __init__(
        self, 
        image_path: str, 
        impulse_vector: ImpulseVector, 
        x: float, 
        y: float, 
        space: pymunk.Space, 
        mass: float = 5, 
        radius: float = 12, 
        max_impulse: float = 100, 
        power_multiplier: float = 50,
        elasticity: float = 0.8, 
        friction: float = 1, 
        collision_layer: int = 0
    ):
        super().__init__(image_path, impulse_vector, x, y, space, mass, radius, max_impulse, power_multiplier, elasticity, friction, collision_layer)
        
        self.space = space
        self.radius = radius
        self.mass = mass
        self.elasticity = elasticity
        self.friction = friction
        
        self.has_growth = False  

    def growth(self):
        if not self.has_growth:
            self.radius *= 1.5 
            self.mass *= 2    
            self.has_growth = True
            
            self.space.remove(self.body, self.shape)  
            
            body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass, 0, self.radius))
            body.position = self.body.position
            body.velocity = self.body.velocity
            shape = pymunk.Circle(body, self.radius)
            shape.elasticity = self.elasticity
            shape.friction = self.friction

            self.space.add(body, shape)

            self.body = body
            self.shape = shape

            self.scale = self.radius / 12
            
            
class LevelManager:
    def __init__(self, space):
        self.space = space
        self.current_level = 0
        self.levels = [
            self.level_1,
            self.level_2,
            self.level_3,
            self.level_4,
        ]

    def load_level(self, sprites, world, birds):
        sprites.clear()
        world.clear()
        birds.clear()
        self.levels[self.current_level](sprites, world)
        return len([obj for obj in world if isinstance(obj, Pig)])

    def next_level(self):
        if self.current_level + 1 < len(self.levels):
            self.current_level += 1
            return True
        return False

    def add_objects(self, columns_data, pigs_data, sprites, world):
        for x, y in columns_data:
            column = Column(x, y, self.space)
            sprites.append(column)
            world.append(column)
        for x, y in pigs_data:
            pig = Pig(x, y, self.space)
            sprites.append(pig)
            world.append(pig)
            
    def level_1(self, sprites, world):
        columns_data = [
            (600, 50),   
        ]
        pigs_data = [
            (600, 100),
        ]
        self.add_objects(columns_data, pigs_data, sprites, world)

    def level_2(self, sprites, world):
        columns_data = [
            (600, 50),
            (800, 50),   
        ]
        pigs_data = [
            (600, 100),
            (750, 100),
            (850, 100),
        ]
        self.add_objects(columns_data, pigs_data, sprites, world)

            
    def level_3(self, sprites, world):
        columns_data = [
            (700, 50),
            (750, 50), 
            (850, 50),
            (900, 50),    
        ]
        pigs_data = [
            (800, 50),
        ]
        self.add_objects(columns_data, pigs_data, sprites, world)
    def level_4(self, sprites, world):
        columns_data = [
            (650, 50),
            (700, 50),   
            (800, 50),   
            (850, 50),   

        ]
        pigs_data = [
            (675, 100),
            (825, 100),
        ]
        self.add_objects(columns_data, pigs_data, sprites, world)

