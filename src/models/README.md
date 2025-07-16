# Model Files

This directory contains the AI models used for spam detection. Large model files are stored using **Git LFS (Large File Storage)** for efficient version control.

## Model Files (Git LFS Tracked)

### 1. IndoBERT Model
- **File**: `model.safetensors` (~475 MB) ✅ **Git LFS**
- **Description**: Fine-tuned IndoBERT model for Indonesian spam detection
- **Status**: Automatically downloaded when cloning repository

### 2. Model Archive
- **File**: `indobert-judul-classifier.zip` (~440 MB) ✅ **Git LFS**
- **Description**: Complete model package with tokenizer and configuration
- **Status**: Automatically downloaded when cloning repository

### 3. Training Arguments
- **File**: `training_args.bin` (~1 KB) ✅ **Git LFS**
- **Description**: Training configuration and hyperparameters
- **Status**: Automatically downloaded when cloning repository

### 4. Configuration Files (Regular Git)
- **File**: `vocab.txt` (~220 KB)
- **File**: `config.json` (~1 KB)
- **File**: `tokenizer_config.json` (~1 KB)
- **File**: `special_tokens_map.json` (~1 KB)
- **Description**: Model configuration files (included in regular Git)

## Setup Instructions

### For Users (Cloning Repository):
1. **Clone repository with Git LFS**:
   ```bash
   git clone https://github.com/Oatse/IndoBert-AI-based-Online-Gambling-Comment-Moderation-System.git
   cd IndoBert-AI-based-Online-Gambling-Comment-Moderation-System
   ```

2. **Verify model files are downloaded**:
   ```bash
   ls -la python/models/
   # Should show all files including large model files
   ```

3. **If LFS files not downloaded automatically**:
   ```bash
   git lfs pull
   ```

### For Developers (Contributing):
1. **Install Git LFS** (if not already installed):
   ```bash
   git lfs install
   ```

2. **Large files are automatically tracked**:
   - `*.safetensors` files
   - `*.bin` files
   - `*.zip` files in `python/models/`

3. **Add and commit normally**:
   ```bash
   git add python/models/
   git commit -m "Update model files"
   git push
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

- `model.safetensors`: ~475 MB ✅ **Git LFS**
- `indobert-judul-classifier.zip`: ~440 MB ✅ **Git LFS**
- `training_args.bin`: ~1 KB ✅ **Git LFS**
- `vocab.txt`: ~220 KB (regular Git)
- `config.json`: ~1 KB (regular Git)
- `tokenizer_config.json`: ~1 KB (regular Git)
- `special_tokens_map.json`: ~1 KB (regular Git)
- **Total LFS**: ~915 MB
- **Total Regular**: ~223 KB

## Git LFS Benefits

- ✅ **Version Control**: Full version history for large files
- ✅ **Efficient Cloning**: Only download LFS files when needed
- ✅ **Bandwidth Optimization**: LFS files downloaded separately
- ✅ **Team Collaboration**: Easy sharing of large model files
- ✅ **GitHub Integration**: Native support for LFS in GitHub

## Notes

- Large model files are now tracked with Git LFS
- Files automatically download when cloning repository
- Use `git lfs pull` if files don't download automatically
- LFS provides efficient storage and bandwidth usage for large files
