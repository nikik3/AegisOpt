#include <iostream>
#include <cmath>
#include <vector>

// High-Frequency Trading (HFT) / Quantitative Finance Kernel
// Calculates European Call Option Prices using the Black-Scholes Formula

double normalCDF(double value) {
    return 0.5 * erfc(-value * M_SQRT1_2);
}

double blackScholesCall(double S, double K, double T, double r, double sigma) {
    double d1 = (log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrt(T));
    double d2 = d1 - sigma * sqrt(T);
    return S * normalCDF(d1) - K * exp(-r * T) * normalCDF(d2);
}

int main() {
    const int numOptions = 5000000;
    double S = 100.0;  // Spot Price
    double K = 100.0;  // Strike Price
    double T = 1.0;    // Time to maturity (1 year)
    double r = 0.05;   // Risk-free interest rate
    double sigma = 0.2; // Volatility

    volatile double dummy = 0; // Prevent aggressive -O3 from optimizing the loop entirely away

    for (int i = 0; i < numOptions; ++i) {
        // Slightly modify S to simulate market tick data
        double S_tick = S + (i % 10) * 0.1;
        dummy += blackScholesCall(S_tick, K, T, r, sigma);
    }

    std::cout << "Computed " << numOptions << " Black-Scholes prices." << std::endl;
    return 0;
}
