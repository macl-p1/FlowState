// ============================================================
// EXERCISE 3: Encapsulation & const-correctness
// ============================================================
// Build a class called `Student`.
//
// REQUIREMENTS:
//   1. Private data members:
//        - string name
//        - int    marks        (0 to 100 inclusive)
//
//   2. Public methods:
//        - Student(const string& n, int m)
//              constructor, use a member initializer list for name.
//              For marks: if m is out of [0,100], clamp it into range
//              (m < 0 -> 0, m > 100 -> 100) before storing.
//        - string getName() const        -> returns name
//        - int    getMarks() const       -> returns marks
//        - void   setMarks(int m)        -> same clamping rule as ctor
//        - char   getGrade() const       -> based on marks:
//              >= 90 -> 'A'
//              >= 75 -> 'B'
//              >= 60 -> 'C'
//              >= 40 -> 'D'
//              else  -> 'F'
//        - void   print() const          -> prints:  "<name>: <marks> (<grade>)"
//              example line:  "Ajay: 85 (B)"
//
// RULES:
//   - name and marks must stay private.
//   - getName(), getMarks(), getGrade(), print() must be const.
//   - Do NOT duplicate the clamping logic by hand in two places --
//     call setMarks() from inside the constructor instead of
//     re-writing the clamp there.
//
// Compile:
//   g++ -std=c++14 -Wall exercise.cpp -o exercise.exe ; ./exercise.exe
// ============================================================

#include <iostream>
#include <string>
using namespace std;

class Student {
    // TODO: private data members
  private:
    string name;
    int marks;
  public:
    Student(const string& n , int m) : name(n) {
      setMarks(m);
    }
    string getName() const {
      return name;
    }
    int getMarks() const {
      return marks;
    }
    void setMarks(int m) {
      if (m > 100) marks = 100;
      else if (m < 0) marks = 0;
      else marks = m;
    }
    char getGrade() const {
      if (marks >= 90) return 'A';
      else if (marks >= 75) return 'B';
      else if (marks >= 60) return 'C';
      else if (marks >= 40) return 'D';
      else return 'F';
    }
    void print() const {
      cout << name << ": " << marks << " (" << getGrade() << ")" << "\n";
    }
};

// ------------------ DRIVER CODE (do not edit) ------------------
int main() {
    Student s1("Ajay", 85);
    s1.print();                    // expect: Ajay: 85 (B)

    Student s2("Riya", 120);       // out of range -> clamped to 100
    s2.print();                    // expect: Riya: 100 (A)

    Student s3("Kabir", -10);      // out of range -> clamped to 0
    s3.print();                    // expect: Kabir: 0 (F)

    s1.setMarks(59);
    s1.print();                    // expect: Ajay: 59 (D)

    s1.setMarks(500);              // clamp again via setter
    s1.print();                    // expect: Ajay: 100 (A)

    cout << s2.getName() << " scored " << s2.getMarks() << "\n";  // Riya scored 100

    return 0;
}
