class JMonthStrategy:
    def calculate(
        self, start_timestamp: int, repeat_for: int, repeated_for: int, unlimited: bool
    ) -> int | None:
        raise NotImplemented
