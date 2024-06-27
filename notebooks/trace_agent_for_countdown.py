"""
What is learning for countdown...?

When we "learn" to search...to backtrack.

We need to go "beyond" programs. The programs from opto.trace can be context-specific, myopically optimal.
This means, learning, optimizer, might need to go well beyond.
"""

from countdown import CountDown
from opto.trace.bundle import bundle, trace_class
from opto.trace.nodes import node

countdown = CountDown(50, 4)
target = 32
nums, solution = countdown.generate(target)


@trace_class
class DeepAgent:
    @bundle("[solve_countdown] Given 4 numbers, apply + - * / to them to get target.", trainable=True)
    def solve_countdown(self, numbers, target: int):
        """
        Numbers: [26, 33, 4, 39]
        Target: 39
        Solution: ['39-33=6', '26*6=156', '156/4=39']

        Numbers: [21, 30, 25, 5]
        Target: 32
        Solution: ['30+25=55', '55/5=11', '21+11=32']

        Need to figure out what set of operations to apply
        """
        solution = []
        return solution


def user_fb_to_verify_solution(numbers, target, solution):
    try:
        rew = countdown.verify_solution(numbers, target, solution)
        return "Solution verified. Success", int(rew)
    except Exception as e:
        return str(e), 0
