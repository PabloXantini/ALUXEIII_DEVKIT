from __future__ import annotations

from fsm import Rule
from utils.r_context import RobotContext, FRANJA_CENTRAL, RADIO_OBJETIVO


class BallLost(Rule):
    """Pelota dejó de verse."""
    def applies(self, ctx: RobotContext) -> bool:
        return not ctx.ball_detected

class BallDetected(Rule):
    """Pelota visible por primera vez (o de vuelta)."""
    def applies(self, ctx: RobotContext) -> bool:
        return ctx.ball_detected

class BallOffCenter(Rule):
    """Pelota visible pero no en medio."""
    def applies(self, ctx: RobotContext) -> bool:
        return (ctx.ball_detected
                and ctx.offset_x is not None
                and abs(ctx.offset_x) > FRANJA_CENTRAL)

class BallCentered(Rule):
    """Pelota en medio pero lejos."""
    def applies(self, ctx: RobotContext) -> bool:
        return (ctx.ball_detected
                and ctx.offset_x is not None
                and abs(ctx.offset_x) <= FRANJA_CENTRAL
                and ctx.radius < RADIO_OBJETIVO)

class BallClose(Rule):
    """Pelota centrada Y suficientemente cerca para detenerse/chutar."""
    def applies(self, ctx: RobotContext) -> bool:
        return (ctx.ball_detected
                and ctx.offset_x is not None
                and abs(ctx.offset_x) <= FRANJA_CENTRAL
                and ctx.radius >= RADIO_OBJETIVO)

# Revisar
class BallGoalAligned(Rule):
    """Pelota esta alineada a la porteria"""
    def applies(self, ctx: RobotContext) -> bool:
        return (ctx.ball_detected
                and ctx.enemy_goal_detected
                and ctx.enemy_goal_offset_x is not None
                and abs(ctx.offset_x) <= FRANJA_CENTRAL
                and abs(ctx.enemy_goal_offset_x) <= FRANJA_CENTRAL)
    
class NotBallGoalAligned(Rule):
    """Pelota esta alineada a la porteria"""
    def applies(self, ctx: RobotContext) -> bool:
        return (ctx.ball_detected
                and ctx.enemy_goal_detected
                and ctx.enemy_goal_offset_x is not None
                and abs(ctx.offset_x) > FRANJA_CENTRAL
                and abs(ctx.enemy_goal_offset_x) > FRANJA_CENTRAL)