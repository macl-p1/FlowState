// ============================================================
// CONCEPT 5: Composition ("has-a")
// ============================================================
// Composition = building a class out of other classes as members.
// "A Car HAS AN Engine." This is different from inheritance
// ("is-a"), which comes next.
//
// Key point: the member object's constructor runs automatically
// when the containing object is constructed -- you initialize it
// via the member initializer list, same mechanism as any other member.
//
// Compile & run:
//   g++ -std=c++14 -Wall example.cpp -o example.exe ; ./example.exe
// ============================================================

#include <iostream>
#include <string>
using namespace std;

class Engine {
private:
    int horsepower;

public:
    Engine(int hp) : horsepower(hp) {
        cout << "  [Engine built: " << horsepower << "hp]\n";
    }

    void start() const {
        cout << "  Engine roars with " << horsepower << "hp\n";
    }
};

class Car {
private:
    string model;
    Engine engine;     // <-- Car HAS AN Engine. Composition.

public:
    // The Engine member is constructed via the initializer list,
    // BEFORE the Car constructor's body runs. Order is determined
    // by declaration order in the class (model, then engine here),
    // NOT by the order written in the initializer list.
    Car(const string& m, int hp) : model(m), engine(hp) {
        cout << "[Car built: " << model << "]\n";
    }

    void drive() const {
        cout << model << " starting up...\n";
        engine.start();     // Car delegates to its Engine member
    }
};

int main() {
    cout << "Building car:\n";
    Car myCar("Tesla Model 3", 480);

    cout << "\nDriving:\n";
    myCar.drive();

    return 0;
}
