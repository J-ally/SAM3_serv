# SAM3 Video Segmentation Pipeline

This repository implements a **complete video segmentation and cropping pipeline** built on top of **SAM3 (Segment Anything Model 3)**.

It allows you to:
- split long videos into short clips
- segment objects from a **text prompt**
- track those objects across the full clip
- generate per-object cropped output videos

This repository acts as an **orchestration layer** around the official **SAM3** repository.

---

##  Features

- Long video clipping into fixed-length clips
- Text-prompt–guided video segmentation (SAM3)
- Multi-frame instance tracking
- Per-frame bounding box extraction
- Video cropping with padding and black background
- Explicit GPU (CUDA) memory management

---

##  Requirements

### Environment

- **Python 3.12 (required)**
- NVIDIA GPU recommended (CUDA)

Create a virtual environment:

```bash
conda create -n sam3-pipeline python=3.12
conda activate sam3-pipeline
```

---

##  Python Dependencies

```txt
opencv-python
einops
decord
pycocotools
scikit-image
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

##  External Dependency: SAM3

SAM3 is **not distributed on PyPI** and must be cloned from the official repository.

### Official repository

 https://github.com/facebookresearch/sam3

### Installation

```bash
git clone https://github.com/facebookresearch/sam3.git
pip install -e sam3
```

The `sam3/` directory must be present **at the same level as this repository** or otherwise available in your `PYTHONPATH`.

---
##  Access Requirements (Hugging Face)

SAM3 is a **gated model** hosted on Hugging Face.  
Before using this pipeline, you must **request access** and **authenticate locally**.

### 1- Request access to SAM3

You must request access on the official SAM3 Hugging Face page  
(approval required by Meta / Facebook Research).

> ⚠️ Without approval, the model weights cannot be downloaded.

### 2- Authenticate with your Hugging Face account

Once access is granted, log in locally:

```bash
huggingface-cli login
```
---

##  Running the Pipeline

The main entry point is:

```bash
python main.py
```

### Configuration

Pipeline parameters are defined in `config.py`:

```python
INPUT_FOLDER = "/path/to/input/videos"
CLIP_FOLDER = "/path/to/clips"
CROP_FOLDER = "/path/to/crops"

NUM_FRAMES_PER_CLIP = 20
FRAME_STEP = 4
PADDING = 20
PROMPT_CLASS = "cow"
```

---

##  Repository Architecture

### Directory Structure

```text
repo/
├── main.py                 # Global pipeline orchestration
├── config.py               # Global configuration
├── requirements.txt
│
├── sam/                     # SAM3 wrapper
│   ├── sam_session.py       # SAM3 video session handling
│   └── __init__.py
│
├── video/                   # Video processing utilities
│   ├── clipper.py           # Video clipping
│   ├── cropper.py           # Bounding boxes, cropping, video writing
│   └── __init__.py
│
├── pipeline/
│   ├── extractor.py         # SAM → BBox → Crop pipeline
│   └── __init__.py
│
├── sam3/                    # Official SAM3 repository (git clone)
└── README.md
```

---

##  Architecture Diagram

```text
┌────────────────────┐
│   Input Videos     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  video/clipper     │  Video clipping
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  SAMSession        │  (sam/sam_session.py)
│  - start_session   │
│  - add_prompt      │
│  - propagate       │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ pipeline/extractor │
│ - masks → bbox     │
│ - padding          │
│ - crop             │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Cropped Videos    │
└────────────────────┘
```

---


## 📄 License

This repository provides an application-level pipeline.

The model weights and license are defined by the official **SAM3 (Facebook Research)** repository.

---

##  References

- SAM3: https://github.com/facebookresearch/sam3
- Segment Anything: https://github.com/facebookresearch/segm

