# ALM Optimizer

## **Short introduction to ALM**

Asset and liability management (often abbreviated ALM) is the practice of managing financial risks that arise due to mismatches between the assets and liabilities as part of an investment strategy in financial accounting.

ALM sits between risk management and strategic planning. It is focused on a long-term perspective rather than mitigating immediate risks and is a process of maximising assets to meet complex liabilities that may increase profitability.

ALM includes the allocation and management of assets, equity, interest rate and credit risk management including risk overlays, and the calibration of company-wide tools within these risk frameworks for optimisation and management in the local regulatory and capital environment.

---

## **Inputs**
The required inputs to this pipeline are:
- A complete set of Assets with the following mandatory fields:
    
    - Portfolio
    - Maturity Date
    - ISIN
    - Nominal
    - Coupon Rate
    

- A Cash Flow projection of the liabilities by portfolio.


## **Suggested Structure:**

### :baby: **Status**
Ironhack Data Analytics Final Project

### :running: **One-liner**
ALM optimizer that provides a restructuring proposal: set of assets to sell and to purchase with the aim to improve pattern. 

### :computer: **Technology stack**
Python, Pandas, Numpy and Matplotlib.

### :boom: **Core technical concepts and inspiration**
Why does it exist? Automatization of manual task of perform elegible bonds to restructure a portfolio. 

### :file_folder: **Folder structure**
```
└── project
    ├── __trash__
    ├── .gitignore
    ├── .env
    ├── README.md
    ├── main_script.py
    ├── p_acquisition    
    │   └──  m_acquisition.py           
    ├── p_analysis    
    │   └──  m_analysis.py 
    ├── p_reporting    
    │   └──  m_reporting.py     
    ├── p_wrangling    
    │   └──  m_wrangling.py                
    ├── notebooks
    │   ├── notebook1.ipynb
    │   └── notebook2.ipynb
    └── data
        ├── raw
        ├── processed
        └── results
```

> Do not forget to include `__trash__` and `.env` in `.gitignore` 

### :shit: **ToDo**
Improvements in visualization.

### :love_letter: **Contact info**
For any comment and suggestion: jmiguelgonzalez1989@gmail.com

---