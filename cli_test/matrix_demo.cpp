#include <iostream>
#include <iomanip>

using namespace std;

void printMatrix(int mat[3][3], const string& name) {
    cout << name << ":" << endl;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            cout << setw(4) << mat[i][j] << " ";
        }
        cout << endl;
    }
    cout << endl;
}

int main() {
    int A[3][3] = { {1, 2, 3}, {4, 5, 6}, {7, 8, 9} };
    int B[3][3] = { {9, 8, 7}, {6, 5, 4}, {3, 2, 1} };
    int C[3][3] = {0};

    cout << "--- AegisOpt Matrix Multiplication Demo ---" << endl;
    printMatrix(A, "Matrix A");
    printMatrix(B, "Matrix B");

    // Standard O(N^3) multiplication
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            for (int k = 0; k < 3; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    printMatrix(C, "Result Matrix (A * B)");
    return 0;
}
