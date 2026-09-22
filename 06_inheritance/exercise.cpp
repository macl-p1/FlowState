// ============================================================
// EXERCISE 6: Inheritance + Polymorphism
// ============================================================
// Build a small shape hierarchy.
//
// REQUIREMENTS:
//
//   class Shape (base):
//     - protected: string color
//     - public: Shape(const string& c)
//     - public: virtual void draw() const
//           prints: "Drawing a <color> shape"
//     - public: virtual ~Shape() {}
//
//   class Circle : public Shape:
//     - private: double radius
//     - public: Circle(const string& c, double r)
//           member-init-list: Shape(c), radius(r)
//     - public: void draw() const override
//           prints: "Drawing a <color> circle, radius <r>"
//     - public: double area() const
//           returns 3.14159 * radius * radius
//
//   class Rectangle : public Shape:
//     - private: double width, height
//     - public: Rectangle(const string& c, double w, double h)
//     - public: void draw() const override
//           prints: "Drawing a <color> rectangle, <w>x<h>"
//     - public: double area() const
//           returns width * height
//
//   Polymorphic function (provided in driver code):
//     void printArea(const Shape& s)
//       calls s.draw() then prints s.area()
//       // Draw first, then the area on the next line
//
//   All prints end with "\n".
//
// RULES:
//   - Shape must be defined BEFORE Circle and Rectangle.
//   - Both classes override draw() — this is runtime polymorphism.
//   - area() is NOT in the base class; it is a "derived-only" method.
//     Call it only through the concrete type (Circle / Rectangle).
//
// Compile:
//   g++ -std=c++14 -Wall exercise.cpp -o exercise.exe ; ./exercise.exe
// ============================================================

#include <iostream>
#include <string>
using namespace std;

// ==================== YOUR CODE HERE ====================

// class Shape { ... };

// class Circle : public Shape { ... };

// class Rectangle : public Shape { ... };

// ==================== DRIVER CODE (do not edit) ====================

int main() {
    Circle   c("red", 2.5);
    Rectangle r("blue", 4.0, 3.0);

    // Polymorphic draw — Shape& calls the right override
    const Shape& s1 = c;
    const Shape& s2 = r;

    s1.draw();
    // expect: Drawing a red circle, radius 2.5

    s2.draw();
    // expect: Drawing a blue rectangle, 4x3

    // area() is derived-only, so cast to concrete type
    cout << "Circle area: "   << static_cast<const Circle&>(s1).area()    << "\n";   // ~19.63
    cout << "Rectangle area: " << static_cast<const Rectangle&>(s2).area() << "\n";   // 12

    return 0;
}
