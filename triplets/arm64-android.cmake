set(VCPKG_TARGET_ARCHITECTURE arm64)
set(VCPKG_CRT_LINKAGE static)
set(VCPKG_LIBRARY_LINKAGE static)
set(VCPKG_CMAKE_SYSTEM_NAME Android)

if("$ENV{ANDROID_NATIVE_API_LEVEL}" STREQUAL "")
	set(ENV{ANDROID_NATIVE_API_LEVEL} 23)
endif()
