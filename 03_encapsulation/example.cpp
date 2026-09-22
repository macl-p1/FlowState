// ============================================================
// CONCEPT 3: Encapsulation & const-correctness
// ============================================================
// Encapsulation = hide internal state behind a controlled interface
// (getters/setters), so the class can enforce its own rules and can
// change its internal representation later without breaking callers.
//
// const-correctness = mark things const wherever possible, so the
// compiler catches accidental mutation for you.
//
// Compile & run:
//   g++ -std=c++14 -Wall example.cpp -o example.exe ; ./example.exe
// ============================================================

#include <iostream>
using namespace std;

class Temperature {
private:
    double celsius;

public:
    Temperature(double c) : celsius(c) {}

    // GETTER: read-only access. Marked const because it doesn't
    // (and can't) modify the object.
    double getCelsius() const {
        return celsius;
    }

    // Derived getter -- computed from state, not stored separately.
    // This is the payoff of encapsulation: callers just ask for
    // fahrenheit, they never see or touch the formula.
    double getFahrenheit() const {
        return celsius * 9.0 / 5.0 + 32.0;
    }

    // SETTER: controlled write access. Can enforce invariants that
    // a public raw field never could.
    void setCelsius(double c) {
        if (c < -273.15) {           // absolute zero -- physically invalid
            cout << "Rejected: " << c << " is below absolute zero.\n";
            return;
        }
        celsius = c;
    }
};

// A function taking a `const Temperature&` promises NOT to modify it.
// The compiler enforces this: inside here, only const methods are callable.
void report(const Temperature& t) {
    cout << t.getCelsius() << "C = " << t.getFahrenheit() << "F\n";
    // t.setCelsius(100);   // <-- COMPILE ERROR: setCelsius isn't const,
                             //     can't call it on a const reference.
}

int main() {
    Temperature t(25.0);
    report(t);

    t.setCelsius(-300);     // rejected, stays at 25
    report(t);

    t.setCelsius(100);      // accepted
    report(t);

    return 0;
}
