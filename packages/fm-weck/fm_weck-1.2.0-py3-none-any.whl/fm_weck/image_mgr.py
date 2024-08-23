# This file is part of fm-weck: executing fm-tools in containerized environments.
# https://gitlab.com/sosy-lab/software/fm-weck
#
# SPDX-FileCopyrightText: 2024 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from fm_tools.fmdata import FmImageConfig
from yaspin import yaspin

from fm_weck import Config

if TYPE_CHECKING:
    from fm_weck.engine import Engine

CONTAINERFILE = Path(__file__).parent / "resources" / "Containerfile"


class ImageMgr(object):
    """
    The image manager singleton is responsible for preparing the images for the container.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageMgr, cls).__new__(cls)
            cls._instance.image_db = Config().get("images", {}).get("database", None) or ":memory:"
        return cls._instance

    def prepare_image(self, engine: "Engine", image: FmImageConfig) -> str:
        if image.full_images:
            return image.full_images[0]

        if image.base_images and not image.required_packages:
            return image.base_images[0]

        logging.info(
            "Building image from from base image %s with packages %s", image.base_images[0], image.required_packages
        )
        image_cmd = engine.image_from(CONTAINERFILE)
        image_cmd.base_image(image.base_images[0])
        image_cmd.packages(image.required_packages)

        with yaspin(text="Building image", color="cyan") as spinner:
            tag = image_cmd.build()
            spinner.ok("✅ ")

        return tag
