#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <random>

#define SIZE 1000000

int main() {
    std::vector<int> data(SIZE);
    std::iota(data.begin(), data.end(), 0);
    
    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(data.begin(), data.end(), g);

    auto start = std::chrono::high_resolution_clock::now();
    std::sort(data.begin(), data.end());
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> diff = end - start;
    std::cout << "Sorting (Size=" << SIZE << ") completed." << std::endl;
    std::cout << "Execution time: " << diff.count() << " s" << std::endl;

    return 0;
}
