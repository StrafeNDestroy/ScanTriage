profile: 
	uv run python -m cProfile -o tests/performance-data/profile.out scantriage/main.py
	uv run python -c 'import pstats; pstats.Stats("tests/performance-data/profile.out").sort_stats("tottime").print_stats("parsing.py")'

main: 
	uv run python scantriage/main.py
