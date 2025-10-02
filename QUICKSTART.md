"""
QUICK START GUIDE
=================

This guide will help you get started with the Music Rights Analysis Tool.

STEP 1: VERIFY SETUP
---------------------
✅ Python 3.8+ installed
✅ Virtual environment activated (.venv)
✅ Dependencies installed (requirements.txt)
✅ Spotify API credentials in .env file
✅ Dataset file in data/ directory

STEP 2: BASIC USAGE
-------------------

# Run analysis for default artist (Coldplay)
python run_analysis.py

# Analyze a different artist
python run_analysis.py --artist "Ed Sheeran"

# Specify custom output location
python run_analysis.py --artist "Taylor Swift" --output "output/custom_report.xlsx"

STEP 3: VIEW RESULTS
--------------------
# Check the output directory for the Excel report
# Report contains 4 sheets:
#   1. Artist Catalog - Full discography with ISRC codes
#   2. Matches - Tracks found in unclaimed database
#   3. Summary - Key metrics and statistics
#   4. Notes - Methodology and assumptions

STEP 4: EXPLORE DATA (OPTIONAL)
--------------------------------
# Use the TSV viewer to explore the dataset
python view_data.py

# Options in viewer:
#   1. View File Structure - See all columns
#   2. Preview First N Rows - View sample data
#   3. Search by ISRC Code - Find specific recordings
#   4. Get Dataset Statistics - Count rows
#   5. Export Sample Data - Create smaller test file
#   6. Exit

CONFIGURATION
-------------
# Edit config/settings.py to customize:

DEFAULT_ARTIST = "Your Artist Name"      # Change default artist
CHUNK_SIZE = 500000                      # Adjust for memory
RATE_LIMIT_DELAY = 0.1                   # Spotify API delay
VERBOSE = True                           # Show detailed progress

COMMAND LINE OPTIONS
--------------------
python run_analysis.py --help

Options:
  --artist ARTIST   Artist name to analyze (default: Coldplay)
  --output OUTPUT   Output Excel file path

TROUBLESHOOTING
---------------

Problem: "Spotify credentials not found"
Solution: Edit .env file with your API credentials

Problem: "Dataset file not found"
Solution: Place unclaimedmusicalworkrightshares.tsv in data/ directory

Problem: "Memory Error"
Solution: Increase CHUNK_SIZE in config/settings.py
          or close other applications

Problem: "API Rate Limit"
Solution: Increase RATE_LIMIT_DELAY in config/settings.py

EXPECTED RUNTIME
----------------
- Dataset Loading: 2-5 minutes
- Spotify Catalog: 2-10 minutes (depends on artist)
- Cross-Reference: 30 seconds - 2 minutes
- Total: ~5-15 minutes per artist

OUTPUT INTERPRETATION
---------------------

High Match Rate (>10%):
  → Many tracks in unclaimed database
  → Review for claiming opportunities

Low Match Rate (<5%):
  → Most tracks properly claimed
  → Good rights management

Zero Matches:
  → All tracks claimed or not in database
  → Still valuable to confirm

Unclaimed Percentage:
  → >50%: High priority for claiming
  → 25-50%: Moderate priority
  → <25%: Lower priority but still valuable

NEXT STEPS
----------
1. Open the Excel report
2. Review the "Matches" sheet
3. Sort by "unclaimed_UnclaimedRightSharePercentage" (descending)
4. Identify high-value tracks
5. Contact MLC or rights organization for claiming

SUPPORT
-------
For detailed documentation, see PROJECT_README.md

For technical details, see source code in src/ directory

For configuration options, see config/settings.py

EXAMPLES
--------

Example 1: Analyze Coldplay (default)
$ python run_analysis.py

Example 2: Analyze Ed Sheeran
$ python run_analysis.py --artist "Ed Sheeran"

Example 3: Custom output location
$ python run_analysis.py --artist "Adele" --output "reports/adele_2025.xlsx"

Example 4: View dataset
$ python view_data.py
> Choose option 1 (View Structure)
> Choose option 3 (Search ISRC: USUM72220001)

DIRECTORY STRUCTURE
-------------------
.
├── config/              # Configuration files
│   └── settings.py      # Main settings
├── data/                # Dataset location
│   └── *.tsv           # Unclaimed works data
├── output/              # Generated reports
│   └── *.xlsx          # Excel reports
├── src/                 # Source code
│   ├── main.py         # Main application
│   └── utils/          # Utility modules
├── .env                 # API credentials
├── run_analysis.py      # Main launcher
├── view_data.py         # Data viewer
└── PROJECT_README.md    # Full documentation

PERFORMANCE TIPS
----------------
1. Use SSD for faster dataset loading
2. Close other applications to free RAM
3. Adjust CHUNK_SIZE based on available memory
4. Enable MEMORY_EFFICIENT in config for large datasets
5. Use --output to save reports to SSD

SECURITY BEST PRACTICES
-----------------------
1. Never commit .env file to version control
2. Keep .gitignore up to date
3. Regenerate API credentials if exposed
4. Store sensitive data in data/ directory (gitignored)
5. Review .gitignore before committing

HAPPY ANALYZING! 🎵📊
"""