"""
Code from:
https://github.com/kanishkg/stream-of-search/blob/main/src/countdown.py
"""

'''
CountDown class for generating questions and trees
'''
import random
import itertools

def combine_nums(a, b):
    # Implicitly makes assumptions about the order of operations and valid operations
    a = int(a)
    b = int(b)
    possible = [[a+b, f"{a}+{b}={a+b}"], [a*b, f"{a}*{b}={a*b}"]]
    if a <= b:
        possible.append([b-a, f"{b}-{a}={b-a}"])
        if a != 0 and b % a == 0:
            possible.append([b//a, f"{b}/{a}={round(b//a,0)}"])
    else:
        possible.append([a-b, f"{a}-{b}={a-b}"])
        if b != 0 and a % b == 0:
            possible.append([a//b, f"{a}/{b}={round(a//b,0)}"])
    return possible

class CountDown(object):
    def __init__(self, max_target=24, start_size=4, min_target=10):
        self.max_target = max_target
        self.min_target = min_target
        self.start_size = start_size

    def generate(self, target):
        if target > self.max_target:
            raise ValueError("Target cannot be greater than max target")
        if target < self.min_target:
            raise ValueError("Target cannot be less than min target")

        found = False
        while not found:
            # nums in question can go up to max target
            nums = [random.randint(1, self.max_target - 1) for _ in range(self.start_size)]
            solution = self.search(target, nums)
            if solution is not None:
                found = True
        return nums, solution

    def search(self, target, nums, operations=[]):
        # Navigate the entire solution tree, implemented with DFS
        if len(nums) == 1:
            if nums[0] == target:
                return operations
            else:
                return None

        for i, j in itertools.combinations(range(len(nums)), 2):
            num1, num2 = nums[i], nums[j]
            remaining_nums = [nums[k] for k in range(len(nums)) if k != i and k != j]
            for result, operation in combine_nums(num1, num2):
                new_nums = remaining_nums + [result]
                new_operations = operations + [operation]
                solution = self.search(target, new_nums, new_operations)
                if solution is not None:
                    return solution
        return None

    def check_i_j(self, i, nums, intermediate_results):
        assert i in nums + intermediate_results, f"{i} not a number from the original set, and not an intermediate result either."
        if i in nums:
            return True
        else:
            return False

    def verify_solution(self, nums, target, solution):
        # Verify that the solution is correct
        intermediate_results = []
        check_nums = nums.copy()
        for step in solution:
            for op in ["+", "-", "*", "/"]:
                if op in step:
                    i, j = step.split("=")[0].split(op)
                    i, j = int(i), int(j)
                    i_is_orig_num = self.check_i_j(i, nums, intermediate_results)
                    j_is_orig_num = self.check_i_j(j, nums, intermediate_results)
                    if i_is_orig_num and i in check_nums:
                        check_nums.remove(i)
                    if j_is_orig_num and j in check_nums:
                        check_nums.remove(j)
                    result = eval(step.split("=")[0])
                    output_result = step.split("=")[1]
                    assert result == int(output_result), f"solution's printed result {output_result} is wrong, {i}{op}{j}={result}"
                    intermediate_results.append(result)
                    break

        assert len(check_nums) == 0, f"Not all original numbers {nums} are used, remaining {check_nums}"
        assert result == target, f"Final result {result} is not equal to target {target}"
        return True




if __name__ == '__main__':
    # any LLM can write a search to solve this problem
    # but an LLM agent can use some memory? to have some heuristics or premonitions
    # to go beyond.
    countdown = CountDown(50, 4)
    target = 32
    nums, solution = countdown.generate(target)
    print(f"Numbers: {nums}")
    print(f"Solution: {solution}")

    countdown.verify_solution(nums, target, solution)