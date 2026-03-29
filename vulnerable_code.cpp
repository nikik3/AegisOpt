#include <iostream>
#include <cstring>

// Intentionally insecure benchmark for security scanning demos.
// Compiles on modern C++ compilers while still demonstrating a classic overflow pattern.
void insecure_function() {
    char buffer[64];
    // Dangerous API: strcpy does not check bounds. Here the input is controlled
    // so it won't crash, but it is still a security smell the scanner should flag.
    std::strcpy(buffer, "HELLO");
    std::cout << "Buffer: " << buffer << std::endl;
}

int main() {
    insecure_function();
    return 0;
}
