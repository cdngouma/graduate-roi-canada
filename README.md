## Project Description

This project analyzes the return on investment (ROI) of postsecondary education in Canada across different fields of study. By integrating data on tuition costs, graduate output, median income five years post-graduation, and labour market outcomes, we explore whether certain fields are oversaturated, undervalued, or in high demand. The goal is to provide insight into how education costs and labour outcomes align—helping inform students, educators, and policymakers about the long-term value of various educational paths.

### Key Questions Explored

- Are we graduating too many students in fields with limited job opportunities?
- Which fields offer the most stable employment or job growth over time?
- Are there education "bubbles"—fields with high tuition costs but low job prospects or earnings?
- How do wages and unemployment rates differ across fields of study?
- Which fields show the highest return on investment (income relative to tuition)?

## Data Preparation (ETL Pipeline)

The preprocessing steps were implemented in a modular Jupyter Notebook and follow a structured ETL (Extract, Transform, Load) approach:

### Extract

- Data is sourced from CSV files downloaded from Statistics Canada and other official open data sources.
- The datasets include:
  - Tuition costs (2006–2025)
  - Graduation counts by field and education level
  - Median income five years post-graduation
  - Labour market outcomes from the census (2011, 2016, 2021)

### Transform

- **Tuition Data**: Renamed columns, extracted the starting year from academic ranges (e.g., "2010/2011" becomes 2010), and filtered out aggregate categories. Education level was added to each row.
- **Graduation Data**: Cleaned field names, unified education levels (Bachelor's, Master's, Doctoral → Undergraduate, Graduate), and filtered for Canadian-wide data.
- **Income Data**: Removed summary categories (e.g., STEM, BHASE), standardized field names, and derived `Graduation Year` from `Survey Year - 5`.
- **Labour Data**: Parsed raw files for census years, removed metadata rows, standardized columns, and cleaned up annotations from field names.
- **Field of Study Normalization**: Applied a universal mapping across datasets to ensure consistent field names.
- **Education Level Unification**: For field-level analysis, education types were merged under a single "Postsecondary" category.
- **Aggregation**:
  - Graduates were summed per year and field.
  - Tuition was computed as a weighted average based on graduate counts.
  - Median income values were retained at the field-year level (not education-specific).
- **Census Alignment**: Each observation year was mapped to its nearest census year (2001, 2006, 2011, 2016, 2021, or 2026) to match labour force data.

### Load

- Cleaned and aggregated datasets were exported as CSV files for downstream analysis:
  - `postsecondary_field_outcomes.csv`: Combined tuition, graduates, and income data by field and year.
  - `postsecondary_labour_outcomes.csv`: Census-based labour indicators by field of study.