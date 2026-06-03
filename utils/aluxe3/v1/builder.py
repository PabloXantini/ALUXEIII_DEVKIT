from __future__ import annotations
from fsm import HState, Machine, MachineBuilder
from utils.aluxe3.v1.states import (
    Search, 
    LookBall, 
    GotoBall, 
    LookForShot,
    GotoEnemyGoal,
    RedirectBall,
    AvoidAllyGoal,
    SideMoveForShot,
    Backwards
)
from utils.aluxe3.v1.rules import (
    BallDetected,
    BallLost,
    BallOffCenter,
    BallCenteredAway,
    BallCenteredClose,
    BallEnemyGoalAligned,
    BallAllyGoalAligned,
    NotBallEnemyGoalAligned,
    NotBallAllyGoalAligned,
    NoGoals,
    BallCentered,
    BallClose
)

class Aluxe3v1aBuilder(MachineBuilder):
    def build_machine(self, debug: bool = False, sandbox: bool = False, name: str = "aluxe", team_color: str = "blue") -> tuple[Machine, object]:
        if sandbox:
            from sandbox.sim_context import SimContext
            ctx = SimContext(debug=debug, name=name, team_color=team_color)
        else:
            from utils.aluxe3.context import RobotContext
            ctx = RobotContext(debug=debug, name=name, team_color=team_color)

        # ── Instanciar estados ────────────────────────────────────────────────────
        search = Search()
        l_ball = LookBall()
        g_ball = GotoBall()
        l_shot  = LookForShot()
        g_goal = GotoEnemyGoal()
        r_ball = RedirectBall()
        a_goal = AvoidAllyGoal()

        # ── Máquina (estado inicial: búsqueda) ────────────────────────────────────
        machine = Machine(search)

        # ── Transiciones ──────────────────────────────────────────────────────────
        #  Desde       → Hacia        Cuando
        # SEARCH
        machine.add(search, l_ball, BallDetected())
        # LOOKBALL
        machine.add(l_ball, g_ball, BallCenteredAway())
        machine.add(l_ball, search, BallLost())
        machine.add(l_ball, l_shot, BallCenteredClose())
        # GOTOBALL
        machine.add(g_ball, l_ball, BallOffCenter())
        machine.add(g_ball, search, BallLost())
        machine.add(g_ball, l_shot, BallCenteredClose())
        # WAITFORSHOT
        machine.add(l_shot, g_goal, BallEnemyGoalAligned())
        machine.add(l_shot, l_ball, NotBallEnemyGoalAligned())
        machine.add(l_shot, a_goal, NotBallAllyGoalAligned())
        machine.add(l_shot, a_goal, BallAllyGoalAligned())
        machine.add(l_shot, r_ball, NoGoals())
        machine.add(l_shot, g_goal, BallCenteredClose())
        machine.add(l_shot, l_ball, BallOffCenter())
        machine.add(l_shot, search, BallLost())
        # GOTOGOAL
        machine.add(g_goal, l_ball, BallOffCenter())
        machine.add(g_goal, search, BallLost())
        # REDIRECTBALL
        machine.add(r_ball, l_ball, BallOffCenter())
        machine.add(r_ball, search, BallLost())
        # AVOIDALLYGOAL
        machine.add(a_goal, l_ball, BallOffCenter())
        machine.add(a_goal, search, BallLost())

        return machine, ctx

class Aluxe3v1bBuilder(MachineBuilder):
    def build_machine(self, debug: bool = False, sandbox: bool = False, name: str = "aluxe", team_color: str = "blue") -> tuple[Machine, object]:
        if sandbox:
            from sandbox.sim_context import SimContext
            ctx = SimContext(debug=debug, name=name, team_color=team_color)
        else:
            from utils.aluxe3.context import RobotContext
            ctx = RobotContext(debug=debug, name=name, team_color=team_color)

        # ===== Instanciar máquinas y estados ===== #
        
        # Máquina Final
        search = Search()
        l_ball = LookBall()
        g_ball = GotoBall()
        machine = Machine(search)
        # --- Estado-Maquinas envolventes
        # MOVEFORSHOT
        ms_g_ball = GotoBall()
        ms_sm_shot = SideMoveForShot()
        ms_back = Backwards()
        machine_m_shot = Machine(ms_sm_shot)
        machine_m_shot.add(ms_sm_shot, ms_g_ball, BallCentered())
        machine_m_shot.add(ms_g_ball, ms_back, BallOffCenter())
        machine_m_shot.add(ms_back, ms_sm_shot, BallDetected())

        m_shot = HState(machine_m_shot)

        # Tabla de estados
        #  Desde       → Hacia        Cuando
        # SEARCH
        machine.add(search, l_ball, BallDetected())
        # LOOKBALL
        machine.add(l_ball, g_ball, BallCenteredAway())
        machine.add(l_ball, search, BallLost())
        machine.add(l_ball, m_shot, BallCenteredClose())
        # GOTOBALL
        machine.add(g_ball, search, BallLost())
        machine.add(g_ball, m_shot, BallCenteredClose())

        # BACKWARDS

        """
        # WAITFORSHOT
        machine.add(l_shot, g_goal, BallEnemyGoalAligned())
        machine.add(l_shot, l_ball, NotBallEnemyGoalAligned())
        machine.add(l_shot, a_goal, NotBallAllyGoalAligned())
        machine.add(l_shot, a_goal, BallAllyGoalAligned())
        machine.add(l_shot, r_ball, NoGoals())
        machine.add(l_shot, g_goal, BallClose())
        machine.add(l_shot, l_ball, BallOffCenter())
        machine.add(l_shot, search, BallLost())
        # GOTOGOAL
        machine.add(g_goal, l_ball, BallOffCenter())
        machine.add(g_goal, search, BallLost())
        # REDIRECTBALL
        machine.add(r_ball, l_ball, BallOffCenter())
        machine.add(r_ball, search, BallLost())
        # AVOIDALLYGOAL
        machine.add(a_goal, l_ball, BallOffCenter())
        machine.add(a_goal, search, BallLost())
        """
        return machine, ctx