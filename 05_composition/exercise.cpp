// ============================================================
// EXERCISE 5: Composition ("has-a")
// ============================================================
// Build TWO classes: `Engine` and `Car`. Car HAS AN Engine (composition).
//
// REQUIREMENTS:
//
//   class Engine:
//     - private: int horsepower
//     - public: Engine(int hp)                 member-init-list, no print
//     - public: int getHorsepower() const      returns horsepower
//     - public: void start() const             prints: "Engine (<hp>hp) started"
//
//   class Car:
//     - private: string model
//     - private: Engine engine                 <-- composition
//     - public: Car(const string& m, int hp)
//           member-init-list for BOTH model and engine (engine(hp))
//     - public: void drive() const
//           prints: "<model> is moving"
//           then calls engine.start()
//     - public: int getPower() const
//           returns engine.getHorsepower()   (Car delegates to its Engine)
//
//   All prints end with "\n".
//
// RULES:
//   - Engine must be defined BEFORE Car (Car contains an Engine, so
//     the compiler needs to see Engine's full definition first).
//   - horsepower, model, engine must all stay private.
//
// Compile:
//   g++ -std=c++14 -Wall exercise.cpp -o exercise.exe ; ./exercise.exe
// ============================================================

#include <iostream>
#include <string>
using namespace std;

class Engine{
  
}
// TODO: class Car

// ------------------ DRIVER CODE (do not edit) ------------------
int main() {
    Car c1("Tesla Model 3", 480);
    Car c2("Toyota Corolla", 140);

    c1.drive();
    // expect:
    // Tesla Model 3 is moving
    // Engine (480hp) started

    c2.drive();
    // expect:
    // Toyota Corolla is moving
    // Engine (140hp) started

    cout << "c1 power: " << c1.getPower() << "\n";   // 480
    cout << "c2 power: " << c2.getPower() << "\n";   // 140

    return 0;
}
