from __future__ import annotations

from fsm import Rule
from utils.r_context import RobotContext, FRANJA_CENTRAL, RADIO_OBJETIVO


class BallLostRule(Rule):
    """Pelota dejó de verse."""
    def applies(self, ctx: RobotContext) -> bool:
        return not ctx.ball_detected


class BallDetectedRule(Rule):
    """Pelota visible por primera vez (o de vuelta)."""
    def applies(self, ctx: RobotContext) -> bool:
        return ctx.ball_detected


class BallOffCenterRule(Rule):
    """Pelota visible pero fuera de la franja central."""
    def applies(self, ctx: RobotContext) -> bool:
        return (ctx.ball_detected
                and ctx.offset_x is not None
                and abs(ctx.offset_x) > FRANJA_CENTRAL)


class BallCenteredRule(Rule):
    """Pelota dentro de la franja central y todavía lejos."""
    def applies(self, ctx: RobotContext) -> bool:
        return (ctx.ball_detected
                and ctx.offset_x is not None
                and abs(ctx.offset_x) <= FRANJA_CENTRAL
                and ctx.radius < RADIO_OBJETIVO)


class BallCloseRule(Rule):
    """Pelota centrada Y suficientemente cerca para detenerse/chutar."""
    def applies(self, ctx: RobotContext) -> bool:
        return (ctx.ball_detected
                and ctx.offset_x is not None
                and abs(ctx.offset_x) <= FRANJA_CENTRAL
                and ctx.radius >= RADIO_OBJETIVO)