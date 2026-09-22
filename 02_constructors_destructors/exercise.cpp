// ============================================================
// EXERCISE 2: Constructors & Destructors
// ============================================================
// Build a class called `Logger`. It simulates a resource that must
// announce when it opens and closes (like a file handle).
//
// REQUIREMENTS:
//   1. Private data member:
//        - string name
//
//   2. Public methods:
//        - Default constructor Logger()
//              sets name = "default", prints:  [open] default
//        - Parameterized constructor Logger(const string& n)
//              sets name = n, prints:  [open] <n>
//        - Copy constructor Logger(const Logger& other)
//              copies the name, prints:  [copy] <name>
//        - Destructor ~Logger()
//              prints:  [close] <name>
//        - void log(const string& msg) const
//              prints:  <name>: <msg>
//
//   All prints end with "\n". Format exactly as shown (no extra
//   spaces) so the output matches the driver's expectations.
//
// RULES:
//   - Use a member initializer list in both non-default constructors.
//   - name must stay private.
//
// Compile:
//   g++ -std=c++14 -Wall exercise.cpp -o exercise.exe ; ./exercise.exe
// ============================================================

#include <iostream>
#include <string>
using namespace std;

class Logger {
    // TODO: private data member
  private:
    string name;
  public:
    Logger() {
      name = "default";
      cout << "[open] " << name << "\n"; 
    }
    Logger(const string &n) : name(n){
      cout << "[open] " << name << "\n";
    }
    Logger(const Logger& other) : name(other.name){
      cout << "[copy] " << name << "\n"; 
    }
    ~Logger(){
      cout << "[close] " << name << "\n"; 
    }
    void log(const string& msg) const {
      cout << name << ": " << msg << "\n"; 
    }
};

// ------------------ DRIVER CODE (do not edit) ------------------
void processWithLogger(Logger lg) {          // pass by value -> copy ctor fires
    lg.log("processing");
}   // lg destructed here

int main() {
    cout << "--- creating loggers ---\n";
    Logger l1;                               // [open] default
    Logger l2("network");                    // [open] network

    l1.log("starting up");                   // default: starting up
    l2.log("connecting");                    // network: connecting

    cout << "--- copying ---\n";
    Logger l3 = l2;                          // [copy] network
    l3.log("copy alive");                    // network: copy alive

    cout << "--- passing by value ---\n";
    processWithLogger(l1);                   // [copy] default, then "default: processing", then [close] default

    cout << "--- end of main ---\n";
    return 0;
    // l3, l2, l1 destructors fire here in reverse order: l3, l2, l1
}
