#include <iostream>
#include <vector>
#include <chrono>

#define N 512

void multiply(const std::vector<std::vector<double>>& A, 
              const std::vector<std::vector<double>>& B, 
              std::vector<std::vector<double>>& C) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    std::vector<std::vector<double>> A(N, std::vector<double>(N, 1.0));
    std::vector<std::vector<double>> B(N, std::vector<double>(N, 1.0));
    std::vector<std::vector<double>> C(N, std::vector<double>(N, 0.0));

    auto start = std::chrono::high_resolution_clock::now();
    multiply(A, B, C);
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> diff = end - start;
    std::cout << "Matrix Multiplication (N=" << N << ") completed." << std::endl;
    std::cout << "Execution time: " << diff.count() << " s" << std::endl;
    
    // Print a value to prevent compiler from optimizing away the whole loop
    std::cout << "Check value: " << C[0][0] << std::endl;

    return 0;
}
