class Box:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def x1(self) -> int:
        return int(self.x - self.w / 2)

    @property
    def y1(self) -> int:
        return int(self.y - self.h / 2)

    @property
    def x2(self) -> int:
        return int(self.x + self.w / 2)

    @property
    def y2(self) -> int:
        return int(self.y + self.h / 2)

    def __repr__(self):
        return f"Box(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def distance_to(self, other: 'Box') -> float:
        dx = max(0, max(self.x1, other.x1) - min(self.x2, other.x2))
        dy = max(0, max(self.y1, other.y1) - min(self.y2, other.y2))
        return (dx ** 2 + dy ** 2) ** 0.5

    def intersects_with(self, other: 'Box') -> bool:
        return self.distance_to(other) == 0

    def adjacent_to(self, other: 'Box', threshold_multiplier: float = 0.1) -> bool:
        dist = self.distance_to(other)
        threshold = (self.w + self.h + other.w + other.h) / 4 * threshold_multiplier
        return dist <= threshold

    def merge(self, other: 'Box') -> 'Box':
        x1 = min(self.x - self.w / 2, other.x - other.w / 2)
        y1 = min(self.y - self.h / 2, other.y - other.h / 2)
        x2 = max(self.x + self.w / 2, other.x + other.w / 2)
        y2 = max(self.y + self.h / 2, other.y + other.h / 2)
        return Box(int((x1 + x2) / 2), int((y1 + y2) / 2), int(x2 - x1), int(y2 - y1))

    def to_box_float(self, image_width: int, image_height: int) -> 'BoxFloat':
        return BoxFloat(
            x=self.x / image_width,
            y=self.y / image_height,
            w=self.w / image_width,
            h=self.h / image_height
        )


class BoxFloat:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return f"BoxFloat(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def to_box(self, image_width: int, image_height: int) -> 'Box':
        return Box(
            x=int(self.x * image_width),
            y=int(self.y * image_height),
            w=int(self.w * image_width),
            h=int(self.h * image_height)
        )
