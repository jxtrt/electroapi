"""Scheduler module for optimizing power usage based on electricity prices."""

from typing import List, Dict, Tuple, Union

import pandas as pd


class Scheduler:
    """Scheduler class for optimizing power usage."""

    def __init__(self, data: pd.DataFrame):
        # store data as dict (hour -> price)
        self.original_data = data
        self.data: Dict[Tuple[int, int]] = {
            row["hour"]: row["price"] for _, row in data.iterrows()
        }

    def n_blocks(self, hours: List[Tuple[int]]) -> int:
        """Calculate the number of consecutive hour blocks in a list of hours."""
        if not hours:
            return 0
        hours = sorted([h[0] for h in hours])
        _n_blocks = 1
        for i in range(len(hours) - 1):
            if hours[i] != hours[i + 1] - 1:
                _n_blocks += 1
        return _n_blocks

    def schedule(
        self, power_on_hours: int, max_blocks: Union[int, None] = None
    ) -> pd.DataFrame:
        """
        dp approach:
            - return a combination of exactly power_on_hours hours,
                with the lowest possible price
            - if max_blocks is set (>0), return a combination with at
                most max_blocks consecutive hour blocks
                even if that means a higher price
        """
        data = list(self.data.items())
        n = len(self.data)
        inf = float("inf")

        if max_blocks is None or max_blocks < 0:
            max_blocks = power_on_hours

        # dp[i][k][b][in_block]
        # 0 <= i <= 23
        # k = number of chosen hours
        # b = number of formed blocks
        # in_block = 0/1 if we are in a block
        dp = [
            [
                [[inf] * 2 for _ in range(max_blocks + 2)]
                for _ in range(power_on_hours + 2)
            ]
            for _ in range(n + 1)
        ]

        parent = [
            [
                [[None] * 2 for _ in range(max_blocks + 2)]
                for _ in range(power_on_hours + 2)
            ]
            for _ in range(n + 1)
        ]

        dp[0][0][0][0] = 0

        for i in range(1, n + 1):
            _, price = data[i - 1]
            for k in range(power_on_hours + 1):
                for b in range(max_blocks + 1):
                    for in_block in (0, 1):
                        cost = dp[i - 1][k][b][in_block]
                        if cost == inf:
                            continue

                        # carry the value forward (not taking this hour)
                        if cost < dp[i][k][b][0]:
                            dp[i][k][b][0] = cost
                            parent[i][k][b][0] = (i - 1, k, b, in_block, False)

                        # take this hour
                        if k < power_on_hours:
                            if in_block == 1:  # extend block
                                if cost + price < dp[i][k + 1][b][1]:
                                    dp[i][k + 1][b][1] = cost + price
                                    parent[i][k + 1][b][1] = (i - 1, k, b, 1, True)
                            else:  # start new block
                                if b + 1 <= max_blocks:
                                    if cost + price < dp[i][k + 1][b + 1][1]:
                                        dp[i][k + 1][b + 1][1] = cost + price
                                        parent[i][k + 1][b + 1][1] = (
                                            i - 1,
                                            k,
                                            b,
                                            0,
                                            True,
                                        )

        best_cost = inf
        best_state = None
        for b in range(max_blocks + 1):
            for in_block in (0, 1):
                cost = dp[n][power_on_hours][b][in_block]
                if cost < best_cost:
                    best_cost = cost
                    best_state = (n, power_on_hours, b, in_block)

        if best_cost == inf:
            return None

        chosen = []
        state = best_state
        while state and state[0] > 0:
            i, k, b, in_block = state
            prev = parent[i][k][b][in_block]
            if prev is None:
                break
            prev_i, prev_k, prev_b, prev_in_block, took = prev
            if took:
                chosen.append(data[i - 1][0])  # store the hour index
            state = (prev_i, prev_k, prev_b, prev_in_block)

        # add the data in original_data by merging
        result = self.original_data[self.original_data["hour"].isin(chosen)]
        result = result.sort_values(by="hour").reset_index(drop=True)

        return result
