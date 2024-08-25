from setuptools import setup, find_packages

setup(
    name='AbdomenAtlas',  # Your package name
    version='0.1.0',  # Your package version
    description='A package for 3D medical image segmentation using deep learning techniques.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),  # Automatically find packages in your project
    install_requires=[
        'connected_components_3d==3.18.0',
        'fastremap==1.15.0',
        'h5py==3.11.0',
        'imageio==2.35.1',
        'matplotlib==3.9.2',
        'monai==1.2.0',
        'nibabel==5.2.1',
        'numpy==2.1.0',
        'opencv_python==4.10.0.84',
        'pandas==2.2.2',
        'Pillow==10.4.0',
        'scipy==1.14.1',
        'tensorboardX==2.6.2.2',
        'torch==2.4.0',
        'tqdm==4.66.5',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify the minimum Python version required
)
