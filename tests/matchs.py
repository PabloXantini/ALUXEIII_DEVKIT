from sandbox.game.entities import Robot
from robot.aluxe3.v1.builder import (
    Aluxe3v1aBuilder,
    Aluxe3v1bBuilder,
    Aluxe3v1TestBuilder
)

def prepare_2v2(debug: bool = False, sandbox: bool = False) -> list:
    a3v1a = Aluxe3v1aBuilder()
    a3v1b = Aluxe3v1bBuilder()
    robots = []
    if not sandbox:
        return robots
    import math
    from sandbox.game.entities import Robot

    team_colors = {
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0)
    }

    # TEAM BLUE
    # Robot 1 (Aliado - Azul) - Empieza en la izquierda mirando a la derecha
    brain1 = a3v1b.build_machine(debug=debug, sandbox=sandbox, name='Cuau', team_color="blue")
    robot1 = Robot(color=team_colors['blue'], brain=brain1)

    brain2 = a3v1b.build_machine(debug=debug, sandbox=sandbox, name='Sanchez', team_color="blue")
    robot2 = Robot(color=team_colors['blue'], brain=brain2)

    # TEAM YELLOW
    # Robot 2 (Enemigo - Amarillo) - Empieza en la derecha mirando a la izquierda
    brain3 = a3v1a.build_machine(debug=debug, sandbox=sandbox, name='Messi', team_color="yellow")
    robot3 = Robot(color=team_colors['yellow'], brain=brain3)

    brain4 = a3v1a.build_machine(debug=debug, sandbox=sandbox, name='Cristiano', team_color="yellow")
    robot4 = Robot(color=team_colors['yellow'], brain=brain4)

    robots = [robot1, robot2, robot3, robot4]
    return robots

def prepare_1v1(debug: bool = False, sandbox: bool = False) -> list:
    a3v1a = Aluxe3v1aBuilder()
    robots = []
    if not sandbox:
        return robots
    import math
    from sandbox.game.entities import Robot

    team_colors = {
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0)
    }

    # TEAM BLUE
    # Robot 1 (Aliado - Azul) - Empieza en la izquierda mirando a la derecha
    brain1 = a3v1a.build_machine(debug=debug, sandbox=sandbox, name='Cuau', team_color="blue")
    robot1 = Robot(kickoff_x=200, kickoff_y=300, color=team_colors['blue'], brain=brain1)

    # TEAM YELLOW
    # Robot 2 (Enemigo - Amarillo) - Empieza en la derecha mirando a la izquierda
    brain2 = a3v1a.build_machine(debug=debug, sandbox=sandbox, name='Messi', team_color="yellow")
    robot2 = Robot(kickoff_x=600, kickoff_y=300, color=team_colors['yellow'], brain=brain2)

    robots = [robot1, robot2]
    return robots

def prepare_solo(debug: bool = False, sandbox: bool = False) -> list:
    a3v1a = Aluxe3v1aBuilder()
    robots = []
    if not sandbox:
        return robots
    from sandbox.game.entities import Robot

    team_colors = {
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0)
    }
    # TEAM BLUE
    # Robot 1 (Aliado - Azul) - Empieza en la izquierda mirando a la derecha
    brain1 = a3v1a.build_machine(debug=debug, sandbox=sandbox, name='Cuau', team_color="blue")
    robot1 = Robot(kickoff_x=200, kickoff_y=300, color=team_colors['blue'], brain=brain1)

    robots = [robot1]
    return robots

def prepare_test(debug: bool = False, sandbox: bool = False) -> tuple:
    test = Aluxe3v1TestBuilder()
    machine, ctx = test.build_machine(debug=debug, sandbox=sandbox, name='TestBot', team_color="blue") 
    robots = []
    if sandbox:
        from sandbox.game.entities import Robot
        robot = Robot(kickoff_x=300, kickoff_y=200, color=(0, 0, 255), brain=(machine, ctx))
        robots = [robot]
    return machine, ctx, robots

