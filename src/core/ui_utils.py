try:
    import pyi_splash
except ImportError:
    pyi_splash = None


def close_splash_screen():
    if pyi_splash:
        pyi_splash.close()
