// ============================================================
// CONCEPT 2: Constructors & Destructors
// ============================================================
// A constructor is a special method that runs automatically when
// an object is created. It replaces the "init()" pattern from
// Concept 1 — and it guarantees the object is never left half-set-up.
//
// A destructor runs automatically when an object is destroyed
// (goes out of scope, or is deleted). Used for cleanup.
//
// Compile & run:
//   g++ -std=c++14 -Wall example.cpp -o example.exe ; ./example.exe
// ============================================================

#include <iostream>
#include <string>
using namespace std;

class BankAccount {
private:
    string owner;
    double balance;

public:
    // Default constructor — runs when no arguments are given.
    BankAccount() {
        owner = "Unknown";
        balance = 0.0;
        cout << "[default ctor] created blank account\n";
    }

    // Parameterized constructor — preferred style uses a
    // MEMBER INITIALIZER LIST (the ": owner(o), balance(b)" part).
    // This directly initializes members instead of default-constructing
    // them and then assigning — more efficient, and required for
    // members like const or references.
    BankAccount(const string& o, double b) : owner(o), balance(b) {
        cout << "[param ctor] created account for " << owner << "\n";
    }

    // Copy constructor — runs when a new object is built FROM an
    // existing one, e.g. "BankAccount b2 = b1;" or passing by value.
    BankAccount(const BankAccount& other) : owner(other.owner), balance(other.balance) {
        cout << "[copy ctor] copied account for " << owner << "\n";
    }

    // Destructor — runs automatically at end of object's lifetime.
    ~BankAccount() {
        cout << "[dtor] destroying account for " << owner << "\n";
    }

    void print() const {
        cout << owner << " has $" << balance << "\n";
    }
};

void showAccount(BankAccount acc) {   // passed BY VALUE -> triggers copy ctor
    cout << "  inside showAccount: ";
    acc.print();
}   // acc's destructor runs here, when the function's local copy dies

int main() {
    BankAccount a;                     // default ctor
    BankAccount b("Ajay", 100.0);      // param ctor
    BankAccount c = b;                 // copy ctor (copy-initialization)

    a.print();
    b.print();
    c.print();

    showAccount(b);                    // copy made for the parameter, then destroyed

    cout << "end of main\n";
    return 0;
    // a, b, c destructors run here, in REVERSE order of construction: c, b, a
}
