/*
 * @lc app=leetcode id=66 lang=cpp
 *
 * [66] Plus One
 */

#include "config.h"
#include "TestRunner.h"

#ifdef LOCAL_TEST
class Solution : public LeetCodeSolution
#else
class Solution
#endif 
{
public:
    std::vector<int> plusOne(std::vector<int> &digits)
    {
        int carry = 1;
        for (int i = digits.size() - 1; i >= 0; --i)
        {
            int sum = digits[i] + carry;
            if (sum > 9)
            {
                digits[i] = sum % 10;
                carry = 1;
            }
            else
            {
                digits[i] = sum;
                carry = 0;
            }
        }
        if (carry)
        {
            digits.insert(digits.begin(), carry);
        }
        return digits;
    } 
};
// @lc code=end


