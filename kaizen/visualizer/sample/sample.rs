struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn new(width: u32, height: u32) -> Rectangle {
        Rectangle { width, height }
    }
}

fn display_rectangle(rect: &Rectangle) {
    println!("Rectangle width: {}, height: {}", rect.width, rect.height);
    println!("Area of rectangle: {}", rect.area());
}

fn main() {
    let rect = Rectangle::new(10, 5);

    display_rectangle(&rect);
}