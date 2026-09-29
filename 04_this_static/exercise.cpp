// ============================================================
// EXERCISE 4: `this` pointer & `static` members
// ============================================================
// Build a class called `Employee` that tracks a running total
// salary paid across ALL employees, and supports method chaining.
//
// REQUIREMENTS:
//   1. Private data members:
//        - string name
//        - double salary
//
//   2. Private static data member:
//        - double totalPayroll     (sum of every salary ever set,
//                                    across all Employee objects)
//
//   3. Public methods:
//        - Employee(const string& name, double salary)
//              member-initializer-list for name and salary,
//              AND adds this salary into totalPayroll.
//              (Constructor body: just totalPayroll += salary;)
//
//        - void setName(const string& name)
//              parameter is named the SAME as the member on purpose --
//              you must use `this->name` to disambiguate.
//
//        - Employee& raiseSalary(double amount)
//              increases salary by amount, ALSO increases totalPayroll
//              by amount, then returns *this (for chaining).
//
//        - void print() const
//              prints:  "<name>: $<salary>"
//              example: "Ajay: $5000"
//
//        - static double getTotalPayroll()
//              returns totalPayroll. Must be static.
//
//   Don't forget: a static data member needs an out-of-class
//   definition line, e.g.   double Employee::totalPayroll = 0;
//   placed after the class, before main().
//
// RULES:
//   - print() must be const.
//   - getTotalPayroll() must be static and callable as
//     Employee::getTotalPayroll().
//
// Compile:
//   g++ -std=c++14 -Wall exercise.cpp -o exercise.exe ; ./exercise.exe
// ============================================================

#include <iostream>
#include <string>
using namespace std;

class Employee {
    private:
      string name;
      double salary;
      static double totalPayroll;
    public:
      Employee(const string& name, double salary) : name(name) , salary(salary) {
        totalPayroll += salary;
      }
      void setName(const string& name) {
        this -> name = name;
      }
      Employee& raiseSalary(double amount){
        totalPayroll += amount;
        salary += amount;
        return *this;
      }
      void print() const {
        cout << name << ": $"<< salary << "\n";
      }
      static double getTotalPayroll() {
        return totalPayroll;
      }
};

// TODO: out-of-class definition for the static member here
double Employee::totalPayroll = 0;

// ------------------ DRIVER CODE (do not edit) ------------------
int main() {
    cout << "Payroll before hiring: $" << Employee::getTotalPayroll() << "\n";

    Employee e1("Ajay", 5000);
    Employee e2("Riya", 6000);

    e1.print();     // Ajay: $5000
    e2.print();     // Riya: $6000

    cout << "Payroll after hiring 2: $" << Employee::getTotalPayroll() << "\n";  // 11000

    e1.raiseSalary(500).raiseSalary(250);   // chained
    e1.print();     // Ajay: $5750

    cout << "Payroll after raises: $" << Employee::getTotalPayroll() << "\n";    // 11750

    e2.setName("Riya Sharma");
    e2.print();     // Riya Sharma: $6000

    return 0;
}
