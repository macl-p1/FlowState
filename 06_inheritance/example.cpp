// ============================================================
// EXAMPLE 6: Inheritance
// ============================================================
// Derive a class from another.  The derived class IS A base
// class plus more.
//
// KEY IDEA:
//   - Base class defines common data/methods
//   - Derived class inherits all that, and can add/override
// ============================================================

#include <iostream>
#include <string>
using namespace std;

// ---------- Base class ----------
class Animal {
protected:                  // derived classes CAN access
    string name;

public:
    Animal(const string& n) : name(n) {}

    // virtual => allows derived override + runtime dispatch
    virtual void speak() const {
        cout << name << " makes a sound\n";
    }

    virtual ~Animal() {}    // always virtual when class has virtuals
};

// ---------- Derived class ----------
// "Dog IS AN Animal"
class Dog : public Animal {
    string breed;

public:
    // constructor calls base constructor, then init own members
    Dog(const string& n, const string& b)
        : Animal(n), breed(b) {}

    // overrides Animal::speak  (must match signature)
    void speak() const override {
        cout << name << " (" << breed << ") says: Woof!\n";
    }
};

// Another derived class
class Cat : public Animal {
    int lives;

public:
    Cat(const string& n, int l)
        : Animal(n), lives(l) {}

    void speak() const override {
        cout << name << " has " << lives << " lives. Meow!\n";
    }

    // Cat-only method — not in base
    void nap() const {
        cout << name << " is napping...\n";
    }
};

// ---------- Polymorphic function ----------
void makeSpeak(const Animal& a) {
    // Calls the CORRECT speak() at runtime based on actual type
    a.speak();
}

int main() {
    Dog   d("Rex", "German Shepherd");
    Cat   c("Luna", 9);

    // Direct call — resolved at compile time
    d.speak();
    // Rex (German Shepherd) says: Woof!

    c.speak();
    // Luna has 9 lives. Meow!

    c.nap();
    // Luna is napping...

    // Polymorphism via base-class reference
    Animal& a1 = d;
    Animal& a2 = c;
    a1.speak();   // Rex (German Shepherd) says: Woof!  (Dog's version)
    a2.speak();   // Luna has 9 lives. Meow!            (Cat's version)

    // Same via function
    makeSpeak(d); // Dog version
    makeSpeak(c); // Cat version

    return 0;
}
