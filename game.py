import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap, QFont


class Zombie:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 100
        self.speed = random.uniform(0.5, 1)
        self.image = QPixmap("zombie.png").scaled(self.width, self.height)
        self.hitbox = QRectF(x, y, self.width, self.height)
        self.name = name

    def update_hitbox(self):
        self.hitbox = QRectF(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.update_hitbox()

    def draw(self, painter):
        painter.drawPixmap(int(self.x), int(self.y), self.image)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 90
        self.height = 78
        self.velocity_x = 0
        self.velocity_y = 0
        self.move_speed = 6
        self.image_left = QPixmap("character_left.png").scaled(self.width, self.height)
        self.image_right = QPixmap("character_right.png").scaled(self.width, self.height)
        self.current_image = self.image_right
        self.hitbox = QRectF(x, y, self.width, self.height)
        self.projectiles = []
        self.projectile_cooldown = 0
        self.projectile_cooldown_max = 45

    def update_hitbox(self):
        self.hitbox = QRectF(self.x, self.y, self.width, self.height)

    def move_left(self):
        self.velocity_x = -self.move_speed
        self.current_image = self.image_left

    def move_right(self):
        self.velocity_x = self.move_speed
        self.current_image = self.image_right

    def stop(self):
        self.velocity_x = 0

    def shoot_projectile(self):
        if self.projectile_cooldown <= 0:
            projectile = Projectile(self.x, self.y + self.height / 2)
            self.projectiles.append(projectile)
            self.projectile_cooldown = self.projectile_cooldown_max

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1

        for projectile in self.projectiles:
            projectile.update()

        self.update_hitbox()

    def draw(self, painter):
        painter.drawPixmap(int(self.x), int(self.y), self.current_image)

        for projectile in self.projectiles:
            projectile.draw(painter)


class Projectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.velocity_x = 10
        self.image = QPixmap("projectile.png").scaled(self.width, self.height)
        self.hitbox = QRectF(x, y, self.width, self.height)

    def update(self):
        self.x += self.velocity_x
        self.update_hitbox()

    def draw(self, painter):
        painter.drawPixmap(int(self.x), int(self.y), self.image)

    def update_hitbox(self):
        self.hitbox = QRectF(self.x, self.y, self.width, self.height)


class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zombie Survival")
        self.setFixedSize(1060, 883)  # Window size
        self.background_image = QPixmap("background.jpg")
        self.menu_button = QPushButton("Start")
        self.menu_button.clicked.connect(self.start_game)
        self.wave_counter_font = QFont("Arial", 20)
        self.zombie_counter_font = QFont("Arial", 20)
        self.zombie_counter = 0

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.menu_button)
        self.setLayout(self.layout)

        self.game_started = False
        self.menu_visible = True
        self.round = 1
        self.num_zombies = 5
        self.player = None
        self.zombies = []
        self.ground_y = 800  # Ground position

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)

        self.setFocusPolicy(Qt.StrongFocus)
        self.show()

    def start_game(self):
        if not self.game_started:
            self.menu_visible = False
            self.menu_button.hide()
            self.player = Player(50, self.ground_y - 78)  # Player initial position on the ground
            self.spawn_initial_zombies()
            self.timer.start(16)
            self.game_started = True

    def spawn_initial_zombies(self):
        for i in range(self.num_zombies):
            x = self.width() + random.randint(200, 800)
            y = self.ground_y - 100  # Zombies start at the ground level
            name = f"Zombie {i+1}"
            zombie = Zombie(x, y, name)
            self.zombies.append(zombie)
            self.zombie_counter += 1

    def keyPressEvent(self, event):
        if self.game_started:
            if event.key() == Qt.Key_Left:
                self.player.move_left()
            elif event.key() == Qt.Key_Right:
                self.player.move_right()
            elif event.key() == Qt.Key_Z:
                self.player.shoot_projectile()

    def keyReleaseEvent(self, event):
        if self.game_started:
            if event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
                self.player.stop()

    def update_game(self):
        self.player.update()
        for zombie in self.zombies:
            zombie.update()
        self.check_collisions()
        self.check_round()
        self.repaint()

    def check_collisions(self):
        for zombie in self.zombies:
            if self.player.hitbox.intersects(zombie.hitbox):
                # Implement collision logic here (e.g., decrease player health, end game, etc.)
                pass

        for projectile in self.player.projectiles:
            for zombie in self.zombies:
                if projectile.hitbox.intersects(zombie.hitbox):
                    self.player.projectiles.remove(projectile)
                    self.zombies.remove(zombie)
                    self.zombie_counter -= 1
                    # Handle projectile hit on a zombie
                    break

    def check_round(self):
        if len(self.zombies) == 0:
            self.round += 1
            self.num_zombies += 5
            self.spawn_initial_zombies()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawPixmap(0, 0, self.width(), self.height(), self.background_image)

        if self.menu_visible:
            painter.drawText(event.rect(), Qt.AlignCenter, "Zombie Survival")
        else:
            ground_rect = QRectF(0, self.ground_y, self.width(), self.height() - self.ground_y)
            painter.drawRect(ground_rect)

            self.player.draw(painter)

            for zombie in self.zombies:
                zombie.draw(painter)

            for projectile in self.player.projectiles:
                projectile.draw(painter)

            painter.setFont(self.wave_counter_font)
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            wave_counter_rect = QRectF(10, 10, 150, 50)
            painter.drawRect(wave_counter_rect)
            painter.setPen(Qt.white)
            painter.drawText(wave_counter_rect, Qt.AlignCenter, f"Wave: {self.round}")

            painter.setFont(self.zombie_counter_font)
            painter.drawText(self.width() - 160, 10, 150, 50, Qt.AlignCenter, f"Zombies: {self.zombie_counter}")

    def closeEvent(self, event):
        self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game_window = GameWindow()
    sys.exit(app.exec_())
