#pragma once

#include <vector>
#include <iostream>
#include <type_traits>

// config is generated when building from the solution file
#include "config.h"
#include "CustomFormatters.h"

// Generic prototype for a test case
struct TestCase
{
    test_arg_type input;
    test_return_type expected;

    TestCase(test_arg_type input, test_return_type expected)
    : input(std::move(input)), expected(std::move(expected)) {}

};


// Base class for the LeetCode solution
class LeetCodeSolution {
public:
    virtual ~LeetCodeSolution() = default;

    // Add the LeetCode test function here as pure virtual
    virtual test_return_type TEST_FUNC(test_arg_type& arg) = 0;
};

LeetCodeSolution* createSolution();  // Factory function declaration

// Templated test runner class with agnostic typesupport
template<typename SolutionType>
class LocalTests {
public:
    void runTests(const std::vector<TestCase>& testCases);

private:

    // using has_begin = decltype(std::declval<T>().begin());
    // using has_end = decltype(std::declval<T>().end());

    template<typename T, typename = void>
    struct is_container : std::false_type {};

    template<typename T>
    struct is_container<T, std::void_t<decltype(std::declval<T>().begin()), decltype(std::declval<T>().end())>> : std::true_type {};  

    template<typename T>
    void printResult(const T& result, const T& expected, int testNumber);
};
