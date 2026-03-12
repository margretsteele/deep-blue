#!/usr/bin/env python


import pstats
p = pstats.Stats('profiling.prof')
p.sort_stats('cumulative').print_stats()
