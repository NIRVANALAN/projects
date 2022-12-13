from PIL import Image
from pathlib import Path
from tqdm import tqdm, trange
import os

# optimize gif in E3DGE
def resize_img_256():
    gt_imgs = list(Path('E3DGE').rglob('*.jpg'))
    for img_path in tqdm(gt_imgs):
        # optimize(str(img), img.parent / f'{img.stem}_opt.gif')
        img = Image.open(img_path).resize((256,256))
        img.save(img_path)
        # os.remove(str(img))


resize_img_256()