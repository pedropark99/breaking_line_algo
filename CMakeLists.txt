cmake_minimum_required(VERSION 3.1)

project(breaking_lines VERSION 1.0 LANGUAGES C)

add_executable(breaking_lines 
	main.c 
)


target_link_libraries(breaking_lines harfbuzz m)


