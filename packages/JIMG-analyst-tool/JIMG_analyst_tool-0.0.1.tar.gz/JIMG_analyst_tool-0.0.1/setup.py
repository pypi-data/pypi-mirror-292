from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'JIMG_analyst_tool'
LONG_DESCRIPTION = '''
This library is designed specifically for the segmentation of cellular nuclei and chromatin, as well as for extracting intensity data from high-resolution images. It provides advanced tools for processing and analyzing raw image series, including operations like z-projection, channel merging, and image resizing. 

In addition to these features, the library includes capabilities for annotating specific regions of images, making it ideal for preparing datasets for machine learning (ML) and artificial intelligence (AI) applications. These annotation tools can be easily adapted to other imaging systems, enabling broad applicability in various fields of image-based data analysis. 

Whether you are working on detailed cellular imaging or broader data-driven research, this library offers a comprehensive solution. For further information or support, please do not hesitate to contact us!
'''


# Setting up
setup(
        name="JIMG_analyst_tool", 
        version=VERSION,
        author="Jakub Kubis",
        author_email="jbiosystem@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=['JIMG_analyst'],
        include_package_data=True,
        install_requires=[
                "csbdeep",
                "JIMG",
                "matplotlib",
                "pandas",
                "numpy",
                "opencv-python", 
                "stardist",
                "tqdm",
                "scikit-image",
                "IPython",
                "mpld3",
            ],        
        keywords=['python', 'nuclei', 'intenisty', 'image', 'high-resolution', 'comparison'],
        license = 'MIT',
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
        ],
        python_requires='>=3.6',
)


