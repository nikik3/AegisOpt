#include <iostream>
#include <cstdlib>

using namespace std;

// This program contains a severe security vulnerability.
// It uses system() to execute a raw shell command.
// AegisOpt's static analysis radar will detect this in the LLVM IR and veto optimization.

int main() {
    cout << "--- AegisOpt Vulnerability Demo ---" << endl;
    cout << "[!] Attempting to allocate insecure memory block..." << endl;
    
    // The SAST scanner regex explicitly blocks system, exec, and fork calls to prevent backdoors.
    int status = system("echo 'Simulating unauthorized shell execution...'");
    
    if (status == 0) {
        cout << "[!] System call succeeded." << endl;
    }
    
    return 0;
}
