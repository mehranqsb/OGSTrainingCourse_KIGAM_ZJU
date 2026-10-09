# OpenGeoSys Training Course 2026

**Numerical Modelling of Coupled Thermo-Hydro-Mechanical Processes in Geological Media**

Installation materials for the joint October 2026 OpenGeoSys training course involving UFZ, KIGAM, Zhejiang University, and TU Bergakademie Freiberg (TUBAF).

The course introduces finite element modelling in geomechanics, the OpenGeoSys workflow, model setup and constitutive models, coupled hydro-mechanical and thermo-hydro-mechanical simulations, and post-processing. It is intended for researchers, engineers, graduate students, and professionals in geotechnical engineering and computational geosciences.

Start with the [Installation and Course Environment Manual](Docs/ogs_installation.pdf). The repository also contains three course exercise notebooks with mesh and project generators, plus a fourth notebook that trains PyTorch constitutive models on OGS results.

## Run the course examples in your browser

[Open all examples on Binder](https://mybinder.org/v2/gh/mehranqsb/OGSTrainingCourse_KIGAM_ZJU/binder).

Additional launch link: [Open the course on OpenGeoSys Binder](https://binder.opengeosys.org/v2/gh/mehranqsb/OGSTrainingCourse_KIGAM_ZJU/binder).

Binder links launch the lightweight `binder` branch, which contains the three
examples and online dependencies. The `main` branch retains the offline installers
and wheelhouses. Changes on `main` do not automatically update `binder`.

No local OGS installation is required. In JupyterLab's left file browser, open
folder 01, 02, or 03 and double-click its notebook, then select **Run → Run All Cells**.

| Example | Browser launch |
| --- | --- |
| 01 — Tunnel excavation / Kirsch | [Launch 01](https://mybinder.org/v2/gh/mehranqsb/OGSTrainingCourse_KIGAM_ZJU/binder?labpath=01_Tunnel_Excavation_Kirsch%2F01_tunnel_excavation_kirsch.ipynb) |
| 02 — Fault-controlled injection / LIE–EFPM | [Launch 02](https://mybinder.org/v2/gh/mehranqsb/OGSTrainingCourse_KIGAM_ZJU/binder?labpath=02_LIE_EFPM_Fault-Controlled_Injection%2F02_lie_efpm_injection.ipynb) |
| 03 — Heated tunnel / TRM | [Launch 03](https://mybinder.org/v2/gh/mehranqsb/OGSTrainingCourse_KIGAM_ZJU/binder?labpath=03_TRM_Heated_Tunnel_FE_Experiment%2F03_trm_heated_tunnel.ipynb) |
| 04 — AI constitutive model / plate (OGS + PyTorch) | Local only: needs PyTorch, see [04_AI_Constitutive_Plate/README.md](04_AI_Constitutive_Plate/README.md) |

The `.binder/` directory configures Python 3.11, OGSTools 0.8, the OGS executable,
Gmsh, and the native libraries needed by Gmsh. The build checks imports and the
OGS version before launching. Binder installs packages online; the platform-specific
Python 3.13 offline wheelhouses are for local course installations.

After a new commit, Binder may rebuild its image and reinstall dependencies.
The first build can take several minutes; later launches of the same commit
usually reuse the image. Session startup, service demand, cache availability,
and this repository's large offline bundles can add time. Expand **Show build logs**
to follow progress. Bookmark the permanent launch link, rather than the temporary
Jupyter session address. A direct notebook link needs a complete `?labpath=...` value.

Binder sessions are temporary. Download results and edited notebooks before leaving.
Example 03 runs multiple coupled simulations and may need considerable time and
memory. Full Binder simulation runs have not yet been verified for this repository.

### Reuse a shared Binder environment (Lars's recommendation)

Lars recommends keeping the environment (tool installation and dependencies) in
one repository and the notebooks and data in another. With the direct course
links above, a new notebook commit can trigger a new image build, which takes
time. Separating the repositories allows notebook updates to reuse the existing
environment image.

Use the [shared OGS environment repository](https://github.com/bilke/binder-ogs-requirements),
which Lars identifies as the environment used by the OGS website:

[Launch the course with the shared OGS environment](https://binder.opengeosys.org/v2/gh/bilke/binder-ogs-requirements/6.5.9-0.8.2?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252Fmehranqsb%252FOGSTrainingCourse_KIGAM_ZJU%26urlpath%3Dlab%252Ftree%252FOGSTrainingCourse_KIGAM_ZJU%252F..%252Fdata%26branch%3Dbinder%26targetPath%3Ddata).

This link selects environment version `6.5.9-0.8.2` and uses nbgitpuller to fetch
the course repository's `binder` branch into `data`, then opens it in JupyterLab.
After updating the notebooks on that branch, open the same link again to pull
the updated content. Notebook-only changes do not require rebuilding the shared
environment image, so launches can be faster once that image is available;
session startup still depends on service demand and cache availability.

To create or adjust a launch link, use the
[nbgitpuller link generator](https://nbgitpuller.readthedocs.io/en/latest/link.html)
with these settings:

| Setting | Value |
| --- | --- |
| Binder service | `https://binder.opengeosys.org` |
| Environment repository | `https://github.com/bilke/binder-ogs-requirements` |
| Environment branch/tag | `6.5.9-0.8.2` |
| Content repository | `https://github.com/mehranqsb/OGSTrainingCourse_KIGAM_ZJU` |
| Content branch | `binder` |
| File to open | `../data` |
| Target path | `data` |
| Application | JupyterLab |

![Lars's annotated nbgitpuller link generator example showing the shared OGS environment and course repository settings](Docs/images/nbgitpuller-binder-link-generator.png)

Lars's example: select the **Binder** tab, enter the settings above, and copy the
generated link.

## Repository contents

| Path | Purpose |
| --- | --- |
| [Docs/ogs_installation.pdf](Docs/ogs_installation.pdf) | Detailed installation manual for Ubuntu, macOS, and Windows, including offline bundle preparation and optional VS Code setup. |
| [Docs/ogs_installation.tex](Docs/ogs_installation.tex) | LaTeX source of the manual. |
| [Project_Idea_Report/project_idea_report.pdf](Project_Idea_Report/project_idea_report.pdf) | Project idea report on physics-constrained AI constitutive models for rock, soil, Martian regolith and 3D-printed geomaterials; LaTeX source alongside. |
| `Docs/tubaf-report.cls`, `Docs/tubaf-*.sty` | TUBAF document class, fonts, colours, logos, and page layout. |
| `Docs/UFZ_KIGAM_ZJU.pdf` | Logo artwork used by the manual. |
| `Docs/ogs_installation.*` (other extensions) | Generated LaTeX auxiliary files and build logs. |
| [install_ogstools_windows.bat](install_ogstools_windows.bat) | Windows online/offline installer. |
| [install_ogstools_macos.command](install_ogstools_macos.command) | Apple Silicon macOS online/offline installer. |
| `python-3.13.15-amd64.exe` | Bundled Python installer for 64-bit x86 Windows. |
| `python-3.13.15-macos11.pkg` | Bundled Python universal2 installer for macOS. |
| `wheelhouse_windows/` | Python wheels for Windows x86-64 and CPython 3.13, plus a `SHA256SUMS` checksum list. |
| `wheelhouse_macos_arm64/` | Python wheels for Apple Silicon and CPython 3.13, plus a `SHA256SUMS` checksum list. |
| `wheelhouse_ubuntu/` | Python wheels for Linux x86-64 and CPython 3.13, plus a `SHA256SUMS` checksum list. |
| [python_packages.txt](python_packages.txt) | Ubuntu/Debian system-package names collected for Python setup; **not a pip requirements file**. |

The wheelhouses contain 172 (Ubuntu), 175 (macOS), and 174 (Windows) wheels. The counts differ because each wheelhouse also carries the dependencies that Jupyter needs only on that platform: `appnope`, `pyobjc-core`, and `pyobjc-framework-Cocoa` on macOS, and `colorama` and `pywinpty` on Windows. Every wheelhouse includes a `SHA256SUMS` file listing the checksum of each wheel. The `Docs/` folder also contains copies of both installer scripts. **Use the root-level scripts**: they locate the wheelhouse and create `.venv_ogs` beside themselves, while the supplied wheelhouses are at the repository root.

## Course environment

| Component | Version in the supplied bundle |
| --- | --- |
| CPython | 3.13; Windows/macOS installer filenames specify 3.13.15 |
| OpenGeoSys (`ogs`) | 6.5.9 |
| OGSTools (`ogstools[all]`) | 0.8.2 |
| Jupyter Notebook | 7.6.3 |
| JupyterLab | 4.6.4 |

The installation commands pin OGS and OGSTools. Notebook, JupyterLab, and other dependencies are not pinned in the online commands, so online installation may select different versions from the bundled wheels.

The supplied installation targets are:

- **Windows:** x86-64 Windows with 64-bit Python 3.13, pip, and the Python launcher (`py`).
- **macOS:** Apple Silicon, macOS 26 or newer, and native ARM64/universal2 Python 3.13. The bundled OGS wheel is tagged `macosx_26_0_arm64`; the Python installer's `macos11` filename does not lower this OGS requirement. This bundle does not support Intel Macs.
- **Ubuntu:** the manual targets Ubuntu 24.04 on x86-64, with Python 3.13 installed alongside the system Python. The wheels are for CPython 3.13; using a different Python minor version requires a matching wheelhouse.

## Download from GitHub (Git LFS)

The Ubuntu and Windows wheels in `wheelhouse_ubuntu/` and `wheelhouse_windows/`, together with the Windows Python installer (`python-3.13.15-amd64.exe`), are stored using **Git Large File Storage (Git LFS)**. Install Git and [Git LFS](https://git-lfs.com/) on the connected computer before downloading the repository. Running `git lfs install` configures an already installed Git LFS client; it does not install the client itself.

### New clone

```bash
git lfs install
git clone https://github.com/mehranqsb/OGSTrainingCourse_KIGAM_ZJU.git
cd OGSTrainingCourse_KIGAM_ZJU
git lfs pull
```

The clone normally downloads LFS objects automatically. The explicit `git lfs pull` also retrieves any objects whose download was skipped. This clone directory is the repository root used by the installation commands below.

### Existing clone

Open a terminal in your existing repository and run:

```bash
git lfs install
git pull --ff-only
git lfs pull
```

### Check before transferring offline

```bash
git lfs ls-files
git lfs fsck
```

Then verify the wheels of your platform against the bundled checksum list, for example:

```bash
cd wheelhouse_ubuntu   # or wheelhouse_macos_arm64, wheelhouse_windows
sha256sum -c SHA256SUMS
```

On macOS use `shasum -a 256 -c SHA256SUMS`. On Windows PowerShell, individual files can be checked with `Get-FileHash <file> -Algorithm SHA256` and compared with the listed value. Every line should report `OK`; a mismatch or a missing file means the download is incomplete.

The Ubuntu and Windows binary entries in `git lfs ls-files` should show `*`, indicating full files in the working directory, rather than `-`, indicating LFS pointers. `git lfs fsck` checks the local LFS objects for integrity.

Complete the download while connected to the internet before copying the files to an offline computer. Small text files beginning with `version https://git-lfs.github.com/spec/v1` are pointers, not installable wheels; run `git lfs pull` to retrieve the actual packages. Use the clone workflow above for the offline bundle: GitHub's **Download ZIP** may contain pointers depending on the repository's archive settings.

## Installation

Download or copy the repository, including the wheelhouse for your platform. Run the commands below from the repository root. The Windows and macOS scripts create or reuse `.venv_ogs`, install the packages, and verify OGSTools, the OGS executable, and Jupyter Notebook.

### Windows

1. Run `python-3.13.15-amd64.exe`. Enable the Python launcher and pip; select **Add Python to PATH**.
2. Open PowerShell in the repository root and check Python:

   ```powershell
   py -3.13 --version
   py -3.13 -m pip --version
   ```

3. Choose one installation mode:

   ```powershell
   # Use the bundled wheels without contacting a package index:
   .\install_ogstools_windows.bat offline

   # Or download packages using an internet connection:
   .\install_ogstools_windows.bat online
   ```

Double-clicking the batch file, or omitting its argument, selects **online** mode. A successful run ends with `Installation succeeded`.

### macOS (Apple Silicon)

1. Run `python-3.13.15-macos11.pkg` and reopen a native Terminal.
2. Check the operating system, Python version, and architecture:

   ```bash
   sw_vers -productVersion
   uname -m
   python3.13 --version
   python3.13 -c "import platform; print(platform.machine())"
   ```

   macOS must be version 26 or newer, and both architecture checks must report `arm64`.

3. From the repository root, choose one installation mode:

   ```bash
   chmod +x install_ogstools_macos.command

   # Use the bundled wheels:
   ./install_ogstools_macos.command offline

   # Or download packages using an internet connection:
   ./install_ogstools_macos.command online
   ```

Double-clicking the executable `.command` file, or omitting its argument, selects **online** mode.

### Ubuntu (x86-64)

There is no Ubuntu installer script. First provide Python 3.13 and its `venv` module using the Ubuntu setup procedure in the [manual](Docs/ogs_installation.pdf). Keep the operating system's Python unchanged.

From the repository root:

```bash
python3.13 --version
python3.13 -m venv .venv_ogs
source .venv_ogs/bin/activate
```

For installation from the bundled wheels:

```bash
python -m pip install --no-index --find-links ./wheelhouse_ubuntu \
  "ogs==6.5.9" "ogstools[all]==0.8.2" notebook jupyterlab
```

Alternatively, for online installation:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install "ogs==6.5.9" "ogstools[all]==0.8.2" notebook jupyterlab
```

**Ubuntu offline prerequisite:** this repository does not contain a `python_debs/` directory or any `.deb` packages. If Python 3.13 and its `venv` module are not already available, prepare those system packages on a connected computer with the same Ubuntu release and architecture, following the manual. `python_packages.txt` is only a package-name list, not an installable bundle. Regenerate it for the target system; the current file also contains the virtual package name `debconf-2.0`, which the manual's preparation procedure replaces with `debconf`.

## Start Jupyter and use the environment

From the repository root, launch Notebook directly without activating the environment:

**Windows (PowerShell):**

```powershell
.\.venv_ogs\Scripts\jupyter.exe notebook
```

**macOS / Ubuntu:**

```bash
./.venv_ogs/bin/jupyter notebook
```

Replace `notebook` with `lab` to start JupyterLab. Keep the terminal open while using Jupyter; press `Ctrl+C` and follow the prompt to stop it.

To use `python`, `ogs`, and `jupyter` directly in a terminal, activate the environment first:

| Shell | Activation command |
| --- | --- |
| Windows PowerShell | `.\.venv_ogs\Scripts\Activate.ps1` |
| Windows Command Prompt | `.venv_ogs\Scripts\activate.bat` |
| macOS / Ubuntu | `source .venv_ogs/bin/activate` |

Run `deactivate` when finished. If PowerShell blocks activation, the direct executable commands above still work.

VS Code is optional and is not bundled. The manual describes installation of the editor and its Python and Jupyter extensions. Select `.venv_ogs` as both the Python interpreter and notebook kernel.

## Verify the installation

With the environment activated, run:

```bash
python -c "from importlib.metadata import version; print('OGS:', version('ogs')); print('OGSTools:', version('ogstools'))"
python -c "import ogstools as ot; assert ot.status(verbose=True)"
ogs --version
jupyter notebook --version
python -m pip check
```

The package versions should report OGS `6.5.9` and OGSTools `0.8.2`. The Windows and macOS scripts already run the version, OGSTools status, and executable checks; `pip check` is an additional dependency check.

Inside a notebook, confirm the selected environment with:

```python
import sys
from importlib.metadata import version

print(sys.executable)
print(version("ogstools"))
```

The interpreter path should point into this repository's `.venv_ogs` directory.

## Offline bundles and troubleshooting

- Keep the complete wheelhouse for your target platform beside the root installer. Offline mode uses `--no-index` and fails if a required compatible package is unavailable.
- If offline installation reports `No matching distribution found`, check the wheelhouse against its `SHA256SUMS` file to find wheels that are missing or damaged.
- Wheelhouses contain Python packages, not Python itself. The Windows and macOS Python installers are supplied separately; Ubuntu system packages must be prepared separately.
- If Windows cannot find `py -3.13`, check that Python 3.13 and the Python launcher were installed, then reopen the terminal.
- If the macOS installer rejects the machine, check the macOS version and ensure Terminal and Python run natively as `arm64`.
- For missing or incompatible wheels, check the Python minor version, operating system, and CPU architecture. Do not mix platform-specific wheelhouses.
- If an earlier attempt left an unusable environment, remove only the generated `.venv_ogs` directory and rerun the installation. Keep the course files and wheelhouses.
- For any failed verification, inspect the output immediately before the failure message.

The [manual](Docs/ogs_installation.pdf) contains procedures for rebuilding the offline bundles, including downloading Windows and macOS wheels from Ubuntu. The inventories and package metadata have been inspected; successful installation on every target platform still requires running the checks above on that platform.

## Rebuild the manual

The compiled PDF is included, so LaTeX is only needed when editing the manual. With a recent LaTeX distribution and `latexmk` installed:

```bash
cd Docs
latexmk -pdf ogs_installation.tex
```

Keep the local `tubaf-*.sty` files, `tubaf-report.cls`, and `UFZ_KIGAM_ZJU.pdf` beside the source. The document uses KOMA-Script, TikZ, TeX Gyre fonts, and the other packages declared in the source and style files. LaTeX compilation is separate from the Python course environment.

## Authors

Mehran Ghasabeh, Thomas Nagel, Olaf Kolditz

## Course contact

**Mehran Ghasabeh**

Institute of Geotechnics, TU Bergakademie Freiberg

[mehran.ghasabeh@ifgt.tu-freiberg.de](mailto:mehran.ghasabeh@ifgt.tu-freiberg.de)
