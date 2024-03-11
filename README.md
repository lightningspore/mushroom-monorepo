# mushroom-monorepo

Welcome to the LightningSpore's Open Source Mushroom Cultivation Codebase, a comprehensive repository dedicated to providing tools, software, and hardware projects for mushroom cultivation enthusiasts and researchers. This repository, includes a wide range of projects from software applications for analog gauge reading to firmware for microcontroller-based sensors, and even electronics schematics for DIY hardware projects.

## Key Components
### Software Projects

- **Analog Gauge Reader**: A Python application that uses OpenCV to read analog gauges. Useful for monitoring pressure in autoclaves or substrate jars. [Read more](software/analog-gauge-reader/README.md).

- **Camera Server**: Starts a web server on a device to return images taken from a webcam. [Read more](software/camera-server/README.md).

- **Pico Firmware**: Firmware written in CircuitPython for various sensors including temperature and humidity sensors. [Read more](software/pico-firmware/README.md).

- **Shelly IoT Devices**: Integration with Shelly IoT devices for controlling environmental conditions. [Example in notebook](notebook/mushroom.ipynb#L12-L25).

### Electronics Projects
- Projects like **Induction Sterilizer**, **Incubator**, and **Culture Fridge** with KiCAD schematics. [Explore Electronics Projects](electronics/ELECTRONICS.md).

### Jupyter Notebooks
- **Mushroom Cultivation Notebook**: A Jupyter notebook that includes code snippets for interacting with IoT devices, and more. [Setup instructions](notebook/HOWTO.md).

## Getting Started
To get started with the projects in this repository:

1. **Clone the repository**: Clone or download the [mushroom-monorepo](file:///Users/samkorn/Documents/repos/mushroom-monorepo/README.md#1%2C3-1%2C3) to your local machine.

2. **Explore the README files**: Each project directory has its own README file with specific instructions on setup and usage.

3. **Install dependencies**: For Python projects, ensure you have the correct version of Python installed and use [pip](software/camera-server/README.md#15%2C1-15%2C1) to install required packages as listed in `pyproject.toml` files, e.g., [camera-server dependencies](software/camera-server/pyproject.toml).

4. **Hardware projects**: For electronics projects, refer to the KiCAD files and schematics provided in the `electronics` directory.

## Contributing
Contributions are welcome! Whether it's adding new features, fixing bugs, or improving documentation, your help is appreciated. Please read through the existing issues or create a new one before submitting a pull request.


## Licensing
- Most of the software is provided under the MIT License, allowing for wide use, modification, and distribution. [View License](software/analog-gauge-reader/LICENSE).

## Contact
For any questions or suggestions, feel free to open an issue in the repository, or contact us at [lightningspore.com](https://lightningspore.com). If you like the contents of this repository, and you would like to financially support further development, please consider purchasing one of the products available on our website.

