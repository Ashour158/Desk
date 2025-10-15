# GDAL Installation Guide for Windows

## Option 1: Using Conda (Recommended)

```bash
# Install Miniconda first from https://docs.conda.io/en/latest/miniconda.html
conda create -n helpdesk python=3.11
conda activate helpdesk
conda install -c conda-forge gdal
pip install -r requirements.txt
```

## Option 2: Using Pre-compiled Wheels

```bash
# Download GDAL wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
# Install the appropriate wheel for your Python version
pip install GDAL-3.6.4-cp311-cp311-win_amd64.whl
```

## Option 3: Using OSGeo4W

1. Download OSGeo4W from https://trac.osgeo.org/osgeo4w/
2. Install with GDAL and Python support
3. Add to PATH: `C:\OSGeo4W\bin`
4. Set environment variables:
   ```bash
   set GDAL_LIBRARY_PATH=C:\OSGeo4W\bin\gdal306.dll
   set GEOS_LIBRARY_PATH=C:\OSGeo4W\bin\geos_c.dll
   set PROJ_LIBRARY_PATH=C:\OSGeo4W\bin\proj.dll
   ```

## Option 4: Docker Development (Alternative)

```bash
# Use Docker for development with GDAL pre-installed
docker run -it --rm -v ${PWD}:/app -w /app osgeo/gdal:ubuntu-small-3.6.4 bash
```

## Verification

```python
# Test GDAL installation
import osgeo.gdal as gdal
print("GDAL version:", gdal.VersionInfo())
```

## For Production Deployment

Use the Docker approach or install GDAL on the production server:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev

# CentOS/RHEL
sudo yum install gdal gdal-devel

# Set environment variables
export GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
export GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so
```
