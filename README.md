# 🎵 ArtistRoyaltyTracker

> **Find unclaimed royalties by matching Spotify catalogs with the MLC database**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

**ArtistRoyaltyTracker** is a Python tool that cross-references Spotify artist catalogs with the MLC unclaimed works database to identify potential royalty recovery opportunities.

---

## 🚀 Quick Setup

### 1. Install
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Spotify API
Create `.env` file:
```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```
Get credentials: https://developer.spotify.com/dashboard

### 3. Add Dataset
Download `unclaimedmusicalworkrightshares.tsv` (6.7GB) → place in `data/` folder  
Source: https://www.themlc.com/

### 4. Run Analysis
```powershell
python run_analysis.py                              # Default (Coldplay)
python run_analysis.py --artist "Taylor Swift"      # Different artist
python run_analysis.py --artist "Ed Sheeran" --output "reports/ed.xlsx"
```

### 5. Check Results
Excel file in `output/` folder with: Catalog, Matches, Summary, Notes sheets

---

## 📊 Example Output

**ArtistRoyaltyTracker** execution:

```
Step 1/5: Authenticating... ✅
Step 2/5: Loading dataset... ✅ 40M+ records
Step 3/5: Finding artist... ✅ Found
Step 4/5: Fetching catalog... ✅ 150 tracks
Step 5/5: Matching ISRCs... ✅ 23 matches

Summary: 150 tracks | 23 matches (15.3%)
Report: output/artist_unclaimed_report.xlsx
```

---

## 📁 Project Structure

```
ArtistRoyaltyTracker/
├── config/settings.py           # Configuration
├── data/*.tsv                   # MLC dataset (6.7GB)
├── output/*.xlsx                # Reports
├── src/
│   ├── main.py                 # Orchestrator
│   └── utils/                  # Core modules
│       ├── dataset_loader.py
│       ├── spotify_handler.py
│       ├── analysis_engine.py
│       └── excel_exporter.py
├── run_analysis.py             # CLI launcher
└── requirements.txt            # Dependencies
```

---

## ⚙️ Configuration

Edit `config/settings.py`:
```python
CHUNK_SIZE = 500000      # Rows per chunk (lower if RAM issues)
MEMORY_EFFICIENT = True  # Enable chunked processing
MAX_RETRIES = 3         # API retry attempts
```

---

## 🚀 Performance

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Memory | 6-8 GB | 500 MB - 1.5 GB | **85% ⬇️** |
| Load Time | 8-12 min | 2-5 min | **60% ⚡** |
| Lookup | O(n) Sequential | O(1) Hash | **Instant** |

---

## 🐛 Quick Fixes

| Issue | Solution |
|-------|----------|
| Memory Error | Reduce `CHUNK_SIZE` in `config/settings.py` |
| Auth Failed | Check `.env` credentials (no spaces around `=`) |
| Artist Not Found | Verify exact spelling on Spotify |
| File Not Found | Ensure dataset in `data/` folder |
| Slow Performance | Use SSD + close apps + increase chunk if 8GB+ RAM |

---

## 💻 Python API

```python
from src.main import MusicRightsAnalyzer

analyzer = MusicRightsAnalyzer(
    artist_name="Taylor Swift",
    output_path="reports/taylor.xlsx"
)
analyzer.run()
```

---

## 🎯 Use Cases

**ArtistRoyaltyTracker** helps:

✅ Artists finding unclaimed royalties  
✅ Rights organizations auditing catalogs  
✅ Legal teams identifying claims  
✅ Researchers analyzing music data

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup guide
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Code organization

---

## 🤝 Contributing

Help improve **ArtistRoyaltyTracker**:

- 🌐 Web interface • 📊 Visualizations • 🔍 Fuzzy matching  
- 🧪 Unit tests • 📱 REST API • 🐳 Docker support

---

## 🙏 Credits

**Spotify Web API** • **MLC Database** • **pandas** • **spotipy**

---

## 📄 License

**ArtistRoyaltyTracker** is licensed under MIT License - Free to use and modify

---

<div align="center">

**Made with ❤️ for the music industry**

⭐ **Star if useful!** • [Setup](#-quick-setup) • [Docs](#-documentation) • [Fixes](#-quick-fixes)

</div>
