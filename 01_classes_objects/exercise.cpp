// ============================================================
// EXERCISE 1: Classes & Objects
// ============================================================
// Build a class called `Rectangle`. main() is already written for
// you below (driver code) — don't change it. Just fill in the class
// so the program compiles and produces sensible output.
//
// REQUIREMENTS:
//   1. Private data members:
//        - double width
//        - double height
//
//   2. Public methods:
//        - void  setDimensions(double w, double h)
//              stores w and h. If either is negative, store 0
//              for that one instead.
//        - double area() const           -> returns width * height
//        - double perimeter() const      -> returns 2 * (width + height)
//        - bool   isSquare() const       -> true if width == height
//        - void   print() const          -> prints:  "WxH  area=A  perim=P"
//              example line:  "3x4  area=12  perim=14"
//
// RULES:
//   - width and height must stay private.
//   - area(), perimeter(), isSquare(), print() must be marked const.
//
// Compile:
//   g++ -std=c++14 -Wall exercise.cpp -o exercise.exe ; ./exercise.exe
// ============================================================

#include <iostream>
using namespace std;

class Rectangle {
  private:
    double width;
    double height;
  public:
    void setDimensions(double w,double h){
      width = w > 0 ? w : 0;
      height = h > 0 ? h : 0;
    }

    double area() const {
      return width * height;
    }

    double perimeter() const {
      return 2 * (width + height);
    }

    bool isSquare() const {
      return height == width;
    }

    void print() const {
      cout << width << "x" << height << " area =" << area() << " perim =" << perimeter() << "\n";
    }
};

// ------------------ DRIVER CODE (do not edit) ------------------
int main() {
    Rectangle r1;
    r1.setDimensions(3, 4);
    r1.print();                 // expect: 3x4  area=12  perim=14

    Rectangle r2;
    r2.setDimensions(5, 5);
    r2.print();                 // expect: 5x5  area=25  perim=20
    std::cout << "r2 is square? " << (r2.isSquare() ? "yes" : "no") << "\n";

    Rectangle r3;
    r3.setDimensions(-2, 6);    // negative width -> should become 0
    r3.print();                 // expect: 0x6  area=0  perim=12

    std::cout << "r1 is square? " << (r1.isSquare() ? "yes" : "no") << "\n";

    return 0;
}
