import numpy as np
import cv2
import math

class VirtualCamera:
    """
    Motor gráfico encargado de generar frames de visión sintéticos en 2D.
    Soporta perspectiva, distancia, oclusión (Painter's Algorithm) y distorsión
    de lente estilo Ojo de Pescado (Barrel Distortion).
    """
    def __init__(self, width=320, height=240, fov_degrees=100):
        self.width = width
        self.height = height
        self.fov = math.radians(fov_degrees)
        
        # Precomputar mapas de remapeo para Ojo de Pescado (Fisheye Barrel Distortion)
        x, y = np.meshgrid(np.arange(self.width), np.arange(self.height))
        x_c = x - self.width / 2.0
        y_c = y - self.height / 2.0
        r = np.sqrt(x_c**2 + y_c**2)
        
        # Factor de compresión (k)
        k = 0.000015 
        
        # Calcular el radio máximo en las esquinas para estirar (hacer zoom) y tapar bordes negros
        max_r = np.sqrt((self.width / 2.0)**2 + (self.height / 2.0)**2)
        zoom_factor = 1 + k * max_r**2
        
        r_s = r * (1 + k * r**2)
        # Zoom-in dividiendo según cuánto se encogieron las orillas
        r_s = r_s / zoom_factor
        
        scale = r_s / np.maximum(r, 1e-5)
        self.map_x = (self.width / 2.0 + x_c * scale).astype(np.float32)
        self.map_y = (self.height / 2.0 + y_c * scale).astype(np.float32)

    def render(self, observer_x, observer_y, observer_angle, ball_entity, other_robots):
        """
        Calcula una imagen RGB representando lo que el agente ve físicamente.
        """
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Renderizado 2.5D: Cielo oscuro arriba (o paredes de la cancha) y Pasto abajo
        frame[:self.height // 2, :] = (30, 30, 30)
        frame[self.height // 2:, :] = (50, 100, 30)
        
        # Para dar textura al pasto y que la distorsión sea muy visible, dibujemos un suelo rústico ajedrezado
        for i in range(0, self.width, 40):
            cv2.line(frame, (i, self.height // 2), 
                     (self.width//2 + (i - self.width//2)*3, self.height), (40, 80, 20), 1)

        objects_to_draw = []
        
        # 1. Añadir la Pelota a la lista de renderizado
        if ball_entity:
            dx = ball_entity.x - observer_x
            dy = ball_entity.y - observer_y
            dist = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)
            diff_angle = (angle - observer_angle + math.pi) % (2 * math.pi) - math.pi
            
            # Evaluamos el fov completo. Damos math.radians(15) de gracia en los bordes para que la distorsión barril los pueda atrapar.
            if abs(diff_angle) < (self.fov / 2) + math.radians(15):
                pixels_per_radian = self.width / self.fov
                img_x = int(self.width / 2 + diff_angle * pixels_per_radian)
                dist_safe = max(1.0, dist)
                r_calc = 1500 / dist_safe
                radius = int(min(120.0, r_calc))
                
                if radius > 0:
                    objects_to_draw.append({
                        'dist': dist,
                        'x': img_x,
                        'radius': radius,
                        'color': (0, 100, 255) # Naranja en OpenCV BGR
                    })

        # 2. Añadir los demás Robots (enemigos u otros aliados) para oclusión
        for other_r in other_robots:
            dx = other_r.x - observer_x
            dy = other_r.y - observer_y
            dist = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)
            diff_angle = (angle - observer_angle + math.pi) % (2 * math.pi) - math.pi
            
            if abs(diff_angle) < (self.fov / 2) + math.radians(15):
                pixels_per_radian = self.width / self.fov
                img_x = int(self.width / 2 + diff_angle * pixels_per_radian)
                dist_safe = max(1.0, dist)
                
                # Relación física aprox: bola 12px, robot 23px
                ball_radius_ref = 12.0
                r_calc = (other_r.radius / ball_radius_ref) * 1500 / dist_safe
                radius = int(min(240.0, r_calc))
                
                if radius > 0:
                    # Invertir color RGB a BGR para OpenCV y oscurecer
                    v = 0.1
                    bgr_color = (other_r.team_color[2] * v, other_r.team_color[1] * v, other_r.team_color[0] * v)
                    objects_to_draw.append({
                        'dist': dist,
                        'x': img_x,
                        'radius': radius,
                        'color': bgr_color
                    })

        # 3. Painter's Algorithm: Ordenar de más lejos a más cerca
        objects_to_draw.sort(key=lambda obj: obj['dist'], reverse=True)
        
        # 4. Dibujarlo todo en orden
        for obj in objects_to_draw:
            cv2.circle(frame, (obj['x'], self.height // 2), obj['radius'], obj['color'], -1)

        # 5. ¡Aplica la lente Fisheye distorsionando la imagen entera antes de entregarla!
        frame = cv2.remap(frame, self.map_x, self.map_y, cv2.INTER_LINEAR, 
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
                          
        return frame
