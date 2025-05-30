class SecondStrategy:
    def calculate(
        self, start_timestamp: int, repeat_for: int, repeated_for: int, unlimited: bool
    ) -> int | None:
        if not unlimited and repeated_for >= repeat_for:
            return None
        else:
            return start_timestamp + repeated_for + 1
