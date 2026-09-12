from setuptools import setup, find_packages

setup(
    name="repopilot",
    version="0.1.0",
    description="CLI tool for developer workflows — setup, env, clean, logs.",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "repopilot=main:main",
        ],
    },
)
