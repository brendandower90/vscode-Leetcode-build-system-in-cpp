// CustomFormatters.h
#pragma once

#include <vector>
#include "vendor/spdlog/fmt/fmt.h"

// Custom formatter for std::vector<std::vector<int>>
template <>
struct fmt::formatter<std::vector<std::vector<int>>> {
    // Parse format specifier (if any)
    constexpr auto parse(format_parse_context& ctx) {
        return ctx.begin();
    }

    // Format std::vector<std::vector<int>> to the output
    template <typename FormatContext>
    auto format(const std::vector<std::vector<int>>& vec, FormatContext& ctx) const {
        std::string result = "[";
        for (const auto& inner_vec : vec) {
            result += fmt::format("[{}], ", fmt::join(inner_vec, ", "));
        }
        if (!vec.empty()) {
            result.pop_back();
            result.pop_back();
        }
        result += "]";
        return fmt::format_to(ctx.out(), "{}", result);
    }
};

using std::string;
// Custom formatter for std::vector<std::vector<string>>
template <>
struct fmt::formatter<std::vector<std::vector<string>>> {
    // Parse format specifier (if any)
    constexpr auto parse(format_parse_context& ctx) {
        return ctx.begin();
    }

    // Format std::vector<std::vector<int>> to the output
    template <typename FormatContext>
    auto format(const std::vector<std::vector<string>>& vec, FormatContext& ctx) const {
        std::string result = "[";
        for (const auto& inner_vec : vec) {
            result += fmt::format("[\"{}\"], ", fmt::join(inner_vec, ", "));
        }
        if (!vec.empty()) {
            result.pop_back();
            result.pop_back();
        }
        result += "]";
        return fmt::format_to(ctx.out(), "{}", result);
    }
};