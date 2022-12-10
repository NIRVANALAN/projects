from pathlib import Path
from tqdm import tqdm, trange
from pygifsicle import optimize
import os


def test_optimize():
    optimize("tests/big.gif", "small.gif")
    optimize("small.gif")
    os.remove("small.gif")


# optimize gif in E3DGE
def optimize_gif_e3dge():
    gifs = list(Path('E3DGE').rglob('*.gif'))
    # print(gifs)
    for gif in tqdm(gifs):
        # optimize(str(gif), gif.parent / f'optimized_{gif.stem}.gif')
        optimize(str(gif), gif.parent / f'{gif.stem}_opt.gif')
        os.remove(str(gif))


optimize_gif_e3dge()