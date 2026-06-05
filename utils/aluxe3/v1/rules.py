from __future__ import annotations

from fsm import Rule
from utils.aluxe3.context import (
    RobotContext, 
    CENTER_TOLERANCE, 
    BALL_RADIUS_CLOSE_MIN
)

class BallLost(Rule):
    """Pelota dejó de verse."""
    def applies(self, ctx: RobotContext) -> bool:
        return not ctx.info['ball']['detected']

class BallDetected(Rule):
    """Pelota visible por primera vez (o de vuelta)."""
    def applies(self, ctx: RobotContext) -> bool:
        return ctx.info['ball']['detected']

class BallOffCenter(Rule):
    """Pelota visible pero no en medio."""
    def applies(self, ctx: RobotContext) -> bool:
        ball = ctx.info['ball']
        return (ball['detected']
                and ball['offset_x'] is not None
                and abs(ball['offset_x']) > CENTER_TOLERANCE)

class BallCenteredAway(Rule):
    """Pelota en medio pero lejos."""
    def applies(self, ctx: RobotContext) -> bool:
        ball = ctx.info['ball']
        return (ball['detected']
                and ball['offset_x'] is not None
                and abs(ball['offset_x']) <= CENTER_TOLERANCE
                and ball['radius'] < BALL_RADIUS_CLOSE_MIN)

class BallCenteredClose(Rule):
    """Pelota centrada Y suficientemente cerca para detenerse/chutar."""
    def applies(self, ctx: RobotContext) -> bool:
        ball = ctx.info['ball']
        return (ball['detected']
                and ball['offset_x'] is not None
                and abs(ball['offset_x']) <= CENTER_TOLERANCE
                and ball['radius'] >= BALL_RADIUS_CLOSE_MIN)

class BallEnemyGoalAligned(Rule):
    """Pelota esta alineada a la porteria"""
    def applies(self, ctx: RobotContext) -> bool:
        ball = ctx.info['ball']
        enemy_goal = ctx.info['enemy_goal']
        return (ball['detected']
                and enemy_goal['detected']
                and enemy_goal['offset_x'] is not None
                and abs(ball['offset_x']) <= CENTER_TOLERANCE
                and abs(enemy_goal['offset_x']) <= CENTER_TOLERANCE)

class BallAllyGoalAligned(Rule):
    def applies(self, ctx: RobotContext) -> bool:
        ball = ctx.info['ball']
        ally_goal = ctx.info['ally_goal']
        return (ball['detected']
                and ally_goal['detected']
                and ally_goal['offset_x'] is not None
                and abs(ball['offset_x']) <= CENTER_TOLERANCE
                and abs(ally_goal['offset_x']) <= CENTER_TOLERANCE)
    
class NotBallEnemyGoalAligned(Rule):
    """Pelota esta alineada a la porteria"""
    def applies(self, ctx: RobotContext) -> bool:
        ball = ctx.info['ball']
        enemy_goal = ctx.info['enemy_goal']
        return (ball['detected']
                and enemy_goal['detected']
                and enemy_goal['offset_x'] is not None
                and (abs(ball['offset_x']) > CENTER_TOLERANCE
                or abs(enemy_goal['offset_x']) > CENTER_TOLERANCE))

class NotBallAllyGoalAligned(Rule):
    def applies(self, ctx: RobotContext) -> bool:
        ball = ctx.info['ball']
        ally_goal = ctx.info['ally_goal']
        return (ball['detected']
                and ally_goal['detected']
                and ally_goal['offset_x'] is not None
                and (abs(ball['offset_x']) > CENTER_TOLERANCE
                or abs(ally_goal['offset_x']) > CENTER_TOLERANCE))

class NoGoals(Rule):
    def applies(self, ctx: RobotContext) -> bool:
        return not ctx.info['ally_goal']['detected'] and not ctx.info['enemy_goal']['detected']

# the goal is held how much time the robot has been in state gotoenemygoal
class TooMuchTimeToGoal(Rule):
    def applies(self, ctx: RobotContext) -> bool:
        return ctx.info['time'] > 10

# rules for Aluxe3v1b
class BallCentered(Rule):
    def applies(self, ctx: RobotContext) -> bool:
        ball = ctx.info['ball']
        return (ball['detected']
                and ball['offset_x'] is not None
                and abs(ball['offset_x']) <= CENTER_TOLERANCE)

class BallClose(Rule):
    def applies(self, ctx: RobotContext) -> bool:
        return ctx.info['ball']['radius'] >= BALL_RADIUS_CLOSE_MIN