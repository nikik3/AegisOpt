#include <chrono>
#include <iostream>
#include <random>
#include <vector>

const int N = 512;

void multiple(const std::vector<std::vector<double>> &A,
              const std::vector<std::vector<double>> &B,
              std::vector<std::vector<double>> &C) {
  for (int i = 0; i < N; ++i) {
    for (int j = 0; j < N; ++j) {
      for (int k = 0; k < N; ++k) {
        C[i][j] += A[i][k] * B[k][j];
      }
    }
  }
}

int main() {
  std::vector<std::vector<double>> A(N, std::vector<double>(N));
  std::vector<std::vector<double>> B(N, std::vector<double>(N));
  std::vector<std::vector<double>> C(N, std::vector<double>(N, 0.0));

  std::mt19937 gen(42);
  std::uniform_real_distribution<> dis(0.0, 1.0);

  for (int i = 0; i < N; ++i) {
    for (int j = 0; j < N; ++j) {
      A[i][j] = dis(gen);
      B[i][j] = dis(gen);
    }
  }

  std::cout << "Starting Matrix Multiplication (N=" << N << ")..." << std::endl;

  auto start = std::chrono::high_resolution_clock::now();
  multiple(A, B, C);
  auto end = std::chrono::high_resolution_clock::now();

  std::chrono::duration<double> elapsed = end - start;
  std::cout << "Execution time: " << elapsed.count() << " sec" << std::endl;

  std::cout << "Result C[0][0]: " << C[0][0] << std::endl;

  return 0;
}
