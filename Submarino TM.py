import pygame
from pygame.locals import *
import matplotlib.pyplot as plt
import sys

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 563
sea_level = 0
submarine_image_pos_xLim = 880
submarine_image_pos_yLim = 500
submarine_image_pos_y_init = sea_level
g = 9.8  # Gravedad
p = 1000  # Densidad del agua
dt = 1
b = 250  # Resistencia
b2 = 50
e = -(p * g * dt)  # Flotabilidad
propeller_acceleration = 0.02
bullets = []


def redraw(screen, submarine):
    screen.blit(background_image, (0, 0))
    submarine.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)


# Classes and Functions
class Projectile:
    def __init__(self, x, y, radius, direction):
        self.x = x
        self.y = y
        self.radius = 5
        self.direction = direction
        self.vel_x = 50 * direction  # Velocidad horizontal
        self.vel_y = 0  # Velocidad vertical inicialmente es 0
        self.gravity = -9.8  # Gravedad
        self.water_density = 1000  # Densidad del agua
        self.Cd = 0.47  # Coeficiente de arrastre
        self.A = 3.14 * (self.radius ** 2)  # Área de la sección transversal
        self.m = (4 / 3) * 3.14 * (self.radius ** 3) * 0.70  # Masa del proyectil
        self.t = 0  # Tiempo
        self.x0 = x  # Posición inicial en x
        self.y0 = y  # Posición inicial en y
        self.v0x = self.vel_x  # Velocidad inicial en x
        self.v0y = self.vel_y  # Velocidad inicial en y

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), self.radius)

    def update(self):  # Nuevo método para actualizar la posición y velocidad del proyectil
        self.t += 0.01
        self.vel_y = self.v0y + 0.5 * self.gravity * self.t ** 2 - 0.5 * self.water_density * self.Cd * self.A * abs(
            self.vel_y) * self.t ** 2 / self.m
        self.y = self.y0 + self.v0y * self.t - 0.5 * self.gravity * self.t ** 2
        self.x = self.x0 + self.v0x * self.t


class Reservoir:
    def __init__(self, actual_level, valve_flow, max_capacity, fluid_to_pump):
        self.actual_level = actual_level
        self.valve_flow = valve_flow
        self.max_capacity = max_capacity
        self.fluid_to_pump = fluid_to_pump

    def pumping_air_water(self, fluid_to_pump):
        if fluid_to_pump == 'air':
            if self.actual_level > 0:
                self.actual_level = max(0, self.actual_level - self.valve_flow)
        elif fluid_to_pump == 'water':
            if self.actual_level < self.max_capacity:
                self.actual_level = min(self.max_capacity, self.actual_level + self.valve_flow)


class Submarine:
    def __init__(self, tank, mass, actual_velocity_y, pos_y, actual_velocity_x, pos_x):
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.mass = mass
        self.actual_velocity_y = actual_velocity_y
        self.tank = tank
        self.actual_velocity_x = actual_velocity_x
        self.left = False
        self.right = False
        self.quieto = False
        self.image = pygame.image.load("submarino.png").convert_alpha()
        self.image2 = pygame.image.load("submarino-rotated.png").convert_alpha()
        self.image3 = pygame.image.load("submarino.png").convert_alpha()
        self.last_direction = 1
        self.mouse_x = 0  # Inicializar coordenada x del mouse
        self.mouse_y = 0  # Inicializar coordenada y del mouse
        self.move_to_click = False  # Variable para rastrear si se ha hecho clic

    def draw(self, screen):
        screen.blit(self.image, (self.pos_x, self.pos_y))

    def calculate_mass(self):
        self.mass = self.tank.actual_level

    def calculate_velocity_y(self):
        self.actual_velocity_y = dt * (
                    (e / self.mass) + g - ((b * self.actual_velocity_y) / self.mass)) + self.actual_velocity_y

    def calculate_position_y(self):
        if self.move_to_click:
            if abs(self.pos_y - self.mouse_y) > 1:
                if self.pos_y < self.mouse_y:
                    self.pos_y += 1
                elif self.pos_y > self.mouse_y:
                    self.pos_y -= 1
            else:
                self.move_to_click = False
        else:
            self.pos_y = self.pos_y + self.actual_velocity_y

            if self.pos_y > submarine_image_pos_yLim:
                self.pos_y = submarine_image_pos_yLim

            if self.pos_y < sea_level:
                self.pos_y = sea_level

        return self.pos_y

    def calculate_velocity_x(self):
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            self.image = self.image2
            propeller_acceleration = +10
            self.right = True
            self.left = False

        elif keys[K_LEFT]:
            self.image = self.image3
            propeller_acceleration = -10
            self.left = True
            self.right = False
        else:
            propeller_acceleration = 0
        self.actual_velocity_x = (dt * ((propeller_acceleration - (b2 * self.actual_velocity_x)) / self.mass)) + self.actual_velocity_x

    def calculate_position_x(self):
        self.pos_x = self.pos_x + self.actual_velocity_x

        if self.pos_x > submarine_image_pos_xLim:
            self.pos_x = submarine_image_pos_xLim
        elif self.pos_x < 0:
            self.pos_x = 0

        return self.pos_x

    def show_plot(positions_y):
        plt.plot(range(len(positions_y)), positions_y)
        plt.xlabel('Tiempo')
        plt.ylabel('Posición y')
        plt.title('Movimiento del submarino en el eje Y')
        plt.grid(True)
        plt.show()


# Main function
def main():
    pygame.init()

    # Crea la ventana y establece el modo de video
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Submarine game")

    # Carga las imágenes después de inicializar la pantalla
    global background_image
    background_image = pygame.image.load("mar.jpg").convert()

    tank1 = Reservoir(1005, 2, 50000, 'air')
    submarine1 = Submarine(tank1, 2, 2, 150, 0, 500)

    # Bandera para rastrear si ya se ha disparado un proyectil
    projectile_fired = False

    while True:
        clic_made = False
        submarine1.calculate_velocity_y()
        submarine1.calculate_velocity_x()
        submarine1.calculate_position_y()
        submarine1.calculate_position_x()

        screen.blit(background_image, (0, 0))
        redraw(screen, submarine1)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    tank1.pumping_air_water('air')
                elif event.key == K_DOWN:
                    tank1.pumping_air_water('water')
                elif event.key == K_SPACE:
                    if submarine1.left:
                        bullets.append(Projectile(submarine1.pos_x, submarine1.pos_y + 30, 4, -1))
                    elif submarine1.right:
                        bullets.append(Projectile(submarine1.pos_x + 117, submarine1.pos_y + 30, 4, 1))
                    elif submarine1.quieto:
                        bullets.append(Projectile(submarine1.pos_x, submarine1.pos_y + 30, 4, submarine1.last_direction))
            elif event.type == pygame.MOUSEBUTTONDOWN and not clic_made:
                submarine1.mouse_x, submarine1.mouse_y = pygame.mouse.get_pos()
                print("Se ha detectado un clic del mouse en:", submarine1.mouse_x, submarine1.mouse_y)
                clic_made = True
                submarine1.move_to_click = True  # Establece move_to_click a True al hacer clic
                if submarine1.pos_y < submarine1.mouse_y:
                    tank1.pumping_air_water('water')
                elif submarine1.pos_y > submarine1.mouse_y:
                    tank1.pumping_air_water('air')

        for bullet in bullets:
            bullet.update()
            if bullet.direction == 0:
                bullet.y += bullet.vel
            else:
                bullet.x += bullet.direction * bullet.vel_x
            if bullet.y > 785 or bullet.x < 0 or bullet.x > 1000:
                bullets.pop(bullets.index(bullet))
        submarine1.calculate_mass()


if __name__ == "__main__":
    main()
