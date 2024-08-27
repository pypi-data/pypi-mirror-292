"""Wrapper for van Buren spheroidal wave function code (in Fortran)."""

import fmodpy

# fmodpy.configure(f_compiler="fintel")


spheroidal = fmodpy.fimport('prolate_swf.f90', build_dir='.', output_dir='.')
