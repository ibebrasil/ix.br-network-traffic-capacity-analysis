# PeeringDB Data Extractor

[Versão em Português](README_pt-br.md)

This project consists of a Python script to extract and process data from the PeeringDB API, focusing on information about Internet Exchanges (IX) in Brazil and their associated facilities.

## Features

- Extracts IX data in Brazil from the PeeringDB API
- Retrieves IXFAC (IX Facility) information for each IX
- Obtains FAC (Facility) details for each IXFAC
- Merges IXFAC and FAC data
- Saves data in JSON and CSV formats

## Requirements

- Python 3.8+
- Anaconda (recommended for environment management)
- PeeringDB API key

## Environment Setup

Follow these steps to set up the development environment:

1. Clone the repository:
   ```
   git clone https://github.com/your-username/peeringdb-data-extractor.git
   cd peeringdb-data-extractor
   ```

2. Create an Anaconda environment with Python 3.8:
   ```
   conda create -n peeringdb-env python=3.8
   ```

3. Activate the environment:
   ```
   conda activate peeringdb-env
   ```

4. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

   If you encounter dependency conflicts, try the following:
   
   a. First, install NumPy:
      ```
      pip install "numpy>=1.23.5,<2.0.0"
      ```
   
   b. Then, install the remaining dependencies:
      ```
      pip install -r requirements.txt
      ```

   c. If you still face issues, you can try installing the dependencies while ignoring conflicts (use with caution):
      ```
      pip install -r requirements.txt --ignore-installed
      ```

## Usage

1. Open the `peeringdb_data_extractor.py` file and replace `<api-key>` with your PeeringDB API key.

2. Run the script:
   ```
   python peeringdb_data_extractor.py
   ```

3. The output files (JSON and CSV) will be generated in the script directory.

## Project Structure

- `peeringdb_data_extractor.py`: Main script
- `requirements.txt`: List of project dependencies
- `README.md`: This file

## Output

The script generates the following files:

- `ix_data.json` and `ix_data.csv`: IX data in Brazil
- `merged_ixfac_fac_data.json` and `merged_ixfac_fac_data.csv`: Merged IXFAC and FAC data

## Troubleshooting

If you encounter errors related to dependency conflicts, try the following solutions:

1. Update your Anaconda environment:
   ```
   conda update --all
   ```

2. If you're using a virtual environment, consider creating a new environment and installing the dependencies in it.

3. Check for conflicts with globally installed packages. You can list all installed packages with:
   ```
   pip list
   ```
   
   Then uninstall problematic packages that are not necessary for this project.

4. If the problem persists, consider reporting the issue by creating an issue in the project repository.

## Contributing

Contributions are welcome! Please open an issue to discuss proposed changes or submit a pull request.

## License

This project is licensed under the [GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.en.html).

This license ensures that the software remains free and open source. Any derivative software or software that uses this code must also be distributed under the terms of the GPL-3.0. For more details, please refer to the LICENSE file in the repository or visit the license link above.
