#include <iostream>
#include <vector>

using namespace std;

// Heavy computation benchmark using the Sieve of Eratosthenes
// The RL Agent will find that loop unrolling and vectorization drastically improves this over basic -O3

int main() {
    const int LIMIT = 5000000;
    vector<bool> is_prime(LIMIT + 1, true);
    is_prime[0] = false;
    is_prime[1] = false;

    cout << "--- AegisOpt Heavy Compute Benchmark ---" << endl;
    cout << "Calculating primes up to " << LIMIT << "..." << endl;

    for (int p = 2; p * p <= LIMIT; p++) {
        if (is_prime[p]) {
            for (int i = p * p; i <= LIMIT; i += p) {
                is_prime[i] = false;
            }
        }
    }

    int prime_count = 0;
    for (int p = 2; p <= LIMIT; p++) {
        if (is_prime[p]) {
            prime_count++;
        }
    }

    cout << "Total Primes Found: " << prime_count << endl;
    cout << "Benchmark execution fully completed." << endl;
    
    return 0;
}
