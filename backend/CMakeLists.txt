cmake_minimum_required(VERSION 3.14)
project(quantbot_backend VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -march=native")

# Support standalone Asio and legacy names for Crow compatibility
add_definitions(-DASIO_STANDALONE)
add_definitions(-DASIO_ENABLE_OLD_SERVICES)

include(FetchContent)

# ── Asio (Networking dependency for Crow) ─────────────────────────────────────
FetchContent_Declare(
  asio-src
  URL https://github.com/chriskohlhoff/asio/archive/refs/tags/asio-1-24-0.tar.gz
)
FetchContent_MakeAvailable(asio-src)

# ── Crow (HTTP framework) ─────────────────────────────────────────────────────
FetchContent_Declare(
  crow-src
  GIT_REPOSITORY https://github.com/CrowCpp/Crow.git
  GIT_TAG v1.2.0
)
# Ensure Crow uses the fetched Asio
set(CROW_FEATURES "asio" CACHE STRING "Enable Asio")
set(ASIO_INCLUDE_DIR "${asio-src_SOURCE_DIR}/asio/include" CACHE PATH "Asio include path")
FetchContent_MakeAvailable(crow-src)

# ── nlohmann/json ─────────────────────────────────────────────────────────────
FetchContent_Declare(
  json
  URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
)
FetchContent_MakeAvailable(json)

# ── PostgreSQL (libpq) ────────────────────────────────────────────────────────
find_package(PostgreSQL REQUIRED)
include_directories(${PostgreSQL_INCLUDE_DIRS})

# ── Sources ───────────────────────────────────────────────────────────────────
set(SOURCES
    main.cpp
    src/IndicatorCalculator.cpp
    src/MockDataProvider.cpp
    src/TradingService.cpp
    src/AuthService.cpp
)

add_executable(quantbot_backend ${SOURCES})

target_include_directories(quantbot_backend PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(quantbot_backend PRIVATE
    Crow::Crow
    nlohmann_json::nlohmann_json
    ${PostgreSQL_LIBRARIES}
)

# Print summary
message(STATUS "QuantBotFX C++ Backend")
message(STATUS "  Build type : ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ std    : ${CMAKE_CXX_STANDARD}")
message(STATUS "  Binary     : quantbot_backend")
