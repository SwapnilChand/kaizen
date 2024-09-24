package kaizen.visualizer.sample;

public class Car {
    private int speed; // Instance variable to hold the speed of the car

    // Constructor to initialize the speed
    public Car() {
        this.speed = 0; // Set initial speed to 0
    }

    // Method to accelerate the car
    public void accelerate() {
        speed++; // Increment speed
        System.out.println("Accelerating: Current speed is " + speed);
    }

    // Method to brake the car
    public void brake() {
        speed = 0; // Set speed to 0
        System.out.println("Braking: Current speed is " + speed);
    }

    public int getSpeed() {
        return speed; // Getter method for speed
    }

    public static void main(String[] args) {
        Car myCar = new Car(); // Create an instance of Car

        myCar.accelerate(); // Call accelerate method
        myCar.accelerate(); // Call accelerate method again
        myCar.brake();      // Call brake method
    }
}