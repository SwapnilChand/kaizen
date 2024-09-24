import math
from typing import List, Optional

class Shape:
    def __init__(self, name: str):
        self.name = name

    def area(self) -> float:
        raise NotImplementedError("Subclass must implement abstract method")

    def perimeter(self) -> float:
        raise NotImplementedError("Subclass must implement abstract method")

class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("Circle")
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        super().__init__("Rectangle")
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

class ShapeFactory:
    @staticmethod
    def create_circle(radius: float) -> Circle:
        return Circle(radius)

    @staticmethod
    def create_rectangle(width: float, height: float) -> Rectangle:
        return Rectangle(width, height)

class ShapeAnalyzer:
    def __init__(self, shapes: List[Shape]):
        self.shapes = shapes

    def total_area(self) -> float:
        return sum(shape.area() for shape in self.shapes)

    def total_perimeter(self) -> float:
        return sum(shape.perimeter() for shape in self.shapes)

    def largest_shape(self) -> Optional[Shape]:
        if not self.shapes:
            return None
        return max(self.shapes, key=lambda shape: shape.area())

def create_sample_shapes() -> List[Shape]:
    factory = ShapeFactory()
    return [
        factory.create_circle(5),
        factory.create_rectangle(3, 4),
        factory.create_circle(2.5),
        factory.create_rectangle(6, 2)
    ]

def main():
    shapes = create_sample_shapes()
    analyzer = ShapeAnalyzer(shapes)
    
    print(f"Total area: {analyzer.total_area():.2f}")
    print(f"Total perimeter: {analyzer.total_perimeter():.2f}")
    
    largest = analyzer.largest_shape()
    if largest:
        print(f"Largest shape: {largest.name} with area {largest.area():.2f}")

if __name__ == "__main__":
    main()