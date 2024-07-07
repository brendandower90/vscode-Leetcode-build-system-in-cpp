#include "config.h"
#include "TestRunner.h"
#include <memory>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>

#include <spdlog/fmt/bundled/core.h>
#include <spdlog/fmt/bundled/color.h>


void initLogger()
{
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_st>();  // Console sink
    auto logger = std::make_shared<spdlog::logger>(test_name, console_sink);
    logger->set_pattern("[%^%n%$]: %v"); // log the name and the text
    spdlog::set_default_logger(logger);
}

template<typename SolutionType>
void LocalTests<SolutionType>::runTests(const std::vector<TestCase>& testCases) {
    for (size_t i = 0; i < testCases.size(); ++i) {
        const auto& testCase = testCases[i];
        SolutionType* solution = createSolution();
        auto result = solution->TEST_FUNC(const_cast<test_arg_type&>(testCase.input));
        printResult(result, testCase.expected, i + 1);
        delete solution;
    }
}


template<typename SolutionType>
template<typename T>
void LocalTests<SolutionType>::printResult(const T& result, const T& expected, int testNumber) 
{
    using namespace fmt;

    bool passed = (result == expected);
    std::string resultStr = passed ? "PASSED" : "FAILED"; 
    auto color = passed ? terminal_color::green : terminal_color::red;
    spdlog::info("Test case {}: {}", testNumber, format(fg(color) | emphasis::bold, resultStr));

    if (!passed)
    {
        if constexpr (is_container<T>::value)
        {
            print("\t   >> Expected: [{}]\n", join(expected, " "));
            print("\t   >> Received: [{}]\n\n", join(result, " "));
        }
        else
        {
            print("\t   >> Expected: {}\n", expected);
            print("\t   >> Received:  {}\n\n", result);
        }
    }
}

int main() 
{
    // Initialize the logger
    initLogger();

    // Declare the test cases vector
    extern std::vector<TestCase> testCases;

    // Run the tests and print the result
    LocalTests<LeetCodeSolution> tests;
    tests.runTests(testCases);

    return 0;
}

// Explicit template instantiation
template class LocalTests<LeetCodeSolution>;

