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
        
    def _project_entity(self, observer, entity, color_bgr, shape_type="circle", base_size=12.0):
        """Calcula las coordenadas y métricas visuales para una entidad."""
        if shape_type == "rect" and hasattr(entity, 'width') and hasattr(entity, 'height'):
            # En la vista 2D del Motor, la altura representa el ancho desde la perspectiva interior.
            ex = entity.x + entity.width / 2.0
            ey = entity.y + entity.height / 2.0
        else:
            ex = entity.x
            ey = entity.y

        dx = ex - observer.x
        dy = ey - observer.y
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        diff_angle = (angle - observer.rangle + math.pi) % (2 * math.pi) - math.pi
        
        if abs(diff_angle) < (self.fov / 2) + math.radians(20):
            pixels_per_radian = self.width / self.fov
            img_x = int(self.width / 2 + diff_angle * pixels_per_radian)
            dist_safe = max(1.0, dist)
            
            # Proporción física para perspectiva 2.5D
            r_calc = (base_size / 12.0) * 1500 / dist_safe
            screen_size = int(min(400.0, r_calc))
            
            # Altura tridimensional teórica (Z) de las entidades
            z_phys = getattr(entity, 'z_height', base_size)
            h_calc = (z_phys / 12.0) * 1500 / dist_safe
            screen_h_size = int(min(400.0, h_calc))
            
            if screen_size > 0:
                return {
                    'dist': dist,
                    'x': img_x,
                    'size': screen_size,
                    'h_size': screen_h_size,
                    'color': color_bgr,
                    'shape': shape_type
                }
        return None

    def render(self, observer, state):
        """
        Calcula una imagen RGB representando lo que el agente ve físicamente.
        Soporta Polimorfismo Geométrico: círculos se dibujan esféricos y porterías rectangulares como muros.
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
        
        if state.ball:
            proj = self._project_entity(observer, state.ball, (0, 100, 255), "circle", state.ball.radius)
            if proj: objects_to_draw.append(proj)
            
        for r in state.robots:
            v = 0.15
            color_bgr = (r.team_color[2] * v, r.team_color[1] * v, r.team_color[0] * v)
            proj = self._project_entity(observer, r, color_bgr, "rect", r.z_height)
            if proj: objects_to_draw.append(proj)
            
        for g in state.goals:
            color_bgr = (g.team_color[2], g.team_color[1], g.team_color[0])
            # La altura (height) de la portería en 2D representa su ancho en la perspectiva 3D
            proj = self._project_entity(observer, g, color_bgr, "rect", g.height)
            if proj: objects_to_draw.append(proj)

        # 4. Painter's Algorithm: Ordenar de más lejos a más cerca
        objects_to_draw.sort(key=lambda obj: obj['dist'], reverse=True)
        
        # 5. Dibujar en orden de fondo a frente
        for obj in objects_to_draw:
            if obj['shape'] == "circle":
                cv2.circle(frame, (obj['x'], self.height // 2), obj['size'], obj['color'], -1)
            elif obj['shape'] == "rect":
                # Prisma/Muro en 2.5D
                w = obj['size']
                h = obj['h_size']
                
                # Limitar el tamaño para que no desborde inmensamente
                w = min(w, self.width * 2)
                h = min(h, self.height * 2)

                top_left = (obj['x'] - w // 2, self.height // 2 - h // 2)
                bottom_right = (obj['x'] + w // 2, self.height // 2 + h // 2)
                cv2.rectangle(frame, top_left, bottom_right, obj['color'], -1)

        # 6. Aplica la lente Fisheye distorsionando la imagen entera antes de entregarla
        frame = cv2.remap(frame, self.map_x, self.map_y, cv2.INTER_LINEAR, 
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
                          
        return frame
