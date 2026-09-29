// ============================================================
// CONCEPT 1: Classes & Objects
// ============================================================
// A class is a blueprint. An object is a concrete thing built
// from that blueprint.
//
// Key ideas shown here:
//   - data members (state)      -> the variables inside a class
//   - member functions (methods)-> the behavior
//   - access specifiers         -> public: usable from outside
//                                  private: internal only (default)
//
// Compile & run:
//   g++ -std=c++17 -Wall example.cpp -o example && ./example
// (on Windows PowerShell:  g++ -std=c++17 -Wall example.cpp -o example.exe ; ./example.exe)
// ============================================================

#include <iostream>
#include <string>

class BankAccount {
private:
    // State: only the class's own methods can touch these.
    std::string owner;
    double balance;

public:
    // A method to set up the object. (We'll formalize this as a
    // "constructor" in Concept 2 — for now it's just a plain method.)
    void init(const std::string& ownerName, double startingBalance) {
        owner = ownerName;
        balance = startingBalance;
    }

    // Behavior that changes state.
    void deposit(double amount) {
        if (amount <= 0) {
            std::cout << "Deposit must be positive.\n";
            return;
        }
        balance += amount;
    }

    void withdraw(double amount) {
        if (amount > balance) {
            std::cout << "Insufficient funds.\n";
            return;
        }
        balance -= amount;
    }

    // Behavior that only reads state.
    void print() const {
        std::cout << owner << " has $" << balance << "\n";
    }
};

int main() {
    // Two independent objects from the same blueprint.
    BankAccount a;
    a.init("Ajay", 100.0);

    BankAccount b;
    b.init("Riya", 50.0);

    a.deposit(25.0);
    a.withdraw(200.0);   // rejected
    a.withdraw(40.0);

    b.deposit(10.0);

    a.print();   // Ajay has $85
    b.print();   // Riya has $60

    // a.balance = 999;  // <-- COMPILE ERROR: 'balance' is private. Good.

    return 0;
}
