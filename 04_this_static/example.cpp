// ============================================================
// CONCEPT 4: `this` pointer & `static` members
// ============================================================
// `this` is an implicit pointer to the current object, available
// inside every non-static member function. You've already used it
// implicitly. Explicit uses: disambiguating a shadowed name, or
// returning *this for chaining.
//
// `static` data members belong to the CLASS, not to any one object.
// There is exactly one copy, shared by every instance -- useful for
// things like "how many objects exist right now".
//
// `static` member functions can be called without an object
// (ClassName::function()) and can only touch static data (no `this`).
//
// Compile & run:
//   g++ -std=c++14 -Wall example.cpp -o example.exe ; ./example.exe
// ============================================================

#include <iostream>
using namespace std;

class Counter {
private:
    int id;

    // Declaration only. Must be DEFINED once outside the class
    // (see below main-adjacent line) -- it's not part of any object.
    static int totalCreated;

public:
    Counter() {
        totalCreated++;          // shared across all objects
        id = totalCreated;
    }

    // explicit `this` use: parameter name shadows the member, so
    // plain `id` would refer to the parameter, not the member.
    void setId(int id) {
        this->id = id;           // this->id is the member, id is the parameter
    }

    int getId() const {
        return id;
    }

    // Chaining pattern: return a reference to the current object so
    // calls can be stacked: obj.setId(5).printSelf();
    Counter& printSelf() {
        cout << "Counter #" << id << "\n";
        return *this;
    }

    // static member function: no `this`, can't access `id` (per-object),
    // can only touch static members like totalCreated.
    static int howManyExist() {
        return totalCreated;
    }
};

// Out-of-class definition -- required once per static data member.
int Counter::totalCreated = 0;

int main() {
    cout << "Before creating any: " << Counter::howManyExist() << "\n";

    Counter a;
    Counter b;
    Counter c;

    a.setId(100);   // explicit this-> disambiguation in action

    cout << "After creating 3: " << Counter::howManyExist() << "\n";

    a.printSelf().printSelf();   // chained via returning *this
    b.printSelf();
    c.printSelf();

    return 0;
}
