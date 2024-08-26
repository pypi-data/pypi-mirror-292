from setuptools import setup, find_packages

setup(
    name='Arp-Mitm',
    version='0.1',
    description='A Python library for ARP spoofing and MITM attacks.',
    author='Matan',
    author_email='matannafgi@gmail.com',
    packages=find_packages(),
    install_requires=['scapy'],
    entry_points={
        'console_scripts': [
            'arp-mitm = arp_mitm.mitm:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)
