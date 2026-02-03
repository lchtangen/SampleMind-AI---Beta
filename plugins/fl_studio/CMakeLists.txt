cmake_minimum_required(VERSION 3.16)
project(SampleMind_FL_Studio_Plugin VERSION 1.0.0 LANGUAGES CXX C)

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Set output directory
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# ============================================================================
# FIND REQUIRED PACKAGES
# ============================================================================

# Find Python
find_package(Python3 REQUIRED COMPONENTS Interpreter Development NumPy)

# Find FL Studio SDK (must be set via -DFL_STUDIO_SDK_PATH)
if(NOT DEFINED FL_STUDIO_SDK_PATH)
    message(WARNING "FL_STUDIO_SDK_PATH not set. Set with: -DFL_STUDIO_SDK_PATH=/path/to/fl/sdk")
else()
    message(STATUS "FL Studio SDK: ${FL_STUDIO_SDK_PATH}")
endif()

# ============================================================================
# SOURCE FILES
# ============================================================================

set(PLUGIN_SOURCES
    cpp/samplemind_wrapper.cpp
    cpp/samplemind_wrapper.h
)

# ============================================================================
# CREATE PLUGIN LIBRARY
# ============================================================================

add_library(SampleMind_FL_Plugin MODULE ${PLUGIN_SOURCES})

# ============================================================================
# INCLUDE DIRECTORIES
# ============================================================================

target_include_directories(SampleMind_FL_Plugin PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp
    ${Python3_INCLUDE_DIRS}
    ${Python3_NumPy_INCLUDE_DIRS}
)

# Add FL Studio SDK includes if available
if(DEFINED FL_STUDIO_SDK_PATH)
    target_include_directories(SampleMind_FL_Plugin PRIVATE
        ${FL_STUDIO_SDK_PATH}/include
        ${FL_STUDIO_SDK_PATH}/src
    )
endif()

# ============================================================================
# LINK LIBRARIES
# ============================================================================

target_link_libraries(SampleMind_FL_Plugin PRIVATE
    Python3::Python
    Python3::NumPy
)

# Link FL Studio SDK libraries if available
if(DEFINED FL_STUDIO_SDK_PATH)
    if(WIN32)
        find_library(FL_SDK_LIB flstudiolib PATHS ${FL_STUDIO_SDK_PATH}/lib)
        if(FL_SDK_LIB)
            target_link_libraries(SampleMind_FL_Plugin PRIVATE ${FL_SDK_LIB})
        endif()
    elseif(APPLE)
        find_library(FL_SDK_LIB NAMES flstudiolib PATHS ${FL_STUDIO_SDK_PATH}/lib)
        if(FL_SDK_LIB)
            target_link_libraries(SampleMind_FL_Plugin PRIVATE ${FL_SDK_LIB})
        endif()
    endif()
endif()

# ============================================================================
# COMPILER FLAGS
# ============================================================================

if(MSVC)
    # Windows MSVC
    target_compile_options(SampleMind_FL_Plugin PRIVATE
        /W4
        /WX
        /O2
        /EHsc
    )

    # Windows-specific definitions
    target_compile_definitions(SampleMind_FL_Plugin PRIVATE
        _WINDOWS
        _USE_MATH_DEFINES
        WIN32_LEAN_AND_MEAN
        VC_EXTRALEAN
    )

elseif(APPLE)
    # macOS Clang
    target_compile_options(SampleMind_FL_Plugin PRIVATE
        -Wall
        -Werror
        -O2
        -fPIC
        -fvisibility=hidden
    )

    # macOS-specific definitions
    target_compile_definitions(SampleMind_FL_Plugin PRIVATE
        __APPLE__
        __MACH__
    )

    # Set deployment target
    set_target_properties(SampleMind_FL_Plugin PROPERTIES
        MACOSX_DEPLOYMENT_TARGET "10.13"
    )

else()
    # Linux GCC/Clang
    target_compile_options(SampleMind_FL_Plugin PRIVATE
        -Wall
        -Werror
        -O2
        -fPIC
        -fvisibility=hidden
    )

    # Linux-specific definitions
    target_compile_definitions(SampleMind_FL_Plugin PRIVATE
        __LINUX__
    )

endif()

# ============================================================================
# PLATFORM-SPECIFIC CONFIGURATION
# ============================================================================

if(WIN32)
    # Windows plugin configuration
    set_target_properties(SampleMind_FL_Plugin PROPERTIES
        PREFIX ""
        SUFFIX ".dll"
        OUTPUT_NAME "SampleMind_FL_Studio"
    )

    # Set Windows subsystem
    set_target_properties(SampleMind_FL_Plugin PROPERTIES
        VS_PLATFORM_TOOLSET "v142"
    )

elseif(APPLE)
    # macOS plugin configuration
    set_target_properties(SampleMind_FL_Plugin PROPERTIES
        PREFIX "lib"
        SUFFIX ".dylib"
        OUTPUT_NAME "SampleMind_FL_Studio"
        FRAMEWORK FALSE
    )

    # macOS-specific linking flags
    target_link_options(SampleMind_FL_Plugin PRIVATE
        "-undefined dynamic_lookup"
    )

else()
    # Linux plugin configuration
    set_target_properties(SampleMind_FL_Plugin PROPERTIES
        PREFIX "lib"
        SUFFIX ".so"
        OUTPUT_NAME "SampleMind_FL_Studio"
    )

endif()

# ============================================================================
# OPTIMIZATION
# ============================================================================

if(CMAKE_BUILD_TYPE MATCHES Release)
    # Release optimizations
    target_compile_options(SampleMind_FL_Plugin PRIVATE
        $<$<CONFIG:Release>:-O3>
        $<$<CONFIG:Release>:-DNDEBUG>
    )
else()
    # Debug configuration
    target_compile_options(SampleMind_FL_Plugin PRIVATE
        $<$<CONFIG:Debug>:-O0>
        $<$<CONFIG:Debug>:-g>
    )
    target_compile_definitions(SampleMind_FL_Plugin PRIVATE
        _DEBUG
    )
endif()

# ============================================================================
# INSTALL TARGETS
# ============================================================================

install(TARGETS SampleMind_FL_Plugin
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

# ============================================================================
# CUSTOM TARGETS
# ============================================================================

# Target for running with Valgrind (Linux)
if(UNIX AND NOT APPLE)
    add_custom_target(valgrind
        COMMAND valgrind --leak-check=full --show-leak-kinds=all
                $<TARGET_FILE:SampleMind_FL_Plugin>
        DEPENDS SampleMind_FL_Plugin
    )
endif()

# Target for code formatting
add_custom_target(format
    COMMAND clang-format -i ${PLUGIN_SOURCES}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

# ============================================================================
# BUILD INFORMATION
# ============================================================================

message(STATUS "================================================")
message(STATUS "SampleMind FL Studio Plugin - Build Configuration")
message(STATUS "================================================")
message(STATUS "CMake Version: ${CMAKE_VERSION}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Python: ${Python3_VERSION}")
message(STATUS "Python Include: ${Python3_INCLUDE_DIRS}")
message(STATUS "NumPy: ${Python3_NumPy_INCLUDE_DIRS}")
message(STATUS "================================================")

# Platform-specific info
if(WIN32)
    message(STATUS "Platform: Windows")
    message(STATUS "Plugin Output: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/SampleMind_FL_Studio.dll")
elseif(APPLE)
    message(STATUS "Platform: macOS")
    message(STATUS "Plugin Output: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/libSampleMind_FL_Studio.dylib")
else()
    message(STATUS "Platform: Linux")
    message(STATUS "Plugin Output: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/libSampleMind_FL_Studio.so")
endif()

message(STATUS "================================================")
