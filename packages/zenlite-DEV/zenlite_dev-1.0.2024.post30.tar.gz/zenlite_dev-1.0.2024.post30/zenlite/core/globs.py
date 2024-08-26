import os, sys;    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = str(True)
import glm, glfw, time
import pygame as pg, numpy as np
from numba import njit as bytec

ZEN_ASSET_DIR = __file__.removesuffix("core\\globs.py")+"assets\\"