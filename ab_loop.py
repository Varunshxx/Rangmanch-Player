class ABLoop:
    """
    Logic for A-B looping functionality.
    """
    def __init__(self, player):
        self.player = player
        self.a = None
        self.b = None

    def toggle(self):
        current_time = self.player.get_property('time-pos')
        if current_time is None:
            return

        if self.a is None:
            # Set A
            self.a = current_time
            self.player.set_property('ab-loop-a', self.a)
            return "A"
        elif self.b is None:
            # Set B
            self.b = current_time
            # Ensure B is after A
            if self.b < self.a:
                self.b, self.a = self.a, self.b
            
            self.player.set_property('ab-loop-a', self.a)
            self.player.set_property('ab-loop-b', self.b)
            return "B"
        else:
            # Clear
            self.clear()
            return "OFF"

    def clear(self):
        self.a = None
        self.b = None
        self.player.set_property('ab-loop-a', 'no')
        self.player.set_property('ab-loop-b', 'no')
