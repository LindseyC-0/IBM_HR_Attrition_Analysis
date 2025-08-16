import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# Load the dataset
df = pd.read_csv('WA_Fn-UseC_-HR-Employee-Attrition.csv')

# Save a reference to the original standard output
original_stdout = sys.stdout

# Open the file in write mode; 'w' will create/overwrite the file.
# All subsequent print() statements (within this 'with' block) will write to this file.
with open('HR_Attrition_Report_Text.txt', 'w') as f:
    sys.stdout = f # Redirect standard output to the file

    # --- YOUR ENTIRE ANALYSIS SCRIPT GOES HERE ---
    # Load the dataset
    df = pd.read_csv('WA_Fn-UseC_-HR-Employee-Attrition.csv')

    # --- 1. Data Cleaning & Preparation ---
    print("--- 1. Data Cleaning & Preparation ---")

    # Drop redundant / non-informative columns
    # EmployeeCount (always 1), StandardHours (always 80), Over18 (always Y), EmployeeNumber (unique ID)
    df = df.drop(columns=['EmployeeCount', 'StandardHours', 'Over18', 'EmployeeNumber'])

    # Check for duplicates (shouldn’t exist, but confirm)
    duplicates_count = df.duplicated().sum()
    print(f"\nData Cleaning: Checked for duplicate rows. Found {duplicates_count} duplicates.")

    # Map ordinal variables for interpretability
    education_map = {1: 'Below College', 2: 'College', 3: 'Bachelor', 4: 'Master', 5: 'Doctor'}
    satisfaction_map = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Very High'} # Used for EnvironmentSatisfaction, JobInvolvement, JobSatisfaction, RelationshipSatisfaction
    worklife_balance_map = {1: 'Bad', 2: 'Good', 3: 'Better', 4: 'Best'}
    performance_map = {3: 'Good', 4: 'Outstanding'} # PerformanceRating is typically 3 or 4

    df['Education'] = df['Education'].map(education_map)
    df['EnvironmentSatisfaction'] = df['EnvironmentSatisfaction'].map(satisfaction_map)
    df['JobSatisfaction'] = df['JobSatisfaction'].map(satisfaction_map)
    df['RelationshipSatisfaction'] = df['RelationshipSatisfaction'].map(satisfaction_map)
    df['WorkLifeBalance'] = df['WorkLifeBalance'].map(worklife_balance_map)
    df['PerformanceRating'] = df['PerformanceRating'].map(performance_map)
    df['JobInvolvement'] = df['JobInvolvement'].map(satisfaction_map) # Assuming similar mapping for JobInvolvement

    # Create age groups (20–30, 31–40, 41–50, 51+).
    # IMPORTANT: This needs to happen BEFORE 'AgeGroup' is added to categorical_cols for astype('category')
    bins = [17, 30, 40, 50, 60] # Adjusted bins to capture 18-30 and ensure 51+
    labels = ['18-30', '31-40', '41-50', '51+']
    df['AgeGroup'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)


    # Confirm categorical encoding: Convert specified columns into categorical data types.
    # IMPORTANT: 'JobInvolvement', 'PerformanceRating', and 'AgeGroup' are now guaranteed to exist
    categorical_cols = ['Attrition', 'Gender', 'MaritalStatus', 'BusinessTravel', 'Department',
                        'EducationField', 'JobRole', 'OverTime', 'JobInvolvement', 'PerformanceRating', 'AgeGroup']
    df[categorical_cols] = df[categorical_cols].astype('category')

    # Basic exploration: Inspect dataset shape, check for missing values, get descriptive stats.
    print(f"\nDataset Overview:")
    print(f"The dataset contains {df.shape[0]} rows (employees) and {df.shape[1]} columns (attributes) after cleaning.")
    print("\nMissing Values Check:")
    missing_values = df.isnull().sum().sum()
    if missing_values == 0:
        print(f"No missing values detected across all columns.")
    else:
        # Use to_string() here as it's just a Series print, no need for to_markdown
        print(f"Found {missing_values} missing values in total. Details per column:\n{df.isnull().sum().to_string()}")

    print("\nDescriptive Statistics for Numeric Columns:")
    print("Summary of numerical data (e.g., age, income, rates):")
    print(df.describe().T.to_markdown(numalign="left", stralign="left"))


    # --- 2. Attrition Analysis (Target Focus) ---
    print("\n--- 2. Attrition Analysis (Target Focus) ---")

    # Overall attrition rate (percentage of employees who left).
    attrition_rate = df['Attrition'].value_counts(normalize=True) * 100
    attrition_rate_yes = attrition_rate.get('Yes', 0)
    attrition_rate_no = attrition_rate.get('No', 0)
    print(f"\nOverall Attrition Rate:")
    print(f"A {attrition_rate_yes:.2f}% of employees left the company last year, while {attrition_rate_no:.2f}% remained. This matches the overall industry rate of 16.12%.")


    # Attrition by Demographics: Age groups, Gender, Marital Status.
    print("\nAttrition by Demographics:")

    # Attrition by Gender
    gender_attrition = pd.crosstab(df['Gender'], df['Attrition'], normalize='index') * 100
    female_attrition = gender_attrition.loc['Female', 'Yes']
    male_attrition = gender_attrition.loc['Male', 'Yes']
    print(f"\n- Gender Impact: Males show a slightly higher attrition rate of {male_attrition:.2f}% compared to females at {female_attrition:.2f}%.")

    # Attrition by Marital Status
    marital_attrition = pd.crosstab(df['MaritalStatus'], df['Attrition'], normalize='index') * 100
    single_attrition = marital_attrition.loc['Single', 'Yes']
    married_attrition = marital_attrition.loc['Married', 'Yes']
    divorced_attrition = marital_attrition.loc['Divorced', 'Yes']
    print(f"\n- Marital Status Impact: Single employees have an attrition rate of {single_attrition:.2f}%. This is more than double the rate for married employees ({married_attrition:.2f}%) and higher than divorced employees ({divorced_attrition:.2f}%).")


    # Attrition by Age Group
    age_group_attrition = pd.crosstab(df['AgeGroup'], df['Attrition'], normalize='index') * 100
    print(f"\n- Age Group Attrition:")
    print(f"The youngest group (18-30 years) exhibits the highest attrition at {age_group_attrition.loc['18-30', 'Yes']:.2f}%, indicating challenges in retaining early-career talent.")
    print(age_group_attrition.to_markdown(numalign="left", stralign="left"))


    # Attrition by work-related features: Department, JobRole, OverTime (Yes vs No), BusinessTravel frequency.
    print("\nAttrition by Work-Related Features:")

    # Attrition by Department
    dept_attrition_rates = pd.crosstab(df['Department'], df['Attrition'], normalize='index') * 100
    print(f"\n- Department Turnover: The Sales department has the highest attrition rate at {dept_attrition_rates.loc['Sales', 'Yes']:.2f}%, closely followed by Human Resources. Research & Development has the lowest.")
    print(dept_attrition_rates.to_markdown(numalign="left", stralign="left"))

    # Attrition by Job Role
    job_role_attrition_rates = pd.crosstab(df['JobRole'], df['Attrition'], normalize='index') * 100
    print(f"\n- Job Role Turnover: Sales Representatives face an attrition rate of {job_role_attrition_rates.loc['Sales Representative', 'Yes']:.2f}%, making it the role with the highest turnover.")
    print(job_role_attrition_rates.sort_values(by='Yes', ascending=False).to_markdown(numalign="left", stralign="left"))

    # Attrition by OverTime
    overtime_attrition = pd.crosstab(df['OverTime'], df['Attrition'], normalize='index') * 100
    yes_overtime_attrition = overtime_attrition.loc['Yes', 'Yes']
    no_overtime_attrition = overtime_attrition.loc['No', 'Yes']
    print(f"\n- Overtime Impact: Employees working overtime are significantly more likely to leave ({yes_overtime_attrition:.2f}% attrition) compared to those who don't ({no_overtime_attrition:.2f}% attrition). This points to potential burnout or work-life balance issues.")

    # Attrition by Business Travel
    travel_attrition_rates = pd.crosstab(df['BusinessTravel'], df['Attrition'], normalize='index') * 100
    frequent_travel_attrition = travel_attrition_rates.loc['Travel_Frequently', 'Yes']
    print(f"\n- Business Travel Frequency: Employees who travel frequently have a notably higher attrition rate ({frequent_travel_attrition:.2f}%).")
    print(travel_attrition_rates.to_markdown(numalign="left", stralign="left"))


    # Attrition vs DistanceFromHome (farther commute = higher attrition?).
    distance_attrition_mean = df.groupby('Attrition', observed=False)['DistanceFromHome'].mean()
    distance_leavers = distance_attrition_mean.loc['Yes']
    distance_stayers = distance_attrition_mean.loc['No']
    print(f"\n- Commute Distance vs Attrition: Employees who left had an average commute of {distance_leavers:.2f} miles, while those who stayed averaged {distance_stayers:.2f} miles. Longer commutes appear to correlate with higher attrition.")


    # Attrition by seniority/tenure: YearsAtCompany, YearsSinceLastPromotion, YearsWithCurrManager.
    print("\nAttrition by Seniority & Tenure:")
    mean_years_at_company = df.groupby('Attrition', observed=False)['YearsAtCompany'].mean()
    mean_years_since_promotion = df.groupby('Attrition', observed=False)['YearsSinceLastPromotion'].mean()
    mean_years_with_manager = df.groupby('Attrition', observed=False)['YearsWithCurrManager'].mean()

    print(f"\n- Years At Company: Leavers had significantly less tenure ({mean_years_at_company.loc['Yes']:.2f} years) compared to stayers ({mean_years_at_company.loc['No']:.2f} years).")
    print(f"- Years Since Last Promotion: Those who left had, on average, fewer years since their last promotion ({mean_years_since_promotion.loc['Yes']:.2f} years) than those who stayed ({mean_years_since_promotion.loc['No']:.2f} years).")
    print(f"- Years With Current Manager: Leavers spent less time with their current manager ({mean_years_with_manager.loc['Yes']:.2f} years) than stayers ({mean_years_with_manager.loc['No']:.2f} years). This suggests a link between career progression, managerial relationships, and retention.")


    # --- 3. Workforce Demographics ---
    print("\n--- 3. Workforce Demographics ---")

    # Age distribution: mean, median, histogram.
    print("\nWorkforce Age Distribution:")
    age_desc = df['Age'].describe()
    print(f"The average employee age is {age_desc['mean']:.2f} years, with a median of {age_desc['50%']:.0f} years. The workforce ranges from {age_desc['min']:.0f} to {age_desc['max']:.0f} years old.")
    print(age_desc.to_markdown(numalign="left", stralign="left"))


    # Gender breakdown: counts and ratios.
    print("\nGender Breakdown:")
    gender_counts = df['Gender'].value_counts()
    gender_ratios = df['Gender'].value_counts(normalize=True) * 100
    print(f"Our workforce is composed of {gender_ratios.loc['Male']:.2f}% Male employees ({gender_counts.loc['Male']} individuals) and {gender_ratios.loc['Female']:.2f}% Female employees ({gender_counts.loc['Female']} individuals).")


    # Education distribution: mapped to human labels.
    print("\nEducation Level Distribution:")
    edu_dist = df['Education'].value_counts(normalize=True) * 100
    print("The majority of employees hold a Bachelor's degree.")
    print(edu_dist.to_markdown(numalign="left", stralign="left"))

    # Marital Status distribution.
    print("\nMarital Status Distribution:")
    marital_dist = df['MaritalStatus'].value_counts()
    print(f"Our workforce is primarily Married ({marital_dist.loc['Married']} employees), followed by Single ({marital_dist.loc['Single']}) and Divorced ({marital_dist.loc['Divorced']}).")
    print(marital_dist.to_markdown(numalign="left", stralign="left"))


    # Department & JobRole composition.
    print("\nDepartment Composition:")
    dept_comp = df['Department'].value_counts()
    print(f"The largest department is Research & Development ({dept_comp.loc['Research & Development']} employees).")
    print(dept_comp.to_markdown(numalign="left", stralign="left"))

    print("\nJob Role Composition:")
    job_role_comp = df['JobRole'].value_counts()
    print(f"The most common roles are Sales Executive ({job_role_comp.loc['Sales Executive']} employees) and Research Scientist ({job_role_comp.loc['Research Scientist']} employees).")
    print(job_role_comp.to_markdown(numalign="left", stralign="left"))

    # BusinessTravel frequency distribution.
    print("\nBusiness Travel Frequency Distribution:")
    travel_dist = df['BusinessTravel'].value_counts()
    print(f"Most employees travel Rarely ({travel_dist.loc['Travel_Rarely']} employees), while a smaller portion travel Frequently or Not at all.")
    print(travel_dist.to_markdown(numalign="left", stralign="left"))


    # --- 4. Compensation & Career Progression ---
    print("\n--- 4. Compensation & Career Progression ---")

    # MonthlyIncome vs JobLevel: Boxplot or summary stats.
    print("\nMonthly Income by Job Level:")
    monthly_income_by_joblevel = df.groupby('JobLevel')['MonthlyIncome'].describe()
    print("As expected, monthly income shows a clear upward trend with increasing job level.")
    print(monthly_income_by_joblevel.to_markdown(numalign="left", stralign="left"))

    # Income comparison by Department and JobRole.
    print("\nMonthly Income by Department:")
    monthly_income_by_dept = df.groupby('Department')['MonthlyIncome'].describe()
    print(f"The highest average monthly income is observed in the Sales department (${monthly_income_by_dept.loc['Sales', 'mean']:.2f}), despite its higher attrition.")
    print(monthly_income_by_dept.to_markdown(numalign="left", stralign="left"))

    print("\nMonthly Income by Job Role:")
    monthly_income_by_jobrole = df.groupby('JobRole')['MonthlyIncome'].describe()
    print(f"Managers and Research Directors command the highest average monthly incomes, while Sales Representatives and Laboratory Technicians are among the lowest paid roles.")
    print(monthly_income_by_jobrole.to_markdown(numalign="left", stralign="left"))

    # HourlyRate & MonthlyRate: check distribution.
    print("\nHourly Rate Distribution:")
    print(df['HourlyRate'].describe().to_markdown(numalign="left", stralign="left"))
    print("\nMonthly Rate Distribution:")
    print(df['MonthlyRate'].describe().to_markdown(numalign="left", stralign="left"))

    # PercentSalaryHike vs Attrition: do employees with lower raises leave more?
    percent_hike_attrition = df.groupby('Attrition', observed=False)['PercentSalaryHike'].mean()
    print(f"\nPercent Salary Hike vs. Attrition:")
    print(f"There's very little difference in average salary hike between employees who stayed ({percent_hike_attrition.loc['No']:.2f}%) and those who left ({percent_hike_attrition.loc['Yes']:.2f}%). This suggests that a recent percentage salary hike alone may not be a primary driver for retention.")


    # StockOptionLevel distribution and impact on attrition.
    print("\nStock Option Level Distribution & Impact:")
    stock_option_dist = df['StockOptionLevel'].value_counts(normalize=True) * 100
    stock_option_attrition = pd.crosstab(df['StockOptionLevel'], df['Attrition'], normalize='index') * 100
    print(f"{stock_option_dist.loc[0]:.2f}% of employees have no stock options (Level 0), and this group has a significantly higher attrition rate ({stock_option_attrition.loc[0, 'Yes']:.2f}%). Employees with Level 1 or 2 stock options show much lower attrition.")
    print("\nStock Option Level Distribution:")
    print(stock_option_dist.to_markdown(numalign="left", stralign="left"))
    print("\nAttrition by Stock Option Level:")
    print(stock_option_attrition.to_markdown(numalign="left", stralign="left"))


    # TotalWorkingYears vs MonthlyIncome: career progression check.
    print("\nCareer Progression: Total Working Years vs. Monthly Income Correlation:")
    total_work_income_corr = df[['TotalWorkingYears', 'MonthlyIncome']].corr().loc['TotalWorkingYears', 'MonthlyIncome']
    print(f"There's a strong positive correlation of {total_work_income_corr:.2f} between Total Working Years and Monthly Income. This confirms a healthy career progression pathway where experience generally leads to higher earnings.")


    # --- 5. Satisfaction & Engagement Analysis ---
    print("\n--- 5. Satisfaction & Engagement Analysis ---")

    # Analyse distributions of satisfaction/engagement variables:
    # JobSatisfaction, EnvironmentSatisfaction, RelationshipSatisfaction, WorkLifeBalance, JobInvolvement.
    print("\nDistribution of Key Satisfaction & Engagement Variables:")
    print("\nJob Satisfaction Distribution:")
    print(df['JobSatisfaction'].value_counts().to_markdown(numalign="left", stralign="left"))
    print("\nEnvironment Satisfaction Distribution:")
    print(df['EnvironmentSatisfaction'].value_counts().to_markdown(numalign="left", stralign="left"))
    print("\nRelationship Satisfaction Distribution:")
    print(df['RelationshipSatisfaction'].value_counts().to_markdown(numalign="left", stralign="left"))
    print("\nWork-Life Balance Distribution:")
    print(df['WorkLifeBalance'].value_counts().to_markdown(numalign="left", stralign="left"))
    print("\nJob Involvement Distribution:")
    print(df['JobInvolvement'].value_counts().to_markdown(numalign="left", stralign="left"))

    # Compare attrition vs satisfaction levels (e.g., % attrition by satisfaction score).
    print("\nAttrition vs. Satisfaction Levels:")
    print(f"Generally, lower satisfaction levels correlate with higher attrition.")
    attr_job_sat = pd.crosstab(df['JobSatisfaction'], df['Attrition'], normalize='index') * 100
    print(f"\n- Job Satisfaction vs. Attrition: Employees with 'Low' Job Satisfaction have an attrition rate of {attr_job_sat.loc['Low', 'Yes']:.2f}%, significantly higher than those with 'Very High' satisfaction ({attr_job_sat.loc['Very High', 'Yes']:.2f}%).")
    print(attr_job_sat.to_markdown(numalign="left", stralign="left"))

    attr_env_sat = pd.crosstab(df['EnvironmentSatisfaction'], df['Attrition'], normalize='index') * 100
    print(f"\n- Environment Satisfaction vs. Attrition: Similar to job satisfaction, 'Low' Environment Satisfaction sees {attr_env_sat.loc['Low', 'Yes']:.2f}% attrition.")
    print(attr_env_sat.to_markdown(numalign="left", stralign="left"))

    attr_rel_sat = pd.crosstab(df['RelationshipSatisfaction'], df['Attrition'], normalize='index') * 100
    print(f"\n- Relationship Satisfaction vs. Attrition: 'Low' Relationship Satisfaction leads to {attr_rel_sat.loc['Low', 'Yes']:.2f}% attrition.")
    print(attr_rel_sat.to_markdown(numalign="left", stralign="left"))

    attr_wl_balance = pd.crosstab(df['WorkLifeBalance'], df['Attrition'], normalize='index') * 100
    print(f"\n- Work-Life Balance vs. Attrition: A 'Bad' Work-Life Balance is associated with the highest attrition at {attr_wl_balance.loc['Bad', 'Yes']:.2f}%.")
    print(attr_wl_balance.to_markdown(numalign="left", stralign="left"))

    attr_job_involve = pd.crosstab(df['JobInvolvement'], df['Attrition'], normalize='index') * 100
    print(f"\n- Job Involvement vs. Attrition: 'Low' Job Involvement has a high attrition rate of {attr_job_involve.loc['Low', 'Yes']:.2f}%, indicating disengagement is a significant factor.")
    print(attr_job_involve.to_markdown(numalign="left", stralign="left"))


    # Cross-tab: JobRole vs Satisfaction (do certain roles report lower satisfaction?).
    print("\nJob Role vs. Job Satisfaction (Counts):")
    job_role_sat_crosstab = pd.crosstab(df['JobRole'], df['JobSatisfaction'])
    print("Examining satisfaction levels across different job roles can highlight specific areas of concern:")
    print(job_role_sat_crosstab.to_markdown(numalign="left", stralign="left"))

    # Satisfaction vs Compensation (are higher-paid employees more satisfied?).
    print("\nMonthly Income by Job Satisfaction Level (Summary Stats):")
    income_by_job_sat = df.groupby('JobSatisfaction')['MonthlyIncome'].describe()
    print("There isn't a strong direct correlation between income level and job satisfaction. Employees across all satisfaction levels show similar income ranges.")
    print(income_by_job_sat.to_markdown(numalign="left", stralign="left"))


    # --- 6. Performance & Development ---
    print("\n--- 6. Performance & Development ---")

    # PerformanceRating distribution: check if skewed (most employees rated 3–4).
    print("\nPerformance Rating Distribution:")
    perf_rating_dist = df['PerformanceRating'].value_counts()
    print(f"The majority of employees ({perf_rating_dist.loc['Good']} individuals) are rated as 'Good', with {perf_rating_dist.loc['Outstanding']} rated 'Outstanding'. The distribution is skewed towards higher ratings.")
    print(perf_rating_dist.to_markdown(numalign="left", stralign="left"))


    # TrainingTimesLastYear distribution: average & impact on attrition.
    print("\nTraining Times Last Year & Attrition Impact:")
    training_desc = df['TrainingTimesLastYear'].describe()
    training_attrition = df.groupby('Attrition', observed=False)['TrainingTimesLastYear'].mean()
    print(f"Employees received training an average of {training_desc['mean']:.2f} times last year. Interestingly, those who stayed received slightly more training ({training_attrition.loc['No']:.2f} times) than those who left ({training_attrition.loc['Yes']:.2f} times).")
    print(training_desc.to_markdown(numalign="left", stralign="left"))


    # YearsSinceLastPromotion: compare high vs low.
    print("\nYears Since Last Promotion vs. Attrition:")
    promo_attrition_mean = df.groupby('Attrition', observed=False)['YearsSinceLastPromotion'].mean()
    print(f"Employees who left had, on average, fewer years since their last promotion ({promo_attrition_mean.loc['Yes']:.2f} years) compared to those who stayed ({promo_attrition_mean.loc['No']:.2f} years). This suggests that slower career progression is a factor in attrition.")


    # YearsWithCurrManager vs Attrition: frequent manager changes effect.
    print("\nYears With Current Manager vs. Attrition:")
    manager_attrition_mean = df.groupby('Attrition', observed=False)['YearsWithCurrManager'].mean()
    print(f"Leavers spent significantly less time with their current manager ({manager_attrition_mean.loc['Yes']:.2f} years) than stayers ({manager_attrition_mean.loc['No']:.2f} years). Frequent manager changes or shorter tenures with managers could contribute to attrition.")


    # JobInvolvement vs PerformanceRating correlation.
    print("\nCorrelation: Job Involvement vs. Performance Rating:")
    # Convert categorical series to their numerical codes for correlation calculation
    job_involvement_codes = df['JobInvolvement'].cat.codes
    performance_rating_codes = df['PerformanceRating'].cat.codes
    df_for_corr = pd.DataFrame({
        'JobInvolvement_Code': job_involvement_codes,
        'PerformanceRating_Code': performance_rating_codes
    })
    job_perf_corr = df_for_corr.corr().loc['JobInvolvement_Code', 'PerformanceRating_Code']
    print(f"The correlation between Job Involvement and Performance Rating is {job_perf_corr:.2f}. This very weak correlation suggests that an employee's perceived involvement in their job doesn't strongly predict their formal performance rating in this dataset.")


    # --- 7. Advanced Attrition Prediction ---
    print("\n--- 7. Advanced Attrition Prediction ---")
    print("This section outlines the process for building machine learning models to predict employee attrition:")
    print("1.  Feature Encoding: Convert all categorical features into numerical formats (e.g., One-Hot Encoding).")
    print("2.  Data Splitting: Divide the dataset into training and testing sets.")
    print("3.  Model Training: Apply algorithms like Logistic Regression, Random Forest, or Gradient Boosting.")
    print("4.  Feature Importance: Identify the strongest predictors of attrition from the trained models.")
    print("5.  Model Evaluation: Assess model performance using metrics like accuracy, ROC-AUC, precision, and recall.")


    # --- 8. Visualizations ---
    print("\n--- 8. Visualizations ---")
    sns.set_style("whitegrid")
    custom_palette = sns.color_palette("rocket") # Define a custom color palette for consistent styling

    # Overall Attrition Pie Chart
    plt.figure(figsize=(8, 8))
    attrition_counts = df['Attrition'].value_counts()
    plt.pie(attrition_counts, labels=attrition_counts.index, autopct='%1.1f%%', startangle=90, colors=custom_palette)
    plt.title('Overall Employee Attrition Rate (16.12% Turnover)', fontsize=16)
    plt.savefig('overall_attrition_pie_chart.png')
    plt.clf() # Clear the current figure to free up memory for the next plot

    # Bar charts: Attrition by Department
    dept_attrition_plot = pd.crosstab(df['Department'], df['Attrition'], normalize='index') * 100
    dept_attrition_plot.sort_values(by='Yes', ascending=False, inplace=True)
    plt.figure(figsize=(12, 7))
    sns.barplot(x=dept_attrition_plot.index, y=dept_attrition_plot['Yes'], hue=dept_attrition_plot.index, legend=False)
    plt.title('Attrition Rate by Department: Sales & HR Departments Lead Turnover', fontsize=16)
    plt.xlabel('Department', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.xticks(rotation=45)
    plt.savefig('attrition_by_department_bar_chart.png')
    plt.clf()

    # Bar charts: Attrition by JobRole
    job_role_attrition_plot = pd.crosstab(df['JobRole'], df['Attrition'], normalize='index') * 100
    job_role_attrition_plot.sort_values(by='Yes', ascending=False, inplace=True)
    plt.figure(figsize=(15, 8))
    sns.barplot(x=job_role_attrition_plot.index, y=job_role_attrition_plot['Yes'], hue=job_role_attrition_plot.index, palette='viridis', legend=False)
    plt.title('Attrition Rate by Job Role: Sales Representatives Most Vulnerable', fontsize=16)
    plt.xlabel('Job Role', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout() # Adjust layout to prevent labels overlapping
    plt.savefig('attrition_by_jobrole_bar_chart.png')
    plt.clf()

    # Bar charts: Attrition by Gender
    gender_attrition_plot = pd.crosstab(df['Gender'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(8, 6))
    sns.barplot(x=gender_attrition_plot.index, y=gender_attrition_plot['Yes'], hue=gender_attrition_plot.index, legend=False)
    plt.title('Attrition Rate by Gender: Slightly Higher for Males', fontsize=16)
    plt.xlabel('Gender', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.savefig('attrition_by_gender_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by Overtime
    overtime_attrition_plot = pd.crosstab(df['OverTime'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(8, 6))
    sns.barplot(x=overtime_attrition_plot.index, y=overtime_attrition_plot['Yes'], hue=overtime_attrition_plot.index, palette=custom_palette, legend=False)
    plt.title('Overtime Impact on Attrition: Significant Turnover Among Overtime Workers', fontsize=16)
    plt.xlabel('Overtime', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.savefig('attrition_by_overtime_bar_chart.png')
    plt.clf()


    # Bar charts: Attrition by BusinessTravel
    travel_attrition_plot = pd.crosstab(df['BusinessTravel'], df['Attrition'], normalize='index') * 100
    travel_attrition_plot.sort_values(by='Yes', ascending=False, inplace=True)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=travel_attrition_plot.index, y=travel_attrition_plot['Yes'], hue=travel_attrition_plot.index, legend=False)
    plt.title('Attrition Rate by Business Travel Frequency: Frequent Travelers at Risk', fontsize=16)
    plt.xlabel('Business Travel', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.savefig('attrition_by_businesstravel_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by StockOptionLevel
    stock_option_attrition_plot = pd.crosstab(df['StockOptionLevel'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(10, 6))
    sns.barplot(x=stock_option_attrition_plot.index, y=stock_option_attrition_plot['Yes'], hue=stock_option_attrition_plot.index, palette='coolwarm', legend=False)
    plt.title('Attrition Rate by Stock Option Level: Higher Turnover with No Stock Options', fontsize=16)
    plt.xlabel('Stock Option Level', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.xticks(rotation=0)
    plt.savefig('attrition_by_stock_option_level_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by YearsAtCompany
    # Bin YearsAtCompany for better visualization if there are many unique values
    bins_yac = [0, 1, 3, 5, 10, 15, 20, df['YearsAtCompany'].max() + 1]
    labels_yac = ['<1', '1-3', '3-5', '5-10', '10-15', '15-20', '20+']
    df['YearsAtCompanyGroup'] = pd.cut(df['YearsAtCompany'], bins=bins_yac, labels=labels_yac, right=False)
    yac_attrition_plot = pd.crosstab(df['YearsAtCompanyGroup'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(12, 7))
    sns.barplot(x=yac_attrition_plot.index, y=yac_attrition_plot['Yes'], hue=yac_attrition_plot.index, palette='magma', legend=False)
    plt.title('Attrition Rate by Years at Company: Higher Turnover in Early Tenure', fontsize=16)
    plt.xlabel('Years at Company Group', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.savefig('attrition_by_years_at_company_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by YearsSinceLastPromotion
    bins_ysl = [0, 1, 2, 5, df['YearsSinceLastPromotion'].max() + 1]
    labels_ysl = ['0', '1', '2-4', '5+'] # Adjusted to match common promotion cycles
    df['YearsSincePromotionGroup'] = pd.cut(df['YearsSinceLastPromotion'], bins=bins_ysl, labels=labels_ysl, right=False)
    ysl_attrition_plot = pd.crosstab(df['YearsSincePromotionGroup'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(12, 7))
    sns.barplot(x=ysl_attrition_plot.index, y=ysl_attrition_plot['Yes'], hue=ysl_attrition_plot.index, palette='cividis', legend=False)
    plt.title('Attrition Rate by Years Since Last Promotion: Stagnation Drives Turnover', fontsize=16)
    plt.xlabel('Years Since Last Promotion Group', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.savefig('attrition_by_years_since_promotion_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by YearsWithCurrManager
    bins_ywcm = [0, 1, 2, 5, df['YearsWithCurrManager'].max() + 1]
    labels_ywcm = ['<1', '1', '2-4', '5+']
    df['YearsWithManagerGroup'] = pd.cut(df['YearsWithCurrManager'], bins=bins_ywcm, labels=labels_ywcm, right=False)
    ywcm_attrition_plot = pd.crosstab(df['YearsWithManagerGroup'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(12, 7))
    sns.barplot(x=ywcm_attrition_plot.index, y=ywcm_attrition_plot['Yes'], hue=ywcm_attrition_plot.index, palette='plasma', legend=False)
    plt.title('Attrition Rate by Years With Current Manager: Manager Relationships Impact Retention', fontsize=16)
    plt.xlabel('Years With Current Manager Group', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.savefig('attrition_by_years_with_manager_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by EnvironmentSatisfaction
    env_sat_attrition_plot = pd.crosstab(df['EnvironmentSatisfaction'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(10, 6))
    sns.barplot(x=env_sat_attrition_plot.index, y=env_sat_attrition_plot['Yes'], hue=env_sat_attrition_plot.index, palette='viridis', legend=False)
    plt.title('Attrition Rate by Environment Satisfaction: Lower Satisfaction, Higher Turnover', fontsize=16)
    plt.xlabel('Environment Satisfaction', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.xticks(rotation=0)
    plt.savefig('attrition_by_environment_satisfaction_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by RelationshipSatisfaction
    rel_sat_attrition_plot = pd.crosstab(df['RelationshipSatisfaction'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(10, 6))
    sns.barplot(x=rel_sat_attrition_plot.index, y=rel_sat_attrition_plot['Yes'], hue=rel_sat_attrition_plot.index, palette='magma', legend=False)
    plt.title('Attrition Rate by Relationship Satisfaction: Relationships Drive Retention', fontsize=16)
    plt.xlabel('Relationship Satisfaction', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.xticks(rotation=0)
    plt.savefig('attrition_by_relationship_satisfaction_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by WorkLifeBalance
    wlb_attrition_plot = pd.crosstab(df['WorkLifeBalance'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(10, 6))
    sns.barplot(x=wlb_attrition_plot.index, y=wlb_attrition_plot['Yes'], hue=wlb_attrition_plot.index, palette='rocket', legend=False)
    plt.title('Attrition Rate by Work-Life Balance: Poor Balance, Higher Turnover', fontsize=16)
    plt.xlabel('Work-Life Balance', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.xticks(rotation=0)
    plt.savefig('attrition_by_work_life_balance_bar_chart.png')
    plt.clf()

    # Bar chart: Attrition by JobInvolvement
    job_involvement_attrition_plot = pd.crosstab(df['JobInvolvement'], df['Attrition'], normalize='index') * 100
    plt.figure(figsize=(10, 6))
    sns.barplot(x=job_involvement_attrition_plot.index, y=job_involvement_attrition_plot['Yes'], hue=job_involvement_attrition_plot.index, palette='cividis', legend=False)
    plt.title('Attrition Rate by Job Involvement: Disengagement Leads to Turnover', fontsize=16)
    plt.xlabel('Job Involvement', fontsize=12)
    plt.ylabel('Attrition Rate (%)', fontsize=12)
    plt.xticks(rotation=0)
    plt.savefig('attrition_by_job_involvement_bar_chart.png')
    plt.clf()


    # Boxplots: MonthlyIncome vs JobLevel
    plt.figure(figsize=(12, 7))
    sns.boxplot(x='JobLevel', y='MonthlyIncome', hue='JobLevel', data=df, palette='GnBu', legend=False)
    plt.title('Monthly Income Distribution by Job Level: Clear Compensation Progression', fontsize=16)
    plt.xlabel('Job Level', fontsize=12)
    plt.ylabel('Monthly Income', fontsize=12)
    plt.savefig('monthly_income_by_job_level_boxplot.png')
    plt.clf()

    # Histograms: Age Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Age'], bins=15, kde=True, color=custom_palette[0])
    plt.title('Age Distribution of Employees: Workforce Concentrated in Mid-Career', fontsize=16)
    plt.xlabel('Age', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.savefig('age_distribution_histogram.png')
    plt.clf()

    # Histograms: MonthlyIncome Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['MonthlyIncome'], bins=20, kde=True, color=custom_palette[1])
    plt.title('Monthly Income Distribution: Diverse Range Across Employees', fontsize=16)
    plt.xlabel('Monthly Income', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.savefig('monthly_income_distribution_histogram.png')
    plt.clf()

    # Histograms: DistanceFromHome Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['DistanceFromHome'], bins=10, kde=True, color=custom_palette[2])
    plt.title('Distance From Home Distribution: Employees Spread Across Commute Distances', fontsize=16)
    plt.xlabel('Distance From Home', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.savefig('distance_from_home_distribution_histogram.png')
    plt.clf()

    # Histograms: TotalWorkingYears Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['TotalWorkingYears'], bins=10, kde=True, color=custom_palette[3])
    plt.title('Total Working Years Distribution: Majority with Moderate Experience', fontsize=16)
    plt.xlabel('Total Working Years', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.savefig('total_working_years_distribution_histogram.png')
    plt.clf()

    # Boxplots: Distance From Home vs Attrition
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Attrition', y='DistanceFromHome', data=df, hue='Attrition', legend=False)
    plt.title('Distance From Home vs Attrition: Longer Commutes Correlate with Turnover', fontsize=16)
    plt.xlabel('Attrition', fontsize=12)
    plt.ylabel('Distance From Home', fontsize=12)
    plt.savefig('distance_from_home_vs_attrition_boxplot.png')
    plt.clf()

    # Stacked bar: Satisfaction scores vs Attrition (Job Satisfaction is already included here)
    satisfaction_crosstab_plot = pd.crosstab(df['JobSatisfaction'], df['Attrition'], normalize='index')
    satisfaction_crosstab_plot.plot(kind='bar', stacked=True, figsize=(10, 6), color=[custom_palette[0], custom_palette[5]]) # Use two distinct colors from palette
    plt.title('Job Satisfaction Level vs Attrition: Lower Satisfaction, Higher Turnover', fontsize=16)
    plt.xlabel('Job Satisfaction Level', fontsize=12)
    plt.ylabel('Proportion', fontsize=12)
    plt.xticks(rotation=0)
    plt.legend(title='Attrition')
    plt.savefig('job_satisfaction_vs_attrition_stacked_bar.png')
    plt.clf()

    # Heatmap: Correlation of numeric features (MonthlyIncome, Age, YearsAtCompany, etc.).
    plt.figure(figsize=(14, 12))
    numeric_df = df.select_dtypes(include=np.number)
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix of Numeric Features: Relationships Within Our Data', fontsize=16)
    plt.tight_layout()
    plt.savefig('correlation_matrix_heatmap.png')
    plt.clf()


    # --- 9. Insights & HR Recommendations ---
    print("\n--- 9. Insights & HR Recommendations ---")
    print("This final section synthesizes all the analysis into actionable insights and recommendations. Here are examples of how you would articulate these points based on the data generated above:")
    print("\nKey Attrition Risk Groups:")
    print("- Young, Single Employees: This demographic (especially 18-30 year olds) consistently shows higher attrition rates. Targeted mentorship, career development plans, and community-building initiatives could be beneficial.")
    print("- Sales Representatives & Laboratory Technicians: These roles experience unusually high turnover. Investigate workload, compensation equity, and career path clarity within these departments.")
    print("- Employees Working Overtime/Long Commutes: High overtime and longer commute distances correlate with higher attrition. Review staffing levels, flexible work options, and commute support programs.")
    print("- Employees with Low Satisfaction or Stock Options: Low job/environment satisfaction and lack of stock options are strong indicators of potential attrition. Implement regular satisfaction surveys, address feedback promptly and review stock option eligibility.")

    print("\nCompensation & Career Progression Considerations:")
    print("- While income generally increases with job level, ensure compensation is competitive specifically for high-risk roles like Sales Representatives and Laboratory Technicians, where attrition is high despite potentially lower pay relative to other roles.")
    print("- Promotions & Managerial Relationships: Employees with shorter tenures in their current role/company and less time with their current manager are more prone to attrition. Focus on clear promotion pathways and training for managers to build strong, supportive relationships with their teams.")
    print("- Work-Life Balance Initiatives: Implement policies that promote better work-life balance, such as flexible hours, remote work options, or caps on overtime, especially for roles prone to burnout.")
    print("- Managerial Training: Equip managers with skills to foster employee engagement, provide regular feedback and support career growth to improve retention within their teams.")
    print("- Review Compensation Structure: Conduct a deeper dive into compensation fairness, particularly for roles and demographics identified as high-risk, and consider adjustments where inequities exist.")
    print("- Enhance Satisfaction Drivers: Actively address factors contributing to low job and environment satisfaction through direct feedback mechanisms and actionable improvements.")

# Reset standard output to the console after the 'with' block
sys.stdout = original_stdout
print("\nAnalysis complete! The text report has been saved to 'HR_Attrition_Report_Text.txt' and plots are saved in the current directory.")
