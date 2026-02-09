# 🚀 Startup Success Prediction through Data Driven Investment Analysis – End-to-End ML Pipeline

## 📌 Project Overview
This project builds an end-to-end Machine Learning pipeline to predict whether a startup will be **successful (1)** or **failed (0)** based on historical features such as funding, rounds, founding year, category, region, etc. The system outputs both:
- ✅ Binary prediction (Success / Failure)
- 📊 Probability of success



---

## 🧠 Problem Statement
Predict startup success using supervised machine learning by learning patterns from historical startup data. The project also explores a continuous success score using regression (SVR).



---

## 🏗️ Project Pipeline (High Level)
1. Import Libraries & Load Data  
2. Data Preprocessing & Feature Engineering  
3. Exploratory Data Analysis (EDA)  
4. Train-Test Splitting  
5. Model Selection & Training  
6. Model Evaluation  
7. Best Model Selection  
8. Final Prediction System  



---

## 📥 Step 1: Import Libraries & Load Dataset
- Import required libraries  
- Load dataset  
- Preview dataset  
- Create a working copy  
- Inspect dataset info and summary statistics  



---

## 🧹 Step 2: Data Preprocessing & Feature Engineering

### 🔸 Drop Noisy / Leaky Columns
- `permalink`, `name`, `homepage_url`, `status`

### 🔸 Handle Missing Values
- Numeric → fill with median (or 0 if median is NaN)  
- Categorical → fill with `"Unknown"`  
- Replace `inf`, `-inf` with NaN and re-handle  
- Clean categorical strings (`'nan'`, `'None'`, `'NaT'` → NaN)

### 🔸 Encoding Categorical Variables
- Low cardinality (<20 unique) → One-hot encoding  
- High cardinality → Frequency encoding  

### 🔸 Feature Engineering
- `startup_age = CURRENT_YEAR - founded_year` (clip negative to 0)  
- `funding_per_round = funding_total_usd / (funding_rounds + 1)`  
- `rounds_per_year = funding_rounds / (startup_age + 1)`  
- `funding_per_employee = funding_total_usd / (num_employees + 1)`  
- `funding_span_days = last_funding_at - first_funding_at` (if available)

### 🔸 Category Simplification
- Extract first category from `category_list` as `category_first`

### 🔸 Prevent Data Leakage
- Drop raw date columns: `founded_at`, `first_funding_at`, `last_funding_at`

### 🔸 Input Alignment for Prediction
- Align single-record input with training columns  
- Fill missing columns with 0  
- Apply same encoding as training



---

## 📊 Step 3: Exploratory Data Analysis (EDA)

### ✔ Missing Value Analysis
- Count + percentage of missing values  
- Visualized with bar chart  

### ✔ Target Distribution
- Class balance: Success (1) vs Failure (0)  

### ✔ Numeric Feature Distribution
- Histograms: `funding_total_usd`, `funding_rounds`, `founded_year`, etc.

### ✔ Outlier Detection
- Boxplots for numeric features  

### ✔ Categorical Feature Success Rate
- Success rate by `market`, `country_code`, `region`, `founded_quarter`  

### ✔ Correlation Analysis
- Correlation heatmap for numeric features  



---

## 🔀 Step 4: Train-Test Split

- Time-based split if `founded_year` exists  
- Else stratified random split  
- 80% training, 20% testing  
- `y_all` = target (success)  
- `X_all` = features  
- Scaling applied later only for models that need it  



---

## 🤖 Step 5: Model Selection

### 📌 Classification Models
- Logistic Regression  
- Random Forest  
- Support Vector Classifier (RBF kernel)  
- XGBoost Classifier  

### 📌 Regression Model
- Support Vector Regression (SVR)  
  - Predicts continuous success probability  
  - Clamped to [0,1] for evaluation  

### 📌 Feature Scaling
- Logistic Regression, SVC, SVR → Scaled  
- Random Forest, XGBoost → Raw features  



---

## 🏋️ Step 6: Model Training

- Train all models using `.fit()`  
- Handle class imbalance using `class_weight="balanced"`  
- No hyperparameter tuning (stable defaults used)  
- Tree models trained on raw data  
- Linear / kernel models trained on scaled data  



---

## 📈 Step 7: Model Evaluation

### ✔ Classification Metrics
- Accuracy  
- Precision  
- Recall  
- F1-score  
- ROC-AUC  

### ✔ Evaluation Outputs
- Comparison table of all models  
- ROC curve of best model  
- ROC-AUC bar chart for all models  

### ✔ Regression Evaluation (SVR)
- ROC-AUC on continuous predictions  
- Thresholded predictions for classification-style metrics  



---

## 🏆 Step 8: Best Model Selection

- Compare all models using ROC-AUC  
- Select model with highest ROC-AUC  
- Retrain best model on full training data  
- Use tree models (Random Forest / XGBoost) for feature importance & explainability  



---

## 🎯 Final Output

The final model:
- Predicts startup success or failure  
- Returns probability of success  
- Can be applied to new startup records  



---

## 🧰 Tech Stack

- **Language:** Python  
- **ML:** scikit-learn, XGBoost  
- **EDA:** Pandas, NumPy, Matplotlib, Seaborn  
- **Model Storage:** joblib  
- **Backend (optional):** FastAPI / Flask  
- **Frontend (optional):** React / HTML + Tailwind  

---

## 📌 Future Enhancements

- Deploy as a web app (FastAPI + React)  
- Add explainability (SHAP)  
- Add model versioning  
- Add logging & monitoring  
- Dockerize services  

---

## 📄 License
For academic and learning purposes.
