import os
import io
import shutil
import random
import zipfile
import threading
from typing import Optional
from multiprocessing.dummy import Pool as ThreadPool

from PIL import Image

from pokemon import Pokemon


class ImageGenerator:
    def __init__(self) -> None:
        self.images_path = os.path.join(os.path.dirname(__file__), "data", "images")
        self.backgrounds_path = os.path.join(
            os.path.dirname(__file__), "backgrounds"
        )

        self.image_cache: dict[str, Image.Image] = {}
        self.image_cache_lock = threading.Lock()

    def get_image_path(self, id: int) -> str:
        return os.path.join(self.images_path, f"{id}.png")

    def get_background_path(self, id: int) -> str:
        return os.path.join(self.backgrounds_path, f"{id}.png")

    def get_backgrounds(self) -> list[int]:
        return [
            int(background.split(".")[0])
            for background in os.listdir(self.backgrounds_path)
        ]

    def open_image(self, path: str) -> Optional[Image.Image]:
        with self.image_cache_lock:
            try:
                # Open image from cache if it exists
                if path not in self.image_cache:
                    self.image_cache[path] = Image.open(path)

                return self.image_cache[path].copy()
            except FileNotFoundError:
                return None

    def generate(self, id: int, bg_id: int) -> Optional[Image.Image]:
        # Open and resize image
        image = self.open_image(self.get_image_path(id))
        if image is None:
            return None

        size = random.randint(300, 400)
        image = image.resize((size, size))

        # Open background image
        bg_image = self.open_image(self.get_background_path(bg_id))

        # Get random position for image
        available_x = bg_image.width - image.width
        x = random.randint(int(1 / 4 * available_x), int(3 / 4 * available_x))

        available_y = bg_image.height - image.height
        y = random.randint(int(1 / 4 * available_y), int(3 / 4 * available_y))

        # Paste image on background
        bg_image.paste(image, (x, y), image)

        return bg_image


class DatasetGenerator:
    def __init__(self) -> None:
        self.image_generator = ImageGenerator()
        self.backgrounds = self.image_generator.get_backgrounds()

        self.dataset_path = os.path.join(
            os.path.dirname(__file__), "data", "dataset.zip"
        )

        self.dataset = zipfile.ZipFile(self.dataset_path, "a")
        self.dataset_lock = threading.Lock()

        self.index = 0
        self.amount = 0

    def generate_images(self, pokemon: Pokemon) -> None:
        exists = False

        try:
            with self.dataset_lock:
                self.dataset.getinfo(f"{pokemon.slug}/1.png")
                exists = True
        except KeyError as e:
            pass

        if exists:
            print(f"Skipping {pokemon.slug} ({self.index}/{self.amount})")
            self.index += 1
            return

        for bg_id in self.backgrounds:
            image = self.image_generator.generate(pokemon.id, bg_id)
            if image is None:
                # This Pokemon doesn't have an image
                continue

            image_data = io.BytesIO()

            image.save(image_data, format="PNG")

            with self.dataset_lock:
                self.dataset.writestr(
                    f"{pokemon.slug}/{bg_id}.png", image_data.getvalue()
                )

        self.index += 1

        print(
            f"Generated {len(self.backgrounds)} images for {pokemon.slug} ({self.index}/{self.amount})"
        )

    def generate(self, pokemon_list: list[Pokemon], threads: int = 200) -> None:
        self.amount = len(pokemon_list)

        pool = ThreadPool(threads)

        pool.map(self.generate_images, pokemon_list)

        pool.close()
        pool.join()
