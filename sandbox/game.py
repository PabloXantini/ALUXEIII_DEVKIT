import pygame
import os
import random
import math
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from sandbox.entities import Ball, Goal, Pitch

class GameController:
    def __init__(self, width=800, height=600, debug=False, mosaic=True):
        self.debug = debug
        self.mosaic = mosaic
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("FUT_ALUX - 2D Match Sandbox")
        self.clock = pygame.time.Clock()
        self.running = True

        self.score = {"blue": 0, "yellow": 0}

        # Entidades globales
        self.pitch = Pitch(width, height, padding=40)
        self.ball = Ball(width / 2, height / 2)
        
        # Meta Aliada = Azul (Izquierda), Meta Enemiga = Amarilla (Derecha)
        self.ally_goal = Goal(0, height / 2 - 100, 40, 200, (30, 80, 200))
        self.enemy_goal = Goal(width - 40, height / 2 - 100, 40, 200, (220, 220, 20))

        # Configuraciones de Simulación y Reglas
        self.RULE_PENALTY_BAN = True
        self.RULE_PENALTY_NEUTRAL = True
        self.RULE_PITCH_BOUNDS_BAN = True
        self.RULE_SAFE_LINES_BAN = True

        self.match_minutes = 2
        self.match_seconds = 0
        self.total_match_time = self.match_minutes * 60 + self.match_seconds
        self.half_time = self.total_match_time / 2.0
        self.time_elapsed = 0.0
        self.current_half = 1

        self.ball_untouched_timer = 0.0
        self.BALL_UNTOUCHED_LIMIT = 20.0

        self.missing_team_timer = {"blue": 0.0, "yellow": 0.0}
        self.kickoff_team = random.choice(["blue", "yellow"])
        self.is_kickoff = True
        self.base_positions = {}
        self.match_over = False

    def reset_match(self, robots):
        self.score = {"blue": 0, "yellow": 0}
        self.time_elapsed = 0.0
        self.current_half = 1
        self.match_over = False
        self.kickoff_team = random.choice(["blue", "yellow"])
        for r in robots:
            r.ban_timer = 0.0
        self.setup_kickoff(robots)

    def setup_kickoff(self, robots):
        self.reset_ball()
        self.is_kickoff = True
        
        assigned_kickoff = False
        for r in robots:
            base_x = r.kickoff_x
            base_y = r.kickoff_y
            base_angle = 0.0 if r.team == "blue" else math.pi
            
            # Forzar que estén en su propia zona del campo
            if r.team == "blue":
                base_x = min(base_x, self.width / 2 - r.radius)
            else:
                base_x = max(base_x, self.width / 2 + r.radius)
            
            if r.team == self.kickoff_team:
                if not assigned_kickoff:
                    # El que saca tiene que estar cerca de la pelota
                    r.x = self.ball.x - 30 if r.team == "blue" else self.ball.x + 30
                    r.y = self.ball.y
                    r.rangle = base_angle
                    assigned_kickoff = True
                else:
                    r.x = base_x + random.uniform(-10, 10)
                    r.y = base_y + random.uniform(-10, 10)
                    r.rangle = base_angle
            else:
                r.x = base_x
                r.y = base_y
                r.rangle = base_angle
                # Asegurar distancia de >= 50 de la pelota para defensores
                dist = math.hypot(r.x - self.ball.x, r.y - self.ball.y)
                if dist < 50:
                    dir_x = (r.x - self.ball.x) / dist
                    dir_y = (r.y - self.ball.y) / dist
                    # Move exactly 50 units away along the direction from ball
                    r.x = self.ball.x + dir_x * 51
                    r.y = self.ball.y + dir_y * 51

    def check_goals(self, robots):
        if self.ball.dragging: return
        tolerance = 5.0
        # Ally goal is at x=0, width=40. Back is x=0. Bounces at x = radius.
        if ((self.ball.x <= self.ball.radius + tolerance) 
            and (self.ally_goal.rect.top <= self.ball.y <= self.ally_goal.rect.bottom)):
            self.score["yellow"] += 1
            self.kickoff_team = "blue"
            self.setup_kickoff(robots)
        # Enemy goal is at x=width-40. Back is x=width. Bounces at x = width - radius.
        elif ((self.ball.x >= self.width - self.ball.radius - tolerance)
            and (self.enemy_goal.rect.top <= self.ball.y <= self.enemy_goal.rect.bottom)):
            self.score["blue"] += 1
            self.kickoff_team = "yellow"
            self.setup_kickoff(robots)

    def reset_ball(self):
        self.ball.x = self.width / 2
        self.ball.y = self.height / 2
        self.ball.vx = 0
        self.ball.vy = 0
        self.ball.last_kicked_by = None
        self.ball_untouched_timer = 0.0

    def step(self, robots):
        if self.match_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.reset_match(robots)
                    elif event.key == pygame.K_q:
                        self.running = False
            return

        dt = 1.0 / 60.0
        self.time_elapsed += dt
        
        # Check halves
        if self.current_half == 1 and self.time_elapsed >= self.half_time:
            self.current_half = 2
            self.kickoff_team = "yellow" if self.kickoff_team == "blue" else "blue"
            for r in robots:
                r.ban_timer = 0.0
            self.setup_kickoff(robots)
        elif self.current_half == 2 and self.time_elapsed >= self.total_match_time:
            self.match_over = True
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False

        self.ball.update(self)
        for robot in robots:
            robot.update(self, robots)
            
        # Resolver colisiones físicas entre robots
        for i in range(len(robots)):
            for j in range(i + 1, len(robots)):
                r1, r2 = robots[i], robots[j]
                if r1.ban_timer > 0 or r2.ban_timer > 0: continue
                dx, dy = r2.x - r1.x, r2.y - r1.y
                dist = math.hypot(dx, dy)
                if 0 < dist < r1.radius + r2.radius:
                    overlap = (r1.radius + r2.radius - dist) / 2
                    nx, ny = dx / dist, dy / dist
                    r1.x -= nx * overlap; r1.y -= ny * overlap
                    r2.x += nx * overlap; r2.y += ny * overlap
            
        self.check_goals(robots)
        # Verificar limites de campo (Zona Segura)
        if self.pitch.check_bounds(self.ball, [self.ally_goal, self.enemy_goal]):
            if self.RULE_SAFE_LINES_BAN and self.ball.last_kicked_by:
                self.ball.last_kicked_by.ban_timer = 60.0 # 1 min ban
            self.reset_ball()

        # Ball untouched timeout
        if abs(self.ball.vx) < 0.1 and abs(self.ball.vy) < 0.1 and not self.ball.dragging:
            self.ball_untouched_timer += dt
        else:
            self.ball_untouched_timer = 0.0

        if self.ball_untouched_timer >= self.BALL_UNTOUCHED_LIMIT:
            self.ball_untouched_timer = 0.0
            neutral_positions = {
                "blue": [(200, 150), (200, 450)],
                "yellow": [(600, 150), (600, 450)]
            }
            assigned = {"blue": 0, "yellow": 0}
            for r in robots:
                if r.ban_timer <= 0 and assigned[r.team] < 2:
                    pos = neutral_positions[r.team][assigned[r.team]]
                    r.x, r.y = pos
                    assigned[r.team] += 1
            self.reset_ball()
            
        # Penalty Area Rules and Pitch bounds for robots
        active_counts = {"blue": 0, "yellow": 0}
        total_counts = {"blue": 0, "yellow": 0}
        
        for r in robots:
            total_counts[r.team] += 1
            if r.ban_timer > 0: continue
            active_counts[r.team] += 1
            
            r_rect = pygame.Rect(r.x - r.radius, r.y - r.radius, r.radius*2, r.radius*2)
            
            # Pitch Bounds (Touch borders)
            if self.RULE_PITCH_BOUNDS_BAN:
                if (r.x - r.radius <= 0 or r.x + r.radius >= self.width or
                    r.y - r.radius <= 0 or r.y + r.radius >= self.height):
                    r.ban_timer = 60.0
                    continue
            
            # Penalty Zones
            for zone in [self.pitch.ally_penalty_zone, self.pitch.enemy_penalty_zone]:
                if zone.contains(r_rect):
                    if self.RULE_PENALTY_BAN:
                        r.ban_timer = 60.0
                elif zone.colliderect(r_rect):
                    if self.RULE_PENALTY_NEUTRAL:
                        # Check if teammate is also inside/colliding
                        for other in robots:
                            if other != r and other.team == r.team and other.ban_timer <= 0:
                                o_rect = pygame.Rect(other.x - other.radius, other.y - other.radius, other.radius*2, other.radius*2)
                                if zone.colliderect(o_rect):
                                    # Move to neutral
                                    r.x = self.width / 2
                                    r.y = 50 if r.y < self.height/2 else self.height - 50
                                    break

        # Missing team penalty
        for team in ["blue", "yellow"]:
            if total_counts[team] > 0 and active_counts[team] < total_counts[team]:
                self.missing_team_timer[team] += dt
                if self.missing_team_timer[team] >= 30.0:
                    self.missing_team_timer[team] = 0.0
                    other_team = "yellow" if team == "blue" else "blue"
                    self.score[other_team] += 1
            else:
                self.missing_team_timer[team] = 0.0

    def render(self, robots):
        # 1. Dibujar Campo (Pitch)
        self.pitch.draw(self.screen)
        
        # 2. Dibujar Metas
        self.ally_goal.draw(self.screen)
        self.enemy_goal.draw(self.screen)
        
        # 3. Dibujar Entidades Dinámicas
        for robot in robots:
            robot.draw(self.screen, debug=self.debug)
        self.ball.draw(self.screen)

        # 4. UI: Tablero de Puntuación y Tiempo
        font = pygame.font.SysFont(None, 48)
        score_txt = font.render(f"AZUL {self.score['blue']} - {self.score['yellow']} AMARILLO", True, (255, 255, 255))
        self.screen.blit(score_txt, (self.width / 2 - score_txt.get_width() // 2, 50))
        
        font_small = pygame.font.SysFont(None, 32)
        mins = int(self.time_elapsed // 60)
        secs = int(self.time_elapsed % 60)
        time_txt = font_small.render(f"Tiempo: {mins:02d}:{secs:02d} | Mitad {self.current_half}", True, (200, 200, 200))
        self.screen.blit(time_txt, (self.width / 2 - time_txt.get_width() // 2, 10))

        if self.match_over:
            font_large = pygame.font.SysFont(None, 72)
            if self.score["blue"] > self.score["yellow"]:
                winner = "GANA AZUL"
            elif self.score["blue"] < self.score["yellow"]:
                winner = "GANA AMARILLO"
            else:
                winner = "EMPATE"
            over_txt = font_large.render(f"FIN DEL JUEGO\n{winner}", True, (255, 255, 255))
            self.screen.blit(over_txt, (self.width / 2 - over_txt.get_width() // 2, self.height / 2 - 30))
            
            font_small2 = pygame.font.SysFont(None, 36)
            restart_txt = font_small2.render("Presiona ENTER para reiniciar", True, (200, 200, 200))
            self.screen.blit(restart_txt, (self.width / 2 - restart_txt.get_width() // 2, self.height / 2 + 30))

        # 5. UI: Depuración FSM
        if robots:
            font_small = pygame.font.SysFont(None, 24)
            y_offset = 500
            for r in robots:
                if r.context:
                    color = (255, 50, 50) if r.ban_timer > 0 else (255, 255, 255)
                    ban_text = f" [BANEADO {int(r.ban_timer)}s]" if r.ban_timer > 0 else ""
                    lbl = font_small.render(f"FSM {r.name}[{r.team}]: {r.context.estado_label}{ban_text}", True, color)
                    self.screen.blit(lbl, (10, y_offset))
                    y_offset += 25

        # 6. Actualizar Ventana y FPS en título
        actual_fps = self.clock.get_fps()
        pygame.display.set_caption(f"FUT_ALUX - 2D Match Sandbox | FPS: {actual_fps:.1f}")
        pygame.display.flip()
        self.clock.tick(60) # Limitar a 60 FPS
        
    def show_virtual_cameras(self, robots):
        """Método helper para desplegar los streams visuales de todos los robots en modo mosaico o individual"""
        if self.debug:
            import cv2
            import numpy as np
            frames = []
            for robot in robots:
                if hasattr(robot, 'context') and robot.context:
                    if not self.mosaic:
                        robot.context.show_debug()
                    else:
                        frame = robot.context.get_debug_frame()
                        if frame is not None:
                            frames.append(frame)
            
            if self.mosaic and frames:
                # Calculate grid size (e.g. 2x2 for 4 robots, 3x2 for 6)
                n = len(frames)
                cols = int(np.ceil(np.sqrt(n)))
                rows = int(np.ceil(n / cols))
                
                # Resize and pad frames to assemble a grid
                h, w, c = frames[0].shape
                grid = np.zeros((h * rows, w * cols, c), dtype=np.uint8)
                
                for idx, frame in enumerate(frames):
                    r = idx // cols
                    c_idx = idx % cols
                    grid[r*h:(r+1)*h, c_idx*w:(c_idx+1)*w] = frame
                    
                cv2.imshow("Virtual Cameras", grid)
        
    def cleanup(self):
        pygame.quit()
