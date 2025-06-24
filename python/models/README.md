# Model Files

This directory contains the AI models used for spam detection. Due to file size limitations, the model files are not included in the Git repository.

## Required Model Files

### 1. IndoBERT Model
- **File**: `model.safetensors` (~475 MB)
- **Description**: Fine-tuned IndoBERT model for Indonesian spam detection
- **Download**: [Contact repository owner for download link]

### 2. Model Archive
- **File**: `indobert-judul-classifier.zip` (~440 MB)
- **Description**: Complete model package with tokenizer and configuration
- **Download**: [Contact repository owner for download link]

### 3. Vocabulary File
- **File**: `vocab.txt` (~220 KB)
- **Description**: Tokenizer vocabulary (included in repository)

## Setup Instructions

1. Download the required model files from the provided links
2. Place them in this directory (`python/models/`)
3. Ensure the following files exist:
   ```
   python/models/
   ├── model.safetensors
   ├── indobert-judul-classifier.zip
   ├── vocab.txt
   └── README.md (this file)
   ```

## Alternative: Using Git LFS

If you prefer to use Git LFS for large files:

```bash
# Install Git LFS
git lfs install

# Track large model files
git lfs track "python/models/*.safetensors"
git lfs track "python/models/*.zip"

# Add and commit
git add .gitattributes
git add python/models/
git commit -m "Add model files with Git LFS"
```

## Model Information

- **Base Model**: IndoBERT (Indonesian BERT)
- **Task**: Binary classification (spam/not spam)
- **Language**: Indonesian
- **Framework**: PyTorch/Transformers
- **Input**: Indonesian text comments
- **Output**: Spam probability (0-1)

## Usage

The models are automatically loaded by the spam detection service when the application starts. Make sure all required files are in place before running the application.

## File Sizes

- `model.safetensors`: ~475 MB
- `indobert-judul-classifier.zip`: ~440 MB
- `vocab.txt`: ~220 KB
- **Total**: ~915 MB

## Notes

- These files are excluded from Git tracking due to size limitations
- Consider using cloud storage or Git LFS for version control of large models
- Models should be downloaded separately during deployment
