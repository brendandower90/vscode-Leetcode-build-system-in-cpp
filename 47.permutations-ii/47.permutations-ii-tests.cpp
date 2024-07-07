#include "TestRunner.h"
#include "47.permutations-ii.cpp"

// ========= TEST CASES  ===========
//
// Define test cases below:
std::vector<TestCase> testCases = {
    {
        // {1, 2, 3},  // Input
        // {1, 2, 4}   // Expected Output
    },
    {
        // {9, 8, 7, 6, 5, 4, 3, 2, 1, 0}, // Input 
        // {9, 8, 7, 6, 5, 4, 3, 2, 1, 1}  // Expected Output
    },
};


// Factory function to create the Solution object in the Leetcode test file
#ifdef LOCAL_TEST
LeetCodeSolution* createSolution() {
    return new Solution();
}

#endif
