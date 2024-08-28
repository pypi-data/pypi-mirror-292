from setuptools import find_packages, setup


def main():
    setup(
        name="atek-core",
        version="0.3",
        description="Aria train and evaluation kits",
        author="Meta Reality Labs Research",
        packages=find_packages(),  # automatically discover all packages and subpackages
        install_requires=[
            "torch==2.0",  # Assuming 'pytorch=2' corresponds to this version
            "torchvision",
            "fvcore",
            "iopath",
            "tqdm",
            "scipy",
            "webdataset",
            "trimesh",
            "pybind11",
            "toolz",
            "opencv-python",
            # Add other dependencies that can be resolved by pip here
        ],
        dependency_links=[
            "git+https://github.com/facebookresearch/pytorch3d.git@stable#egg=pytorch3d",
            "git+https://github.com/facebookresearch/detectron2.git#egg=detectron2",
        ],
        extras_require={
            "dev": [
                "projectaria-tools==1.5.4",
            ]
        },
    )


if __name__ == "__main__":
    main()
